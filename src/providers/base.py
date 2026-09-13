"""Abstract provider protocols and shared HTTP connection pooling."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

import httpx


class HTTPClientPool:
    """Manages persistent asynchronous HTTP client sessions for zero socket churn."""

    _client: httpx.AsyncClient | None = None
    _loop: asyncio.AbstractEventLoop | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if cls._client is None or cls._client.is_closed or (cls._loop is not None and cls._loop is not current_loop):
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
            cls._loop = current_loop
        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client and not cls._client.is_closed:
            try:
                await cls._client.aclose()
            except RuntimeError:
                pass
            finally:
                cls._client = None
                cls._loop = None


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


def is_mock_mode() -> bool:
    """Return True if running in offline mock mode (pytest, test env, or MOCK_ALL_MODELS)."""
    import os

    if os.getenv("MOCK_ALL_MODELS", "").lower() in ("1", "true", "yes", "on"):
        return True
    if os.getenv("TESTING", "").lower() in ("1", "true", "yes", "on"):
        return True
    if os.getenv("PYTEST_CURRENT_TEST") is not None:
        return True
    try:
        from src.core.config import settings

        if settings.app.mock_all_models or settings.app.app_env in ("test", "testing"):
            return True
    except Exception:
        pass
    return False


__all__ = [
    "HTTPClientPool",
    "LLMProviderProtocol",
    "TTSProviderProtocol",
    "VisualProviderProtocol",
    "MusicProviderProtocol",
    "VideoMotionProtocol",
    "LipSyncProtocol",
    "is_mock_mode",
]

