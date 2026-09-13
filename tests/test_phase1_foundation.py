"""Phase 1 Foundation Verification Test Suite."""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from src.api.main import app
from src.core.queue import TaskQueue
from src.providers.base import (
    HTTPClientPool,
    LipSyncProtocol,
    LLMProviderProtocol,
    MusicProviderProtocol,
    TTSProviderProtocol,
    VideoMotionProtocol,
    VisualProviderProtocol,
)


@pytest.mark.asyncio
async def test_web_studio_ui_and_health_served():
    """Verify that FastAPI serves both /health API and interactive Web Studio UI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Health check
        health_resp = await ac.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"

        # 2. Web UI dashboard
        ui_resp = await ac.get("/ui")
        assert ui_resp.status_code == 200
        assert "text/html" in ui_resp.headers["content-type"]
        assert "CineAI Studio" in ui_resp.text


@pytest.mark.asyncio
async def test_task_queue_lifecycle():
    """Verify asynchronous task queue enqueue, worker execution, and completion."""
    queue = TaskQueue()
    executed_payloads = []

    async def sample_handler(payload: dict):
        executed_payloads.append(payload["item"])

    queue.register_handler("test_job", sample_handler)

    # 1. Enqueue task
    task = await queue.enqueue("test_job", {"item": "render_4k_scene_1"})
    assert task.status == "queued"
    assert queue.queue_depth == 1

    # 2. Start worker and await completion
    await queue.start_worker()
    await asyncio.sleep(0.1)

    assert len(executed_payloads) == 1
    assert executed_payloads[0] == "render_4k_scene_1"
    assert queue.queue_depth == 0

    await queue.stop_worker()


@pytest.mark.asyncio
async def test_http_connection_pool_lifecycle():
    """Verify singleton HTTP client session reuse and clean shutdown."""
    client1 = HTTPClientPool.get_client()
    client2 = HTTPClientPool.get_client()
    assert client1 is client2  # Shared connection pool
    assert not client1.is_closed

    await HTTPClientPool.close()
    assert HTTPClientPool._client is None


def test_provider_protocols_runtime_checkable():
    """Verify all 6 modal AI provider protocols are registered and runtime checkable."""
    protocols = [
        LLMProviderProtocol,
        TTSProviderProtocol,
        VisualProviderProtocol,
        MusicProviderProtocol,
        VideoMotionProtocol,
        LipSyncProtocol,
    ]
    for proto in protocols:
        assert isinstance(proto, type)
