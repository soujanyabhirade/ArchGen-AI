"""
Health check endpoint.

Why this file exists:
Every real backend needs a way to answer "are you alive and responding?" without
touching any business logic. This is used by:
  - You, manually, to confirm the server started correctly.
  - Later: Docker healthchecks, load balancers, uptime monitors.

It deliberately does nothing else - no DB check, no AI check - because right now
neither of those exist yet. This endpoint should stay trivial forever; it's not
the place for "is Gemini reachable" logic (that would be a separate readiness
check, if we ever need one).
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
