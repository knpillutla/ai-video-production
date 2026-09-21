"""Google Gemini 1.5 Pro LLM adapter for structured scriptwriting and retention hooks."""

import json
from typing import Any
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, LLMProviderProtocol, is_mock_mode


class CharacterMetadata(BaseModel):
    """Culturally authentic character metadata synthesized from script."""

    name: str = Field(description="Culturally authentic character name matching language/region")
    age: int = Field(default=24, description="Character age (default mid-20s per Directive 12)")
    gender: str = Field(default="female", description="'male' or 'female'")
    body_composition: str = Field(default="medium_fit", description="'skinny', 'medium_fit', 'athletic_strong', 'curvy_healthy', 'chubby'")
    height: str = Field(default="medium", description="'short', 'medium', 'tall'")
    role: str = Field(default="heroine", description="'hero', 'heroine', 'supporting', 'troupe'")
    relationship: str = Field(default="lead", description="'lover', 'friend', 'mom', 'dad', 'son', 'daughter', 'teacher', 'uncle', 'lead'")
    appearance_summary: str = Field(default="", description="Visual prompt describing physical appearance, attire, and features")


class ScenePlanItem(BaseModel):
    """Structured scene storyboard specification."""

    scene_index: int
    duration_seconds: float = Field(default=4.0, ge=2.0, le=10.0)
    shot_type: str = Field(default="medium", description="close_up, wide, medium, over_shoulder")
    visual_prompt: str = Field(description="4K Photoreal diffusion prompt for Flux Schnell")
    dialogue: str = Field(description="Spoken narration line for Azure Speech HD")


class ScriptOutput(BaseModel):
    """Structured 8-12 minute video script and storyboard."""

    title: str
    hook_thesis: str
    characters: list[CharacterMetadata] = Field(default_factory=list, description="List of characters in the production")
    scenes: list[ScenePlanItem]
    target_duration_seconds: int = 480
    recommended_fps: int = Field(default=30, description="24 for film drama, 30 for dance/music, 60 for walking/action")
    audio_sample_rate_hz: int = Field(default=48000, description="Broadcast audio sample rate: 48000 Hz 24-bit")
    vocal_gender: str = Field(default="female", description="'female', 'male', 'duet', 'background_chorus', or 'instrumental'")
    vocal_delivery_type: str = Field(default="lead_lip_sync", description="'lead_lip_sync', 'background_song', 'voiceover_narration', or 'instrumental_only'")


class GeminiLLMAdapter(LLMProviderProtocol):
    """Tier-2 Flagship LLM Adapter powered by Gemini 1.5 Pro via non-blocking Async HTTP."""

    def __init__(self, api_key: str | None = None, strict: bool = False):
        self.api_key = api_key or settings.llm.google_api_key or settings.llm.gemini_api_key or None
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"
        self.strict = strict

    async def generate_text(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate unstructured retention narrative text."""
        if is_mock_mode():
            return f"[Generated Script] Topic: {prompt[:80]} | Retention Hook: Did you know this changed everything?"

        client = HTTPClientPool.get_client()
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key} if self.api_key else {}

        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            resp = await client.post(self.base_url, headers=headers, params=params, json=body, timeout=45.0)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            if resp.status_code == 429:
                err_msg = "Google AI Studio prepayment credits depleted (HTTP 429 RESOURCE_EXHAUSTED)."
                logger.warning(f"gemini_api_quota_exhausted: {err_msg}")
                if self.strict:
                    raise RuntimeError(f"Production Halted: {err_msg} Please top up credits at https://ai.studio/projects")
            else:
                logger.warning(f"gemini_api_call_non_200: status={resp.status_code}, body={resp.text[:180]}.")
                if self.strict:
                    raise RuntimeError(f"Production Halted: Gemini returned HTTP {resp.status_code}: {resp.text[:180]}")
        except Exception as ex:
            if self.strict:
                raise
            logger.warning(f"gemini_api_call_skipped: {ex}. Using deterministic local synthesis fallback.")

        # Deterministic offline fallback for tests or missing API keys
        return f"[Generated Script] Topic: {prompt[:80]} | Retention Hook: Did you know this changed everything?"

    def _build_storyboard_for_prompt(self, prompt: str) -> dict[str, Any]:
        """Build topic-accurate storyboard plan adhering to ScenePlan contracts."""
        from src.providers.llm.mock_storyboards import resolve_mock_storyboard
        return resolve_mock_storyboard(prompt)

    async def generate_structured(self, prompt: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate structured JSON scene plan obeying Pydantic storyboard contracts."""
        fallback_plan = self._build_storyboard_for_prompt(prompt)

        if is_mock_mode():
            return fallback_plan

        sys_prompt = "You are a broadcast video director. Return ONLY valid JSON adhering to the ScenePlan specification."
        raw = await self.generate_text(prompt, system_prompt=sys_prompt)


        # Clean markdown codeblocks if model returned ```json ... ```
        clean_json = raw.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.split("\n", 1)[-1]
            if clean_json.endswith("```"):
                clean_json = clean_json.rsplit("\n", 1)[0]

        try:
            parsed = json.loads(clean_json)
            if isinstance(parsed, list):
                return {"scenes": parsed}
            return parsed
        except Exception as ex:
            if self.strict:
                raise RuntimeError(f"Production Halted: Gemini returned invalid JSON ({ex}). Fallbacks disabled.")
            return fallback_plan


__all__ = ["GeminiLLMAdapter", "ScenePlanItem", "ScriptOutput"]

