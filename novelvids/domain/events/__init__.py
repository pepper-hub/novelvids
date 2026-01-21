"""Domain events for event-driven architecture."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base class for domain events."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(default_factory=dict)


class NovelCreatedEvent(DomainEvent):
    """Event raised when a novel is created."""

    event_type: str = "novel.created"
    novel_id: UUID
    user_id: UUID


class NovelProcessingStartedEvent(DomainEvent):
    """Event raised when novel processing starts."""

    event_type: str = "novel.processing_started"
    novel_id: UUID


class NovelProcessingCompletedEvent(DomainEvent):
    """Event raised when novel processing completes."""

    event_type: str = "novel.processing_completed"
    novel_id: UUID
    video_url: str | None = None


class ChapterProcessedEvent(DomainEvent):
    """Event raised when a chapter is processed."""

    event_type: str = "chapter.processed"
    chapter_id: UUID
    novel_id: UUID


class CharacterExtractedEvent(DomainEvent):
    """Event raised when characters are extracted."""

    event_type: str = "character.extracted"
    novel_id: UUID
    character_ids: list[UUID]


class SceneGeneratedEvent(DomainEvent):
    """Event raised when a scene is generated."""

    event_type: str = "scene.generated"
    scene_id: UUID
    chapter_id: UUID


class ImageGeneratedEvent(DomainEvent):
    """Event raised when an image is generated."""

    event_type: str = "image.generated"
    scene_id: UUID
    image_url: str
    cost: float


class AudioGeneratedEvent(DomainEvent):
    """Event raised when audio is generated."""

    event_type: str = "audio.generated"
    scene_id: UUID
    audio_url: str
    duration: float
    cost: float


class VideoComposedEvent(DomainEvent):
    """Event raised when video is composed."""

    event_type: str = "video.composed"
    video_id: UUID
    video_url: str
    duration: float


class UsageRecordedEvent(DomainEvent):
    """Event raised when usage is recorded."""

    event_type: str = "usage.recorded"
    user_id: UUID
    resource_type: str
    cost: float


class TaskFailedEvent(DomainEvent):
    """Event raised when a task fails."""

    event_type: str = "task.failed"
    task_id: UUID
    error_message: str
    error_details: dict[str, Any] = Field(default_factory=dict)
