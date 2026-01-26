"""Database repository implementations."""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from tortoise.models import Model
from tortoise.queryset import QuerySet

from novelvids.domain.repositories import (
    BaseRepository,
    ChapterRepository,
    CharacterRepository,
    NovelRepository,
    SceneRepository,
    UsageRecordRepository,
    UserRepository,
    VideoRepository,
    WorkflowRepository,
)
from novelvids.infrastructure.database.models import (
    ChapterModel,
    CharacterModel,
    ComfyUIWorkflowModel,
    NovelModel,
    SceneModel,
    UsageRecordModel,
    UserModel,
    VideoModel,
)

T = TypeVar("T", bound=Model)


class TortoiseRepository(Generic[T]):
    """Base Tortoise ORM repository implementation."""

    model_class: type[T]

    def _get_queryset(self) -> QuerySet[T]:
        return self.model_class.all()

    async def get_by_id(self, entity_id: UUID) -> T | None:
        return await self.model_class.get_or_none(id=entity_id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[T]:
        queryset = self._get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        return await queryset.offset(skip).limit(limit)

    async def create(self, **data: Any) -> T:
        return await self.model_class.create(**data)

    async def update(self, entity_id: UUID, data: dict) -> T | None:
        entity = await self.get_by_id(entity_id)
        if entity:
            await entity.update_from_dict(data).save()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        deleted = await self.model_class.filter(id=entity_id).delete()
        return deleted > 0

    async def count(self, filters: dict | None = None) -> int:
        queryset = self._get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        return await queryset.count()


class TortoiseNovelRepository(TortoiseRepository[NovelModel], NovelRepository):
    """Tortoise ORM implementation of NovelRepository."""

    model_class = NovelModel

    async def get_by_user_id(self, user_id: UUID) -> list[NovelModel]:
        return await self.model_class.filter(user_id=user_id)

    async def get_with_chapters(self, novel_id: UUID) -> NovelModel | None:
        return await self.model_class.get_or_none(id=novel_id).prefetch_related("chapters")


class TortoiseChapterRepository(TortoiseRepository[ChapterModel], ChapterRepository):
    """Tortoise ORM implementation of ChapterRepository."""

    model_class = ChapterModel

    def _get_queryset(self) -> QuerySet[ChapterModel]:
        """Override to add default ordering by chapter number."""
        return self.model_class.all().order_by("number")

    async def get_by_novel_id(self, novel_id: UUID) -> list[ChapterModel]:
        return await self.model_class.filter(novel_id=novel_id).order_by("number")


class TortoiseCharacterRepository(TortoiseRepository[CharacterModel], CharacterRepository):
    """Tortoise ORM implementation of CharacterRepository."""

    model_class = CharacterModel

    async def get_by_novel_id(self, novel_id: UUID) -> list[CharacterModel]:
        return await self.model_class.filter(novel_id=novel_id)

    async def get_by_name(self, novel_id: UUID, name: str) -> CharacterModel | None:
        return await self.model_class.get_or_none(novel_id=novel_id, name=name)


class TortoiseSceneRepository(TortoiseRepository[SceneModel], SceneRepository):
    """Tortoise ORM implementation of SceneRepository."""

    model_class = SceneModel

    async def get_by_chapter_id(self, chapter_id: UUID) -> list[SceneModel]:
        return await self.model_class.filter(chapter_id=chapter_id).order_by("sequence")


class TortoiseVideoRepository(TortoiseRepository[VideoModel], VideoRepository):
    """Tortoise ORM implementation of VideoRepository."""

    model_class = VideoModel

    async def get_by_novel_id(self, novel_id: UUID) -> list[VideoModel]:
        return await self.model_class.filter(novel_id=novel_id)


class TortoiseUserRepository(TortoiseRepository[UserModel], UserRepository):
    """Tortoise ORM implementation of UserRepository."""

    model_class = UserModel

    async def get_by_email(self, email: str) -> UserModel | None:
        return await self.model_class.get_or_none(email=email)

    async def get_by_username(self, username: str) -> UserModel | None:
        return await self.model_class.get_or_none(username=username)


class TortoiseUsageRecordRepository(TortoiseRepository[UsageRecordModel], UsageRecordRepository):
    """Tortoise ORM implementation of UsageRecordRepository."""

    model_class = UsageRecordModel

    async def get_by_user_id(
        self,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[UsageRecordModel]:
        queryset = self.model_class.filter(user_id=user_id)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        return await queryset.order_by("-created_at")

    async def get_total_cost(
        self,
        user_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> float:
        from tortoise.functions import Sum

        queryset = self.model_class.filter(user_id=user_id)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        result = await queryset.annotate(total=Sum("total_cost")).values("total")
        return float(result[0]["total"] or 0) if result else 0.0


class TortoiseWorkflowRepository(TortoiseRepository[ComfyUIWorkflowModel], WorkflowRepository):
    """Tortoise ORM implementation of WorkflowRepository."""

    model_class = ComfyUIWorkflowModel

    async def get_by_category(self, category: str) -> list[ComfyUIWorkflowModel]:
        return await self.model_class.filter(category=category)

    async def get_default(self, category: str) -> ComfyUIWorkflowModel | None:
        return await self.model_class.get_or_none(category=category, is_default=True)
