"""Domain services for business logic."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from novelvids.domain.entities import Character, Chapter, Novel, Scene


class NovelParserService(ABC):
    """Service for parsing novels and extracting information."""

    @abstractmethod
    async def parse_novel(self, content: str) -> dict[str, Any]:
        """Parse novel content and extract metadata."""
        pass

    @abstractmethod
    async def extract_chapters(self, content: str) -> list[dict[str, Any]]:
        """Extract chapters from novel content."""
        pass

    @abstractmethod
    async def extract_characters(self, content: str) -> list[dict[str, Any]]:
        """Extract characters from novel content."""
        pass

    @abstractmethod
    async def generate_scenes(self, chapter: Chapter) -> list[dict[str, Any]]:
        """Generate scene descriptions from chapter content."""
        pass


class ImageGenerationService(ABC):
    """Service for generating images via ComfyUI."""

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        width: int = 1024,
        height: int = 576,
        seed: int | None = None,
        workflow_id: UUID | None = None,
    ) -> str:
        """Generate a single image and return URL."""
        pass

    @abstractmethod
    async def generate_character_reference(
        self,
        character: Character,
        num_images: int = 4,
    ) -> list[str]:
        """Generate reference images for a character."""
        pass

    @abstractmethod
    async def generate_scene_image(
        self,
        scene: Scene,
        characters: list[Character],
    ) -> str:
        """Generate image for a scene with character consistency."""
        pass


class AudioGenerationService(ABC):
    """Service for generating audio/voice."""

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        provider: str = "edge_tts",
    ) -> tuple[str, float]:
        """Generate speech audio and return (url, duration)."""
        pass

    @abstractmethod
    async def clone_voice(
        self,
        reference_audio: str,
        text: str,
    ) -> tuple[str, float]:
        """Clone voice from reference audio."""
        pass

    @abstractmethod
    async def generate_dialogue_audio(
        self,
        scene: Scene,
        character: Character | None,
    ) -> tuple[str, float]:
        """Generate audio for scene dialogue."""
        pass


class VideoCompositionService(ABC):
    """Service for composing final videos."""

    @abstractmethod
    async def compose_scene_video(
        self,
        scene: Scene,
        image_url: str,
        audio_url: str | None,
    ) -> str:
        """Compose a single scene video."""
        pass

    @abstractmethod
    async def compose_chapter_video(
        self,
        chapter: Chapter,
        scene_videos: list[str],
    ) -> str:
        """Compose chapter video from scene videos."""
        pass

    @abstractmethod
    async def compose_full_video(
        self,
        novel: Novel,
        chapter_videos: list[str],
    ) -> str:
        """Compose full novel video from chapter videos."""
        pass


class BillingService(ABC):
    """Service for managing billing and usage tracking."""

    @abstractmethod
    async def record_usage(
        self,
        user_id: UUID,
        resource_type: str,
        quantity: float,
        description: str | None = None,
    ) -> float:
        """Record resource usage and return cost."""
        pass

    @abstractmethod
    async def check_balance(self, user_id: UUID, required_amount: float) -> bool:
        """Check if user has sufficient balance."""
        pass

    @abstractmethod
    async def deduct_balance(self, user_id: UUID, amount: float) -> float:
        """Deduct amount from user balance."""
        pass

    @abstractmethod
    async def get_usage_summary(
        self,
        user_id: UUID,
        start_date=None,
        end_date=None,
    ) -> dict[str, Any]:
        """Get usage summary for a user."""
        pass
