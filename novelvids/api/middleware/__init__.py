"""API middleware."""

import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration:.3f}s"
        )

        # Add timing header
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        return response


class CORSMiddleware:
    """CORS middleware configuration helper."""

    @staticmethod
    def get_config() -> dict:
        return {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
