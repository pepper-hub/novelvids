"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
from tortoise.contrib.fastapi import register_tortoise

from novelvids.api.middleware import CORSMiddleware as CORSConfig
from novelvids.api.middleware import LoggingMiddleware
from novelvids.api.v1 import router as v1_router
from novelvids.core.config import settings
from novelvids.infrastructure.database.config import get_tortoise_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Novel Video Generator - Generate videos from novels using ComfyUI",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Add middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CORSMiddleware, **CORSConfig.get_config())

    # Register routes
    app.include_router(v1_router, prefix="/api")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}

    # Register Tortoise ORM
    register_tortoise(
        app,
        config=get_tortoise_config(),
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return app


app = create_app()
