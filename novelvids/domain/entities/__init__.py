"""Domain entities for the application."""

from abc import ABC
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EntityBase(BaseModel, ABC):
    """Base class for all domain entities."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class TaskStatus(StrEnum):
    """Task execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Gender(StrEnum):
    """Character gender."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class VoiceProvider(StrEnum):
    """Voice synthesis provider."""

    EDGE_TTS = "edge_tts"
    AZURE = "azure"
    OPENAI = "openai"
    FISH_SPEECH = "fish_speech"
    CUSTOM = "custom"


class Novel(EntityBase):
    """Novel entity representing a story to be converted to video."""

    title: str
    content: str
    author: str | None = None
    user_id: UUID
    status: TaskStatus = TaskStatus.PENDING
    total_chapters: int = 0
    processed_chapters: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chapter(EntityBase):
    """Chapter entity representing a section of a novel."""

    novel_id: UUID
    number: int
    title: str
    content: str
    status: TaskStatus = TaskStatus.PENDING
    scene_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class Character(EntityBase):
    """Character entity for maintaining character consistency."""

    name: str
    novel_id: UUID
    description: str | None = None
    gender: Gender = Gender.OTHER
    age_range: str | None = None
    appearance: str | None = None
    personality: str | None = None
    voice_id: str | None = None
    voice_provider: VoiceProvider = VoiceProvider.EDGE_TTS
    reference_images: list[str] = Field(default_factory=list)
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Scene(EntityBase):
    """Scene entity representing a single frame/shot."""

    chapter_id: UUID
    sequence: int
    description: str
    dialogue: str | None = None
    speaker_id: UUID | None = None
    prompt: str | None = None
    negative_prompt: str | None = None
    image_url: str | None = None
    audio_url: str | None = None
    duration: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)


class Video(EntityBase):
    """Video entity representing a generated video."""

    novel_id: UUID
    chapter_id: UUID | None = None
    title: str
    url: str | None = None
    duration: float = 0.0
    resolution: str = "1920x1080"
    fps: int = 24
    status: TaskStatus = TaskStatus.PENDING
    metadata: dict[str, Any] = Field(default_factory=dict)


class User(EntityBase):
    """User entity."""

    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    balance: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class UsageRecord(EntityBase):
    """Usage record for billing."""

    user_id: UUID
    resource_type: str
    quantity: float
    unit_cost: float
    total_cost: float
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIWorkflow(EntityBase):
    """ComfyUI workflow configuration."""

    name: str
    description: str | None = None
    workflow_json: dict[str, Any]
    category: str = "general"
    is_default: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
