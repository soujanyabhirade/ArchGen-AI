"""
Application entrypoint.

Why this file exists:
This is where the FastAPI `app` object is created and assembled - it's the
"wiring" layer. It should stay thin: register routers, register middleware,
read settings. It should NOT contain route logic or business logic itself
(that belongs in api/routes/ and services/ respectively).

Why CORS middleware is here already, even though there's no frontend yet:
the frontend (Phase 0, Task 2) will run on a different port than the backend,
which means every request from it is a cross-origin request by default. Adding
CORS now, driven by settings.ALLOWED_ORIGINS, means Task 2 isn't blocked on a
"why is my fetch() failing" CORS debugging detour.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generation, health
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(generation.router)
