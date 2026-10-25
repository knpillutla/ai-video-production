"""OpenAI GPT-4o LLM adapter for structured scriptwriting and directorial timelines."""

from __future__ import annotations

import asyncio
import json
from typing import Any
import httpx

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, LLMProviderProtocol, is_mock_mode


def get_live_openai_api_key(explicit_key: str | None = None) -> str | None:
    """Resolve active OpenAI API key, dynamically checking disk .env for newly saved keys."""
    if explicit_key:
        return explicit_key
    try:
        from dotenv import dotenv_values
        vals = dotenv_values(".env")
        disk_k = vals.get("OPENAI_API_KEY")
        if disk_k and disk_k.strip():
            return disk_k.strip()
    except Exception:
        pass
    return settings.llm.live_openai_api_key or settings.llm.openai_api_key or None


class OpenAILLMAdapter(LLMProviderProtocol):
    """Flagship OpenAI Adapter powered by GPT-4o / GPT-4o-mini via non-blocking Async HTTP."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
        strict: bool = False,
    ):
        self.api_key = get_live_openai_api_key(api_key)
        eff_model = model
        try:
            import os
            from dotenv import dotenv_values
            env_m = os.getenv("OPENAI_MODEL")
            if env_m and env_m.strip():
                eff_model = env_m.strip()
            else:
                disk_m = dotenv_values(".env").get("OPENAI_MODEL")
                if disk_m and disk_m.strip():
                    eff_model = disk_m.strip()
        except Exception:
            pass
        self.model = eff_model or "gpt-4o"
        self.provider = "openai"
        self.strict = strict
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def _post_with_retry(
        self, body: dict[str, Any], timeout: float = 180.0, max_retries: int = 2
    ) -> dict[str, Any]:
        """Post request to OpenAI API with persistent client and exponential backoff."""
        active_key = get_live_openai_api_key(self.api_key)
        if not active_key:
            if self.strict:
                raise RuntimeError("OpenAI API Key is missing. Please set OPENAI_API_KEY in .env.")
            return {}

        client = HTTPClientPool.get_client()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {active_key}",
        }
        req_timeout = httpx.Timeout(timeout, connect=30.0, read=timeout)
        masked_key = f"{active_key[:6]}...{active_key[-4:]}" if len(active_key) >= 12 else "none"
        logger.info(f"openai_api_request: key='{masked_key}' model='{self.model}'")

        for attempt in range(1, max_retries + 2):
            try:
                resp = await client.post(self.endpoint, headers=headers, json=body, timeout=req_timeout)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (500, 502, 503, 504) and attempt <= max_retries:
                    backoff = attempt * 2.0
                    logger.warning(f"openai_api_retry: status={resp.status_code}, retrying in {backoff:.1f}s...")
                    await asyncio.sleep(backoff)
                    continue
                if resp.status_code == 429:
                    err = "OpenAI rate limit or insufficient quota (HTTP 429)."
                    logger.error(f"openai_quota_error: {err}")
                    raise RuntimeError(f"OpenAI Error: {err} Check billing at https://platform.openai.com/account/billing")
                err_text = resp.text[:250]
                logger.error(f"openai_api_non_200: status={resp.status_code}, body={err_text}")
                raise RuntimeError(f"OpenAI API Error (HTTP {resp.status_code}): {err_text}")
            except (httpx.TimeoutException, httpx.NetworkError) as ex:
                if attempt <= max_retries:
                    backoff = attempt * 2.0
                    logger.warning(f"openai_network_retry: attempt {attempt} failed: {ex}. Retrying in {backoff:.1f}s...")
                    await asyncio.sleep(backoff)
                    continue
                logger.error(f"openai_network_failed: {ex}")
                raise RuntimeError(f"OpenAI API request timed out or failed: {ex}") from ex
        return {}

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate unstructured retention narrative text."""
        if is_mock_mode():
            return f"[OpenAI Script] Topic: {prompt[:80]} | Hook: Did you know this changed everything?"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        is_reasoning = any(self.model.startswith(p) for p in ("o1", "o3"))
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if not is_reasoning:
            body["temperature"] = temperature
        try:
            data = await self._post_with_retry(body)
            if data and "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            raise RuntimeError("OpenAI returned empty response choices.")
        except Exception as ex:
            if not is_mock_mode() or self.strict:
                raise RuntimeError(f"Script Generation Failed (OpenAI): {ex}") from ex
            logger.warning(f"openai_text_failed: {ex}. Using mock fallback.")

        return f"[OpenAI Script] Topic: {prompt[:80]} | Hook: Did you know this changed everything?"

    def _build_fallback_storyboard(self, prompt: str) -> dict[str, Any]:
        from src.providers.llm.mock_storyboards import resolve_mock_storyboard
        return resolve_mock_storyboard(prompt)

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any] | None = None,
        audio_path: str | Any | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON screenplay plan obeying schema."""
        fallback = self._build_fallback_storyboard(prompt)
        if is_mock_mode() and not self.strict:
            return fallback

        schema_json = json.dumps(schema, indent=2) if schema else ""
        schema_clause = f"\n\nJSON SCHEMA SPECIFICATION (STRICT ADHERENCE REQUIRED):\n{schema_json}" if schema_json else ""
        sys_prompt = (
            "You are a master broadcast video director. Return ONLY valid JSON adhering strictly to the requested schema.\n"
            f"{schema_clause}\n"
            "Do not include conversational preamble. Strictly output pure, parseable JSON."
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ]
        is_reasoning = any(self.model.startswith(p) for p in ("o1", "o3"))
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        if not is_reasoning:
            body["temperature"] = 0.2

        try:
            data = await self._post_with_retry(body)
            if data and "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                clean = content.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[-1]
                    if clean.endswith("```"):
                        clean = clean.rsplit("\n", 1)[0]
                parsed = json.loads(clean)
                if isinstance(parsed, list):
                    return {"scenes": parsed}
                if "title" in parsed and "title_en" not in parsed:
                    parsed["title_en"] = parsed["title"]
                if "song_title" in parsed and "title_en" not in parsed:
                    parsed["title_en"] = parsed["song_title"]
                if isinstance(parsed, dict):
                    parsed.setdefault("llm_provider", "openai")
                    parsed.setdefault("llm_model", self.model)
                return parsed
            raise RuntimeError("OpenAI returned empty response choices.")
        except Exception as ex:
            if not is_mock_mode() or self.strict:
                raise RuntimeError(f"Script Generation Failed (OpenAI): {ex}") from ex
            logger.warning(f"openai_structured_failed: {ex}. Using mock fallback.")

        return fallback


__all__ = ["OpenAILLMAdapter", "get_live_openai_api_key"]
