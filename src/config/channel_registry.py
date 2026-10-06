"""Channel Profile Registry and Directorial Guardrails Loader.

Loads modular per-channel definitions from src/config/channels/<channel_id>.json.
Provides strongly-typed schemas, prompt injection blocks, and save operations.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("ChannelRegistry")

CHANNELS_DIR = Path(__file__).resolve().parent / "channels"


class AudioProfile(BaseModel):
    bgm_enabled_by_default: bool = True
    style: str = "Harmonic soundscape"
    instruments: List[str] = Field(default_factory=list)
    foley_elements: List[str] = Field(default_factory=list)
    target_lufs: float = -14.0
    bgm_ducking_db: float = -18.0
    suno_tag_template: str = ""


class VisualLightingGuardrails(BaseModel):
    lighting_temperature: str = "Natural daylight"
    negative_visual_tokens: str = "modern clutter, blurry optics"
    purity_rule: str = "Pure pristine nature, zero clutter"


class YouTubeSEODefaults(BaseModel):
    primary_tags: List[str] = Field(default_factory=list)
    category_id: str = "10"


class ChannelProfile(BaseModel):
    channel_id: str
    channel_name: str
    handle: str
    niche_category: str
    target_audience: str
    tag: str = ""
    comments: str = ""
    allowed_genres: List[str] = Field(default_factory=list)
    audio_profile: AudioProfile = Field(default_factory=AudioProfile)
    visual_lighting_guardrails: VisualLightingGuardrails = Field(
        default_factory=VisualLightingGuardrails
    )
    youtube_seo_defaults: YouTubeSEODefaults = Field(default_factory=YouTubeSEODefaults)

    def format_directorial_guardrails_block(self) -> str:
        """Build formatted directorial guardrails text to inject into Gemini prompt."""
        bgm_str = (
            "ENABLED"
            if self.audio_profile.bgm_enabled_by_default
            else "DISABLED (Pure Natural Foley / ASMR)"
        )
        tags_str = ", ".join(self.youtube_seo_defaults.primary_tags[:6])
        return f"""======================================================================
ACTIVE CHANNEL BRANDING & AUDIENCE GUARDRAILS ({self.handle} - {self.channel_name}):
======================================================================
- Niche Category: {self.niche_category}
- Target Audience Intent: {self.target_audience}
- Acoustic Directorial Policy: {self.audio_profile.style}
  * Default BGM: {bgm_str}
  * Target Integrated Loudness: {self.audio_profile.target_lufs} LUFS
  * Recommended Suno Tags: {self.audio_profile.suno_tag_template}
- Visual & Lighting Guardrails:
  * Lighting Standard: {self.visual_lighting_guardrails.lighting_temperature}
  * Negative Visual Constraints: {self.visual_lighting_guardrails.negative_visual_tokens}
  * Purity & Composition Rule: {self.visual_lighting_guardrails.purity_rule}
- Algorithmic SEO Focus Tags: {tags_str}
"""


_CACHE: Optional[Dict[str, ChannelProfile]] = None


def load_channel_profiles(force_reload: bool = False, user_email: str = "knpillutla@gmail.com") -> Dict[str, ChannelProfile]:
    """Load and parse all per-channel JSON files from user storage directory."""
    global _CACHE
    if _CACHE is not None and not force_reload:
        return _CACHE

    profiles: Dict[str, ChannelProfile] = {}
    from src.core.storage import storage_service
    user_chan_dir = storage_service.get_user_container_path(user_email) / "channels"
    if user_chan_dir.exists():
        for prof_file in user_chan_dir.glob("*/channel_profile.json"):
            try:
                data = json.loads(prof_file.read_text(encoding="utf-8"))
                profile = ChannelProfile(**data)
                profiles[profile.channel_id.lower()] = profile
            except Exception as exc:
                logger.warning(f"Failed to load channel profile {prof_file}: {exc}")

    if not profiles and CHANNELS_DIR.exists():
        for json_file in CHANNELS_DIR.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                profile = ChannelProfile(**data)
                profiles[profile.channel_id.lower()] = profile
            except Exception:
                pass

    _CACHE = profiles
    return _CACHE


def get_channel_profile(channel_id: Optional[str], user_email: str = "knpillutla@gmail.com") -> Optional[ChannelProfile]:
    """Retrieve profile for a specific channel slug or return default."""
    if not channel_id:
        return None
    profiles = load_channel_profiles(user_email=user_email)
    slug = channel_id.lower().strip()
    return profiles.get(slug)


def save_channel_profile(profile: ChannelProfile, user_email: str = "knpillutla@gmail.com") -> Path:
    """Save or update an individual channel profile JSON file in user storage."""
    from src.core.storage import storage_service
    user_chan_dir = storage_service.get_user_container_path(user_email) / "channels" / profile.channel_id.lower().strip()
    user_chan_dir.mkdir(parents=True, exist_ok=True)
    target_file = user_chan_dir / "channel_profile.json"
    target_file.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    load_channel_profiles(force_reload=True, user_email=user_email)
    logger.info(f"Saved channel profile: {target_file}")
    return target_file
