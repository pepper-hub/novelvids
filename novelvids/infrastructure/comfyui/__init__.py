"""ComfyUI API client for image generation."""

import asyncio
from typing import Any
from uuid import uuid4

import aiohttp
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from novelvids.core.config import settings
from novelvids.core.exceptions import ComfyUIError


class ComfyUIClient:
    """Client for interacting with ComfyUI API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url = base_url or settings.comfyui.base_url
        self.api_key = api_key or settings.comfyui.api_key
        self.timeout = timeout or settings.comfyui.timeout
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def health_check(self) -> bool:
        """Check if ComfyUI server is available."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/system_stats") as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"ComfyUI health check failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def queue_prompt(self, workflow: dict[str, Any]) -> str:
        """Queue a workflow prompt and return the prompt ID."""
        session = await self._get_session()
        client_id = str(uuid4())

        payload = {
            "prompt": workflow,
            "client_id": client_id,
        }

        try:
            async with session.post(
                f"{self.base_url}/prompt",
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ComfyUIError(f"Failed to queue prompt: {error_text}")
                data = await response.json()
                return data["prompt_id"]
        except aiohttp.ClientError as e:
            raise ComfyUIError(f"Network error: {e}") from e

    async def get_history(self, prompt_id: str) -> dict[str, Any]:
        """Get execution history for a prompt."""
        session = await self._get_session()
        async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
            if response.status != 200:
                raise ComfyUIError(f"Failed to get history: {response.status}")
            return await response.json()

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Download generated image."""
        session = await self._get_session()
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type,
        }
        async with session.get(f"{self.base_url}/view", params=params) as response:
            if response.status != 200:
                raise ComfyUIError(f"Failed to get image: {response.status}")
            return await response.read()

    async def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: float = 1.0,
        max_wait: float = 300.0,
    ) -> dict[str, Any]:
        """Wait for a prompt to complete and return the result."""
        elapsed = 0.0
        while elapsed < max_wait:
            history = await self.get_history(prompt_id)
            if prompt_id in history:
                prompt_data = history[prompt_id]
                if "outputs" in prompt_data:
                    return prompt_data["outputs"]
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise ComfyUIError(f"Prompt {prompt_id} timed out after {max_wait}s")

    async def generate_image(
        self,
        workflow: dict[str, Any],
        output_node_id: str = "9",
    ) -> list[bytes]:
        """Generate images using a workflow and return the image data."""
        prompt_id = await self.queue_prompt(workflow)
        outputs = await self.wait_for_completion(prompt_id)

        images = []
        if output_node_id in outputs:
            for image_info in outputs[output_node_id].get("images", []):
                image_data = await self.get_image(
                    filename=image_info["filename"],
                    subfolder=image_info.get("subfolder", ""),
                    folder_type=image_info.get("type", "output"),
                )
                images.append(image_data)

        return images


class ComfyUIWorkflowBuilder:
    """Builder for creating ComfyUI workflow configurations."""

    @staticmethod
    def build_txt2img_workflow(
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        seed: int = -1,
        steps: int = 20,
        cfg: float = 7.0,
        sampler: str = "euler",
        scheduler: str = "normal",
        checkpoint: str = "sd_xl_base_1.0.safetensors",
    ) -> dict[str, Any]:
        """Build a basic text-to-image workflow."""
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": cfg,
                    "denoise": 1,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["7", 0],
                    "positive": ["6", 0],
                    "sampler_name": sampler,
                    "scheduler": scheduler,
                    "seed": seed if seed >= 0 else None,
                    "steps": steps,
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": height,
                    "width": width,
                },
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": prompt,
                },
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": negative_prompt,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "novelvids",
                    "images": ["8", 0],
                },
            },
        }

    @staticmethod
    def inject_character_reference(
        workflow: dict[str, Any],
        reference_images: list[str],
        strength: float = 0.8,
    ) -> dict[str, Any]:
        """Inject character reference images into workflow for consistency."""
        # This is a placeholder for IP-Adapter or similar integration
        # Actual implementation depends on the ComfyUI workflow structure
        return workflow
