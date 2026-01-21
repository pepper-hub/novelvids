"""Repository interfaces for domain entities."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from novelvids.domain.entities import EntityBase

T = TypeVar("T", bound=EntityBase)


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[T]:
        """Get all entities with pagination and optional filters."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, entity_id: UUID, data: dict) -> T | None:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID."""
        pass

    @abstractmethod
    async def count(self, filters: dict | None = None) -> int:
        """Count entities with optional filters."""
        pass


class NovelRepository(BaseRepository):
    """Repository interface for Novel entities."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list:
        """Get all novels by user ID."""
        pass

    @abstractmethod
    async def get_with_chapters(self, novel_id: UUID):
        """Get novel with all its chapters."""
        pass


class ChapterRepository(BaseRepository):
    """Repository interface for Chapter entities."""

    @abstractmethod
    async def get_by_novel_id(self, novel_id: UUID) -> list:
        """Get all chapters by novel ID."""
        pass


class CharacterRepository(BaseRepository):
    """Repository interface for Character entities."""

    @abstractmethod
    async def get_by_novel_id(self, novel_id: UUID) -> list:
        """Get all characters by novel ID."""
        pass

    @abstractmethod
    async def get_by_name(self, novel_id: UUID, name: str):
        """Get character by name within a novel."""
        pass


class SceneRepository(BaseRepository):
    """Repository interface for Scene entities."""

    @abstractmethod
    async def get_by_chapter_id(self, chapter_id: UUID) -> list:
        """Get all scenes by chapter ID."""
        pass


class VideoRepository(BaseRepository):
    """Repository interface for Video entities."""

    @abstractmethod
    async def get_by_novel_id(self, novel_id: UUID) -> list:
        """Get all videos by novel ID."""
        pass


class UserRepository(BaseRepository):
    """Repository interface for User entities."""

    @abstractmethod
    async def get_by_email(self, email: str):
        """Get user by email."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str):
        """Get user by username."""
        pass


class UsageRecordRepository(BaseRepository):
    """Repository interface for UsageRecord entities."""

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date=None,
        end_date=None,
    ) -> list:
        """Get usage records by user ID with optional date range."""
        pass

    @abstractmethod
    async def get_total_cost(
        self,
        user_id: UUID,
        start_date=None,
        end_date=None,
    ) -> float:
        """Get total cost for a user within date range."""
        pass


class WorkflowRepository(BaseRepository):
    """Repository interface for ComfyUIWorkflow entities."""

    @abstractmethod
    async def get_by_category(self, category: str) -> list:
        """Get workflows by category."""
        pass

    @abstractmethod
    async def get_default(self, category: str):
        """Get default workflow for a category."""
        pass
