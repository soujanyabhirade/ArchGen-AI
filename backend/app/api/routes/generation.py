"""
Generation endpoint (placeholder).

Why this file exists:
This is the route that will eventually trigger the full AI architecture-generation
pipeline (Phase 1). For THIS task, it does no AI work at all - it just accepts
a validated idea string and echoes back a canned response.

Why build a placeholder instead of waiting until Phase 1 to create this route?
Because it lets us validate the full request/response contract (URL, method,
request schema, response schema, status codes) right now, independent of the
much harder problem of AI integration. When Phase 1 arrives, we swap the inside
of this function for a call to the generation service - the route signature,
validation, and error-handling shape don't need to change.

Note the route handler has no business logic in it beyond calling into a
service function. That's intentional: routes should stay thin and only handle
HTTP concerns. The actual "what happens when you generate" logic lives in
app/services/, even in placeholder form.
"""

from fastapi import APIRouter

from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.architecture_generator import generate_architecture_placeholder

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse, tags=["generation"])
def generate(request: GenerationRequest) -> GenerationResponse:
    return generate_architecture_placeholder(request.idea)
