"""
Request/response schemas for the generation endpoint.

Why this file exists:
FastAPI uses Pydantic models to validate incoming requests and to define/document
the shape of responses (this is also what powers the auto-generated /docs page).

We keep schemas in their own module, separate from route handlers, because:
  - The same schema often gets reused across multiple routes (e.g. generate + retrieve).
  - It keeps route files focused on HTTP concerns (status codes, routing) rather than
    data-shape concerns.
  - In Phase 1, this is where the full architecture output schema (services, DBs,
    endpoints, roadmap, etc.) will live and grow. Starting it now, even as a stub,
    means the shape is already isolated in the right place.

For this task, we only define the MINIMUM needed for a placeholder endpoint:
what a request looks like, and a trivial acknowledgment response. No AI-shaped
fields yet - those arrive in Phase 1 once the Gemini schema is actually designed.
"""

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    idea: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="A short product idea, e.g. 'Food Delivery App'",
    )


class GenerationResponse(BaseModel):
    idea: str
    status: str
    message: str
