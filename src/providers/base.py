"""Abstract provider protocols and shared HTTP connection pooling."""

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

import httpx


class HTTPClientPool:
    """Manages persistent asynchronous HTTP client sessions for zero socket churn."""

    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None


@runtime_checkable
class LLMProviderProtocol(Protocol):
    """Protocol for creative scriptwriting and structured transcreation."""

    async def generate_text(self, prompt: str, system_prompt: str, temperature: float = 0.7) -> str:
        ...

    async def generate_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        ...


@runtime_checkable
class TTSProviderProtocol(Protocol):
    """Protocol for neural speech narration."""

    async def synthesize_speech(self, text: str, voice_id: str, language_code: str) -> bytes:
        ...


@runtime_checkable
class VisualProviderProtocol(Protocol):
    """Protocol for 4K diffusion image generation."""

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        ...


@runtime_checkable
class MusicProviderProtocol(Protocol):
    """Protocol for royalty-cleared background music generation."""

    async def generate_track(self, genre: str, mood: str, duration_seconds: int) -> str:
        ...


@runtime_checkable
class VideoMotionProtocol(Protocol):
    """Protocol for video motion diffusion synthesis."""

    async def generate_motion(self, image_url_or_path: str, motion_prompt: str, duration_seconds: int = 5) -> str:
        ...


@runtime_checkable
class LipSyncProtocol(Protocol):
    """Protocol for talking avatar mouth synchronization."""

    async def generate_lipsync(self, face_image_path: str, audio_stem_path: str) -> str:
        ...


__all__ = [
    "HTTPClientPool",
    "LLMProviderProtocol",
    "TTSProviderProtocol",
    "VisualProviderProtocol",
    "MusicProviderProtocol",
    "VideoMotionProtocol",
    "LipSyncProtocol",
]
