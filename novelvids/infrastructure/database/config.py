"""Database configuration for Tortoise ORM."""

from novelvids.core.config import settings


def get_tortoise_config() -> dict:
    """Get Tortoise ORM configuration."""
    return {
        "connections": {
            "default": settings.database.get_connection_url(),
        },
        "apps": {
            "models": {
                "models": [
                    "novelvids.infrastructure.database.models",
                    "aerich.models",
                ],
                "default_connection": "default",
            },
        },
        "use_tz": True,
        "timezone": "UTC",
    }


TORTOISE_ORM = get_tortoise_config()
