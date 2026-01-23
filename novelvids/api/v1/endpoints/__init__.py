"""V1 API endpoints."""

from novelvids.api.v1.endpoints.auth import router as auth_router
from novelvids.api.v1.endpoints.chapters import router as chapters_router
from novelvids.api.v1.endpoints.characters import router as characters_router
from novelvids.api.v1.endpoints.chapter_processing import router as chapter_processing_router
from novelvids.api.v1.endpoints.dashboard import router as dashboard_router
from novelvids.api.v1.endpoints.generation import router as generation_router
from novelvids.api.v1.endpoints.novels import router as novels_router


__all__ = [
    "auth_router",
    "novels_router",
    "chapters_router",
    "characters_router",
    "chapter_processing_router",
    "generation_router",
    "dashboard_router",
]
