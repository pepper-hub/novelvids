"""File storage infrastructure."""

import hashlib
import os
from pathlib import Path
from uuid import uuid4

import aiofiles

from novelvids.core.config import settings
from novelvids.core.exceptions import StorageError


class LocalStorage:
    """Local file storage implementation."""

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.storage.base_path)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure storage directories exist."""
        directories = ["images", "audio", "video", "temp", "workflows"]
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, category: str, filename: str) -> Path:
        """Get full file path for a category and filename."""
        return self.base_path / category / filename

    def _generate_filename(self, extension: str, prefix: str = "") -> str:
        """Generate a unique filename."""
        unique_id = str(uuid4())[:8]
        prefix_part = f"{prefix}_" if prefix else ""
        return f"{prefix_part}{unique_id}.{extension}"

    async def save_file(
        self,
        content: bytes,
        category: str,
        extension: str,
        filename: str | None = None,
    ) -> str:
        """Save file content and return the relative path."""
        if len(content) > settings.storage.max_file_size:
            raise StorageError(f"File exceeds maximum size of {settings.storage.max_file_size} bytes")

        if filename is None:
            filename = self._generate_filename(extension)

        file_path = self._get_file_path(category, filename)
        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            return f"{category}/{filename}"
        except Exception as e:
            raise StorageError(f"Failed to save file: {e}") from e

    async def read_file(self, relative_path: str) -> bytes:
        """Read file content by relative path."""
        file_path = self.base_path / relative_path
        if not file_path.exists():
            raise StorageError(f"File not found: {relative_path}")

        try:
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
        except Exception as e:
            raise StorageError(f"Failed to read file: {e}") from e

    async def delete_file(self, relative_path: str) -> bool:
        """Delete file by relative path."""
        file_path = self.base_path / relative_path
        if file_path.exists():
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                raise StorageError(f"Failed to delete file: {e}") from e
        return False

    def get_full_path(self, relative_path: str) -> str:
        """Get full filesystem path for a relative path."""
        return str(self.base_path / relative_path)

    def get_url(self, relative_path: str) -> str:
        """Get URL for accessing a file (for local, returns path)."""
        return f"/storage/{relative_path}"

    async def compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    async def save_image(self, content: bytes, prefix: str = "") -> str:
        """Save image content."""
        return await self.save_file(content, "images", "png", prefix=prefix if prefix else None)

    async def save_audio(self, content: bytes, extension: str = "mp3") -> str:
        """Save audio content."""
        return await self.save_file(content, "audio", extension)

    async def save_video(self, content: bytes, extension: str = "mp4") -> str:
        """Save video content."""
        return await self.save_file(content, "video", extension)
