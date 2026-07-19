"""
Architecture generation service (placeholder).

Why this file exists:
This is where the real work will happen starting in Phase 1: building the prompt,
calling Gemini, validating the structured JSON it returns, and shaping it into
the response schema. It does NOT belong in the route file (app/api/routes/generation.py)
because:
  - Routes handle HTTP (status codes, request parsing).
  - Services handle business logic (what "generating an architecture" actually means).
  - This separation means we can unit-test this function directly, with no HTTP
    layer involved, and later swap/mock the Gemini call without touching routes.

For THIS task, the function does the simplest possible thing that satisfies the
contract: it returns a canned response using the idea the user submitted, so we
can prove the full request -> validation -> service -> response path works.
"""

from app.schemas.generation import GenerationResponse


def generate_architecture_placeholder(idea: str) -> GenerationResponse:
    return GenerationResponse(
        idea=idea,
        status="not_implemented",
        message=(
            f"Received idea '{idea}'. Architecture generation logic "
            "will be implemented in Phase 1."
        ),
    )
