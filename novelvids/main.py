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

    # Register exception handlers
    from fastapi.exceptions import RequestValidationError
    from tortoise.exceptions import DoesNotExist, IntegrityError
    from novelvids.api.exceptions import AppException
    from novelvids.api.handlers import (
        app_exception_handler,
        global_exception_handler,
        validation_exception_handler,
        integrity_error_handler,
        does_not_exist_handler,
    )

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(DoesNotExist, does_not_exist_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    return app


app = create_app()
