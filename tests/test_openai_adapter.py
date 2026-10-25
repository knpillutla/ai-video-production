"""Targeted unit tests for OpenAILLMAdapter and LLM factory (Rule 8 offline deterministic)."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch
import pytest

from src.providers.llm.llm_factory import get_llm_adapter, resolve_llm_provider
from src.providers.llm.openai_adapter import OpenAILLMAdapter


def test_resolve_llm_provider_env():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}):
        assert resolve_llm_provider() == "openai"
    with patch.dict(os.environ, {"LLM_PROVIDER": "gemini"}):
        assert resolve_llm_provider() == "gemini"
    assert resolve_llm_provider("openai") == "openai"


def test_get_llm_adapter_factory():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}):
        adapter = get_llm_adapter()
        assert isinstance(adapter, OpenAILLMAdapter)
        assert adapter.model == "gpt-4o"


@pytest.mark.asyncio
async def test_openai_adapter_mock_mode():
    with patch("src.providers.llm.openai_adapter.is_mock_mode", return_value=True):
        adapter = OpenAILLMAdapter(api_key="sk-test", strict=False)
        text = await adapter.generate_text("Test prompt")
        assert "[OpenAI Script]" in text
        data = await adapter.generate_structured("Test prompt")
        assert "scenes" in data or "characters" in data


@pytest.mark.asyncio
async def test_openai_adapter_structured_parsing():
    adapter = OpenAILLMAdapter(api_key="sk-test", strict=True)
    mock_resp = {
        "choices": [{
            "message": {
                "content": '{"title_en": "Ocean Waves", "title_localized": "Saagara Tarangini", "broadcast_timeline": []}'
            }
        }]
    }
    with patch("src.providers.llm.openai_adapter.is_mock_mode", return_value=False):
        with patch.object(adapter, "_post_with_retry", new=AsyncMock(return_value=mock_resp)):
            res = await adapter.generate_structured("Prompt")
            assert res.get("title_en") == "Ocean Waves"
            assert res.get("title_localized") == "Saagara Tarangini"
            assert res.get("llm_provider") == "openai"
            assert res.get("llm_model") == "gpt-4o"


def test_resolve_llm_model():
    from src.providers.llm.llm_factory import resolve_llm_model
    assert resolve_llm_model("openai", "o3-mini") == "o3-mini"
    with patch.dict(os.environ, {"OPENAI_MODEL": "chatgpt-4o-latest"}):
        assert resolve_llm_model("openai") == "chatgpt-4o-latest"
    with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-2.5-pro"}):
        assert resolve_llm_model("gemini") == "gemini-2.5-pro"
