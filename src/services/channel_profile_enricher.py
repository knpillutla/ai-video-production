"""AI Channel Profile Directorial Synthesizer via Gemini LLM.

Takes channel name, handle, selected genres, and user intent, and autonomously
generates a comprehensive ChannelProfile with audio policies, lighting rules,
Suno tag templates, and YouTube SEO defaults.
"""

from __future__ import annotations
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from src.config.channel_registry import ChannelProfile
from src.providers.llm.gemini_adapter import GeminiLLMAdapter

logger = logging.getLogger("ChannelProfileEnricher")


class ChannelEnrichRequest(BaseModel):
    channel_name: str
    handle: str
    allowed_genres: List[str] = Field(default_factory=list)
    user_intent: str = ""
    channel_slug: Optional[str] = None


async def enrich_channel_profile_with_gemini(
    req: ChannelEnrichRequest,
) -> ChannelProfile:
    """Prompt Gemini to synthesize a complete ChannelProfile JSON schema."""
    slug = (
        req.channel_slug
        or req.channel_name.lower().replace(" ", "_").replace("-", "_")
    )
    handle = req.handle if req.handle.startswith("@") else f"@{req.handle}"

    prompt = f"""You are the Chief YouTube Channel Strategist and Master Visual Director for an automated broadcast studio.
Your task is to synthesize a complete, production-ready Channel Profile for a new channel with strict directorial guardrails.

USER SPECIFICATIONS:
- Channel Name: "{req.channel_name}"
- YouTube Handle: "{handle}"
- Channel Slug / ID: "{slug}"
- Allowed Genres / Categories: {json.dumps(req.allowed_genres)}
- User Vision & Intent: "{req.user_intent or 'Autonomously derive optimal high-retention relaxing and ambient visual channel strategy.'}"

DIRECTORIAL SYNTHESIS RULES:
1. TARGET AUDIENCE & TAG: Clearly define the viewer psychological state and a punchy 2-4 word display tag with emoji (e.g. '🌿 432Hz Nature & Meditation' or '🔥 Pure ASMR Sleep').
2. AUDIO POLICY:
   - Determine if BGM should be enabled by default (True for music/melodic/relaxation, False for pure nature/sleep ASMR/rain/hearth).
   - Define exact instruments, foley elements, target integrated loudness (-14.0 LUFS for music, -16.0 LUFS for ASMR/sleep), ducking dB (-18.0 to -22.0 dB).
   - Create an optimized Suno prompt tag template.
3. VISUAL & LIGHTING GUARDRAILS:
   - Specify optimal color temperature (e.g. 5400K-5600K daylight vs 1800K-2400K amber hearth glow).
   - Strict negative visual constraints (e.g. no modern clutter, no tourists, no harsh lighting).
   - Purity and composition rule.
4. YOUTUBE SEO:
   - Provide 6-8 high-volume, low-competition primary algorithmic tags.
   - YouTube Category ID (e.g. "10" for Music/Relaxation, "28" for Science, "23" for Comedy, "24" for Entertainment).

CRITICAL: Return ONLY a valid JSON object matching this exact schema:
{{
  "channel_id": "{slug}",
  "channel_name": "{req.channel_name}",
  "handle": "{handle}",
  "tag": "Emoji + short punchy 2-4 word display badge",
  "comments": "Internal strategy guidelines and notes",
  "niche_category": "Short concise niche headline",
  "target_audience": "Detailed viewer persona and viewing session intent",
  "allowed_genres": {json.dumps(req.allowed_genres)},
  "audio_profile": {{
    "bgm_enabled_by_default": true,
    "style": "Acoustic style description",
    "instruments": ["instrument 1", "instrument 2"],
    "foley_elements": ["foley 1", "foley 2"],
    "target_lufs": -14.0,
    "bgm_ducking_db": -18.0,
    "suno_tag_template": "Suno tags string"
  }},
  "visual_lighting_guardrails": {{
    "lighting_temperature": "Lighting description with Kelvin range",
    "negative_visual_tokens": "comma-separated negative tokens",
    "purity_rule": "Composition and scene purity rule"
  }},
  "youtube_seo_defaults": {{
    "primary_tags": ["Tag 1", "Tag 2", "Tag 3"],
    "category_id": "10"
  }}
}}
"""

    llm = GeminiLLMAdapter(strict=True)
    logger.info(
        f"enriching_channel_profile_via_gemini: name='{req.channel_name}' slug='{slug}'"
    )
    raw_data = await llm.generate_structured(prompt)

    if not isinstance(raw_data, dict):
        raise ValueError("Gemini returned invalid non-dict response.")

    profile = ChannelProfile.model_validate(raw_data)
    return profile
