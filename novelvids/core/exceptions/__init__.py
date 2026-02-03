"""Custom exceptions for the application."""

from typing import Any


class NovelVidsError(Exception):
    """Base exception for NovelVids application."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(NovelVidsError):
    """Validation error exception."""

    pass


class NotFoundError(NovelVidsError):
    """Resource not found exception."""

    pass


class AuthenticationError(NovelVidsError):
    """Authentication failed exception."""

    pass


class AuthorizationError(NovelVidsError):
    """Authorization failed exception."""

    pass



class StorageError(NovelVidsError):
    """Storage operation error exception."""

    pass


class BillingError(NovelVidsError):
    """Billing operation error exception."""

    pass


class TaskError(NovelVidsError):
    """Task execution error exception."""

    pass


class InsufficientBalanceError(BillingError):
    """Insufficient balance exception."""

    pass
