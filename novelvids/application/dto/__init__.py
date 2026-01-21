"""Data Transfer Objects for API layer."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class BaseDTO(BaseModel):
    """Base DTO with common configuration."""

    class Config:
        from_attributes = True


# User DTOs
class UserCreateDTO(BaseModel):
    """DTO for creating a user."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdateDTO(BaseModel):
    """DTO for updating a user."""

    username: str | None = None
    email: EmailStr | None = None

class LoginDTO(BaseModel):
    """DTO for user login."""

    username: str
    password: str
    
class UserResponseDTO(BaseDTO):
    """DTO for user response."""

    id: UUID
    username: str
    email: str
    is_active: bool
    balance: float
    created_at: datetime


class TokenDTO(BaseModel):
    """DTO for authentication token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenDTO(BaseModel):
    """DTO for refresh token request."""

    refresh_token: str



# Novel DTOs
class NovelCreateDTO(BaseModel):
    """DTO for creating a novel."""

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    author: str | None = None


class NovelUpdateDTO(BaseModel):
    """DTO for updating a novel."""

    title: str | None = None
    content: str | None = None
    author: str | None = None


class NovelResponseDTO(BaseDTO):
    """DTO for novel response."""

    id: UUID
    title: str
    author: str | None
    status: str
    total_chapters: int
    processed_chapters: int
    created_at: datetime
    updated_at: datetime


class NovelDetailDTO(NovelResponseDTO):
    """DTO for detailed novel response."""

    content: str
    metadata: dict[str, Any]


# Chapter DTOs
class ChapterResponseDTO(BaseDTO):
    """DTO for chapter response."""

    id: UUID
    novel_id: UUID
    number: int
    title: str
    status: str
    scene_count: int
    created_at: datetime


class ChapterDetailDTO(ChapterResponseDTO):
    """DTO for detailed chapter response."""

    content: str
    metadata: dict[str, Any]


# Character DTOs
class CharacterCreateDTO(BaseModel):
    """DTO for creating a character."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    gender: str = "other"
    age_range: str | None = None
    appearance: str | None = None
    personality: str | None = None
    voice_id: str | None = None
    voice_provider: str = "edge_tts"


class CharacterUpdateDTO(BaseModel):
    """DTO for updating a character."""

    name: str | None = None
    description: str | None = None
    gender: str | None = None
    appearance: str | None = None
    voice_id: str | None = None
    voice_provider: str | None = None


class CharacterResponseDTO(BaseDTO):
    """DTO for character response."""

    id: UUID
    novel_id: UUID
    name: str
    description: str | None
    gender: str
    voice_provider: str
    reference_images: list[str]
    created_at: datetime


# Scene DTOs
class SceneResponseDTO(BaseDTO):
    """DTO for scene response."""

    id: UUID
    chapter_id: UUID
    sequence: int
    description: str
    dialogue: str | None
    speaker_id: UUID | None
    image_url: str | None
    audio_url: str | None
    duration: float
    status: str


# Video DTOs
class VideoResponseDTO(BaseDTO):
    """DTO for video response."""

    id: UUID
    novel_id: UUID
    chapter_id: UUID | None
    title: str
    url: str | None
    duration: float
    resolution: str
    fps: int
    status: str
    created_at: datetime


# Workflow DTOs
class WorkflowCreateDTO(BaseModel):
    """DTO for creating a workflow."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    workflow_json: dict[str, Any]
    category: str = "general"
    is_default: bool = False


class WorkflowResponseDTO(BaseDTO):
    """DTO for workflow response."""

    id: UUID
    name: str
    description: str | None
    category: str
    is_default: bool
    created_at: datetime


# Usage DTOs
class UsageRecordResponseDTO(BaseDTO):
    """DTO for usage record response."""

    id: UUID
    resource_type: str
    quantity: float
    unit_cost: float
    total_cost: float
    description: str | None
    created_at: datetime


class UsageSummaryDTO(BaseModel):
    """DTO for usage summary."""

    total_cost: float
    total_images: int
    total_audio_seconds: float
    total_video_seconds: float
    records: list[UsageRecordResponseDTO]


# Generation DTOs
class GenerateImageDTO(BaseModel):
    """DTO for image generation request."""

    prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=576, ge=256, le=2048)
    seed: int = -1
    workflow_id: UUID | None = None


class GenerateAudioDTO(BaseModel):
    """DTO for audio generation request."""

    text: str = Field(min_length=1)
    voice_id: str
    provider: str = "edge_tts"


class ProcessNovelDTO(BaseModel):
    """DTO for novel processing request."""

    novel_id: UUID
    start_chapter: int = 1
    end_chapter: int | None = None
    generate_images: bool = True
    generate_audio: bool = True
    generate_video: bool = True


# Pagination
class PaginationDTO(BaseModel):
    """DTO for pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponseDTO(BaseModel):
    """DTO for paginated response."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
