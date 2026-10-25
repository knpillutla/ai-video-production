"""Unified LLM Provider Factory.

Dynamically routes LLM calls to Gemini or OpenAI based on:
1. Explicit function parameter (e.g. provider='openai')
2. LLM_PROVIDER in .env (e.g. LLM_PROVIDER=openai)
3. Available API keys (falls back to OpenAI if Gemini is not configured)
"""

from __future__ import annotations

import os
from typing import Optional

from src.core.config import settings
from src.providers.base import LLMProviderProtocol
from src.providers.llm.gemini_adapter import GeminiLLMAdapter, get_live_gemini_api_key
from src.providers.llm.openai_adapter import OpenAILLMAdapter, get_live_openai_api_key


def resolve_llm_provider(explicit_provider: Optional[str] = None) -> str:
    """Resolve the active LLM provider name ('gemini' or 'openai')."""
    if explicit_provider and explicit_provider.strip():
        return explicit_provider.strip().lower()

    env_prov = os.getenv("LLM_PROVIDER")
    if env_prov and env_prov.strip():
        return env_prov.strip().lower()

    cfg_prov = getattr(settings.llm, "effective_llm_provider", "gemini")
    if cfg_prov and cfg_prov != "gemini":
        return cfg_prov.lower()

    # If OpenAI key exists but Gemini key is absent, default to OpenAI
    if not get_live_gemini_api_key() and get_live_openai_api_key():
        return "openai"

    return "gemini"


def resolve_llm_model(provider: Optional[str] = None, explicit_model: Optional[str] = None) -> str:
    """Resolve the active LLM model name ('chatgpt-4o-latest', 'gemini-flash-latest', etc.)."""
    if explicit_model and explicit_model.strip():
        return explicit_model.strip()
    eff_prov = resolve_llm_provider(provider)
    if eff_prov in ("openai", "gpt-4o", "chatgpt"):
        return os.getenv("OPENAI_MODEL") or getattr(settings.llm, "default_openai_model", "gpt-4o")
    return os.getenv("GEMINI_MODEL") or "gemini-flash-latest"


def get_llm_adapter(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    strict: bool = False,
    api_key: Optional[str] = None,
) -> LLMProviderProtocol:
    """Instantiate and return the configured LLM adapter."""
    eff_prov = resolve_llm_provider(provider)
    eff_model = resolve_llm_model(eff_prov, model)
    if eff_prov in ("openai", "gpt-4o", "chatgpt"):
        return OpenAILLMAdapter(api_key=api_key, model=eff_model, strict=strict)

    return GeminiLLMAdapter(api_key=api_key, model=eff_model, strict=strict)


__all__ = ["get_llm_adapter", "resolve_llm_provider", "resolve_llm_model"]
