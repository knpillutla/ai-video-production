"""Global Pytest configuration and model testing cost governance.

Non-Negotiable Rule:
When testing models as part of automated tests, only run one test only with
10 sec duration, to ensure we do not call more than one test, to save on costs.
The test suite must only be run locally even if model keys are present.
"""

import os
from typing import Any
import pytest
import httpx

# Pre-set environment variables so module-level imports default to local mock
os.environ["MOCK_ALL_MODELS"] = "true"
os.environ["TESTING"] = "true"
os.environ["APP_ENV"] = "test"

# Domains of paid external AI providers that must NEVER be called by automated tests
BLOCKED_MODEL_DOMAINS = (
    "generativelanguage.googleapis.com",
    "api.together.xyz",
    "image.pollinations.ai",
    "speech.microsoft.com",
    "api.suno.ai",
    "queue.fal.run",
)

LIVE_MODEL_MAX_DURATION_SECONDS = 10.0


def clamp_model_test_duration(duration_seconds: float) -> float:
    """Enforce maximum 10-second duration cap for live model tests."""
    return min(float(duration_seconds), LIVE_MODEL_MAX_DURATION_SECONDS)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for model testing safety."""
    config.addinivalue_line(
        "markers",
        "live_model: mark test as executing against a real/paid external AI model API",
    )


def pytest_collection_modifyitems(session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
    """Ensure that when testing models as part of automated tests, ONLY ONE test is run."""
    live_items = [item for item in items if item.get_closest_marker("live_model") is not None]

    if len(live_items) > 1:
        raise pytest.UsageError(
            f"MODEL TESTING COST SAFETY VIOLATION: Found {len(live_items)} live model tests! "
            "When testing models as part of automated tests, only run one test only with "
            "10 sec duration, to ensure we do not call more than one test, to save on costs."
        )


@pytest.fixture(autouse=True, scope="session")
def enforce_offline_model_safety():
    """Session-wide network guard: intercepts and blocks calls to paid model endpoints."""
    original_send = httpx.AsyncClient.send

    async def guarded_async_send(self: httpx.AsyncClient, request: httpx.Request, *args: Any, **kwargs: Any) -> httpx.Response:
        url_str = str(request.url)
        is_live_test = os.getenv("ALLOW_SINGLE_LIVE_MODEL_TEST", "false").lower() == "true"

        for domain in BLOCKED_MODEL_DOMAINS:
            if domain in url_str and not is_live_test:
                raise RuntimeError(
                    f"CRITICAL SAFETY VIOLATION: Automated test attempted to call external model API: {url_str}. "
                    "The test suite must only be run locally even if model keys are present. "
                    "When testing models as part of automated tests, only run one test only with 10 sec duration."
                )
        return await original_send(self, request, *args, **kwargs)

    httpx.AsyncClient.send = guarded_async_send
    yield
    httpx.AsyncClient.send = original_send
