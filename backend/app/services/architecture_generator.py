"""
Architecture generation service.

Why this file exists:
This is where "generating an architecture" actually happens - kept out of the
route file (app/api/routes/generation.py) so routes stay focused on HTTP
concerns and this logic stays independently testable/swappable.

Phase 2 change: Gemini is now prompted to act as a senior software architect
and return a full structured architecture (matching ArchitectureData in
schemas/generation.py) instead of plain text. Two layers work together to
make the output reliable:
  1. response_schema (passed to the Gemini API call) constrains the model's
     decoding so it's strongly biased toward emitting valid JSON matching
     our shape.
  2. Explicit json.loads() + Pydantic validation, done ourselves after the
     call returns.
Layer 1 alone is not sufficient to trust blindly: content can still be
truncated (token limits), blocked by safety filters, or occasionally
malformed. Layer 2 is what turns "Gemini probably returned good JSON" into
"we have verified this JSON is actually valid before it leaves this service."

Note: the function is still named generate_architecture_placeholder even
though it's no longer a placeholder. Left as-is because app/api/routes/generation.py
imports it by this exact name, and that file is explicitly out of scope for
this change. Worth renaming in a later cleanup pass.
"""

import json
import logging

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.generation import ArchitectureData, GenerationResponse

logger = logging.getLogger(__name__)

_MODEL_NAME = "models/gemini-3.1-flash-lite"

# The persona + instructions Gemini is given on every request. Kept as a
# module-level constant (not rebuilt per-call) since it's static text - only
# the user's idea changes between requests, not these instructions.
#
# Why the instructions repeat "return only JSON" even though response_schema
# already constrains the output: response_schema controls decoding shape, but
# it doesn't stop the model from, say, adding an explanatory sentence before
# the JSON if the prompt doesn't explicitly forbid it in some edge cases.
# Belt-and-suspenders: tell it AND constrain it.
_SYSTEM_INSTRUCTION = """\

You are a Senior Software Architect with expertise in designing scalable,
secure, production-ready distributed systems.

Your task is to generate a COMPLETE microservice architecture for the given
product idea.

IMPORTANT RULES:

- Return ONLY valid JSON.
- Do NOT return markdown.
- Do NOT wrap JSON inside code blocks.
- Do NOT add explanations.
- The JSON MUST exactly match the provided response schema.

Architecture Requirements:

1. Always include an API Gateway as one of the microservices.
   - Set api_gateway=true only for that service.
   - Every other service must have api_gateway=false.

2. Generate between 5 and 8 microservices.

3. Every microservice MUST contain:
   - name
   - responsibility
   - language
   - framework
   - api_gateway

4. Recommend the most appropriate database for every service.
   Examples:
   - PostgreSQL
   - MySQL
   - MongoDB
   - Redis
   - Elasticsearch

Include a short justification.

5. Define communication between services.

Use:
- REST for synchronous communication.
- event-driven for asynchronous communication.

If communication is event-driven,
include the broker.

Possible brokers:
- Kafka
- RabbitMQ
- Google Pub/Sub
- AWS SQS

6. Every microservice MUST expose at least one REST API endpoint.

Each endpoint must include:
- method
- path
- description

7. Generate a technology_stack object containing:

- frontend
- backend
- database
- message_broker
- api_gateway
- deployment

Use realistic technologies.

Example:
Frontend → React
Backend → FastAPI
Deployment → Kubernetes

8. Add practical deployment_notes.

Mention:
- Docker
- Kubernetes
- Scaling
- Load balancing
- Monitoring
- CI/CD

9. Generate an architecture_score.

Score from 1 to 10:

- scalability
- security
- maintainability
- cost_efficiency

10. The architecture should follow industry best practices,
be production-ready,
and be logically consistent.

Return ONLY valid JSON.
"""

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    # Lazy, cached client construction - see Phase 1 notes: building this at
    # import time would crash the whole app on startup if the API key isn't
    # configured yet, instead of failing only the requests that need it.
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def generate_architecture_placeholder(idea: str) -> GenerationResponse:
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set; cannot call Gemini.")
        return GenerationResponse(
            idea=idea,
            status="error",
            message="Server misconfiguration: GEMINI_API_KEY is not set.",
        )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=_MODEL_NAME,
            contents=idea,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_INSTRUCTION,
                # response_mime_type + response_schema together tell Gemini's
                # API to constrain decoding toward valid JSON matching this
                # exact Pydantic model - this is what "schema-constrained
                # output" (mentioned back in the architecture plan) means in
                # practice, and it's what replaces "hope the model formats
                # it correctly" with an actual API-level constraint.
                response_mime_type="application/json",
                response_schema=ArchitectureData,
            ),
        )
    except APIError as exc:
        logger.error("Gemini API error for idea=%r: %s", idea, exc)
        return GenerationResponse(
            idea=idea,
            status="error",
            message=f"Gemini API error: {exc}",
        )
    except Exception as exc:
        logger.exception("Unexpected error calling Gemini for idea=%r", idea)
        return GenerationResponse(
            idea=idea,
            status="error",
            message="Unexpected error while contacting Gemini.",
        )

    raw_text = response.text
    if not raw_text:
        logger.warning("Gemini returned an empty response for idea=%r", idea)
        return GenerationResponse(
            idea=idea,
            status="error",
            message="Gemini returned an empty response.",
        )

    # Layer 2, step 1: is this even syntactically valid JSON at all?
    # This can fail despite response_schema if, e.g., the response was
    # truncated mid-object due to hitting a token limit.
    try:
        parsed_json = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Gemini returned invalid JSON for idea=%r: %s", idea, exc)
        return GenerationResponse(
            idea=idea,
            status="error",
            message="Gemini returned invalid JSON.",
        )

    # Layer 2, step 2: is this JSON actually shaped like ArchitectureData?
    # response_schema makes this failure unlikely but not impossible - e.g.
    # the model could omit a required field or return a wrong-typed value.
    # This is the check that guarantees the caller either gets a fully valid
    # ArchitectureData object, or a clear error - never a half-shaped object
    # that breaks something downstream (like the React Flow diagram) later.
    try:
        architecture = ArchitectureData.model_validate(parsed_json)
    except ValidationError as exc:
        logger.error(
            "Gemini's JSON failed schema validation for idea=%r: %s", idea, exc
        )
        return GenerationResponse(
            idea=idea,
            status="error",
            message=f"Gemini's response did not match the required schema: {exc}",
        )

    return GenerationResponse(
        idea=idea,
        status="success",
        message=f"Architecture generated for '{idea}'.",
        architecture=architecture,
    )