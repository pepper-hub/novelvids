"""Database infrastructure module."""

from novelvids.infrastructure.database.config import TORTOISE_ORM, get_tortoise_config
from novelvids.infrastructure.database.repositories import (
    TortoiseChapterRepository,
    TortoiseCharacterRepository,
    TortoiseNovelRepository,
    TortoiseSceneRepository,
    TortoiseUsageRecordRepository,
    TortoiseUserRepository,
    TortoiseVideoRepository,
    TortoiseWorkflowRepository,
)

__all__ = [
    "TORTOISE_ORM",
    "get_tortoise_config",
    "TortoiseNovelRepository",
    "TortoiseChapterRepository",
    "TortoiseCharacterRepository",
    "TortoiseSceneRepository",
    "TortoiseVideoRepository",
    "TortoiseUserRepository",
    "TortoiseUsageRecordRepository",
    "TortoiseWorkflowRepository",
]
