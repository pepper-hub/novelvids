"""V1 API router."""

from fastapi import APIRouter

from novelvids.api.v1.endpoints import (
    auth_router,
    chapters_router,
    characters_router,
    chapter_processing_router,
    dashboard_router,
    generation_router,
    novels_router,
)

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(novels_router)
router.include_router(chapters_router)
router.include_router(characters_router)
router.include_router(dashboard_router)
router.include_router(generation_router)
router.include_router(chapter_processing_router)
