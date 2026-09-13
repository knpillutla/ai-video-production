"""Metadata-Driven AI Production Stack Resolver for the Model Selector MCP Server."""

from typing import Any
from pydantic import BaseModel, Field
from src.core.telemetry import logger
from src.mcp.model_selector.cultural_catalog import (
    lookup_costume_stack,
    lookup_cultural_stack,
    lookup_dance_stack,
    lookup_art_style,
)
from src.services.cultural_derivation import derive_cultural_context


class ScriptMetadata(BaseModel):
    """Metadata parameters describing creative vision, format, and styling."""

    title: str = ""
    genre: str = "comedy"
    language: str = "en"
    visual_style: str = Field(default="realistic", description="realistic, anime, cartoon, 3d, comic")
    art_style: str = Field(default="photorealistic_cinematic", description="Global art style or aesthetic")
    video_format: str = Field(default="faceless", description="faceless, talking_head, dance_video, cinematic, podcast, travel_guide, vlog, web_series")
    culture: str = Field(default="", description="indian_south, indian_north, east_asian, western_global")
    ethnicity: str = Field(default="", description="south_asian, east_asian, caucasian")
    dance_type: str = Field(default="", description="indian_classical, indian_folk_mass, contemporary")
    costume_style: str = Field(default="", description="indian_traditional_saree, indian_royal_sherwani, indian_traditional_dhoti")
    user_home_country: str = Field(default="", description="User home country: in, india, us, jp, etc.")
    user_cultural_heritage: str = Field(default="", description="User heritage: indian_south, indian_north, etc.")
    character_name: str = ""
    has_character: bool = False
    has_lipsync: bool = False
    has_dance: bool = False
    audio_type: str = Field(default="instrumental_bgm", description="instrumental_bgm, vocal_song, dialogue_only")
    budget_tier: str = "balanced"


def resolve_production_stack(metadata: dict[str, Any]) -> dict[str, Any]:
    """Dynamically resolve the optimal AI model for every pipeline stage based on script metadata."""
    meta = ScriptMetadata(**metadata) if not isinstance(metadata, ScriptMetadata) else metadata
    v_style = meta.visual_style.lower()
    v_format = meta.video_format.lower()
    lang = meta.language.lower()

    # 1. Visual Model & Global Art Style Selection
    art_info = lookup_art_style(meta.art_style or v_style, country=meta.user_home_country)
    if "anime" in v_style or "manga" in v_style:
        visual = {
            "model": "animagine-xl-3.1",
            "provider": "Fal.ai",
            "unit_cost_usd": 0.0040,
            "unit_name": "image",
            "reasoning": "Selected Animagine XL 3.1 for authentic cel-shaded anime aesthetic, vibrant line-art, and expressive character design.",
        }
    elif "cartoon" in v_style or "3d" in v_style or "pixar" in v_style:
        visual = {
            "model": "sdxl-turbo-pixar-3d",
            "provider": "Stability",
            "unit_cost_usd": 0.0035,
            "unit_name": "image",
            "reasoning": "Selected 3D Stylized Pixar/Disney diffusion model for exaggerated cartoon proportions and studio lighting.",
        }
    elif "comic" in v_style:
        visual = {
            "model": "sd-comicbook-lora",
            "provider": "TogetherAI",
            "unit_cost_usd": 0.0030,
            "unit_name": "image",
            "reasoning": "Selected Graphic Novel & Comic Book diffusion model with halftone ink shading and dramatic framing.",
        }
    elif art_info.get("display_name") != "Broadcast 4K Photorealistic Cinematic":
        visual = {
            "model": art_info.get("recommended_diffusion_model", "flux-1-dev"),
            "provider": "TogetherAI",
            "unit_cost_usd": 0.0030,
            "unit_name": "image",
            "art_style": art_info["display_name"],
            "reasoning": f"Selected {art_info['display_name']} ({art_info['origin_country']}) with authentic lighting and palette.",
        }
    else:  # Default Realistic
        visual = {
            "model": "flux-1-schnell",
            "provider": "TogetherAI",
            "unit_cost_usd": 0.0030,
            "unit_name": "image",
            "reasoning": "Selected Together AI FLUX.1-schnell for sub-second 4K cinematic photorealism and typographic prompt fidelity at $0.003/image.",
        }

    # 2. Character Animation, Motion & Dance Model Selection
    if meta.has_dance or "dance" in v_format:
        motion = {
            "model": "mimic-motion",
            "provider": "Fal.ai",
            "unit_cost_usd": 0.0400,
            "unit_name": "second",
            "animation_type": "full_body_dance",
            "reasoning": "Dance video detected: Selected Fal.ai MimicMotion for audio-driven full-body pose transfer and synchronized hook steps.",
        }
    elif meta.has_lipsync or "talking_head" in v_format:
        motion = {
            "model": "live-portrait",
            "provider": "Fal.ai",
            "unit_cost_usd": 0.0120,
            "unit_name": "second",
            "animation_type": "facial_lipsync",
            "reasoning": "Talking-head format: Selected Fal.ai LivePortrait for sub-millimeter facial landmark tracking and expressive phoneme audio lip-sync.",
        }
    elif "travel" in v_format or "vlog" in v_format or any(k in v_format for k in ("scenic", "walk", "relaxation", "drive", "lounge", "nature")):
        motion = {
            "model": "camera-pan-zoom-2.5d",
            "provider": "LocalFFmpeg",
            "unit_cost_usd": 0.0000,
            "unit_name": "second",
            "animation_type": "aerial_drone_pan_zoom",
            "reasoning": "Scenic Relaxation / Travel / Walking Tour format: Selected 2.5D optical drone pan-zoom and landmark parallax on CPU ($0.00).",
        }
    else:  # Faceless / B-Roll / Documentary
        motion = {
            "model": "camera-pan-zoom-2.5d",
            "provider": "LocalFFmpeg",
            "unit_cost_usd": 0.0000,
            "unit_name": "second",
            "animation_type": "optical_parallax",
            "reasoning": "Faceless video format: Selected Local FFmpeg 2.5D optical pan-zoom on CPU. Zero GPU overhead, zero compute cost ($0.00).",
        }

    # 3. Cultural Derivation Engine (User Home Country or Script)
    derived = derive_cultural_context(
        script_text=f"{meta.title} {meta.genre}",
        user_home_country=meta.user_home_country or None,
        user_cultural_heritage=meta.user_cultural_heritage or meta.culture or None,
        language=lang,
        genre=meta.genre,
        video_format=meta.video_format,
        art_style=meta.art_style,
    )
    effective_culture = meta.culture or derived.culture
    effective_ethnicity = meta.ethnicity or derived.ethnicity
    effective_costume = meta.costume_style or derived.clothing_style
    cult_stack = lookup_cultural_stack(culture=effective_culture, language=lang)

    # 4. Voiceover & Speech Synthesis Model Selection (Culturally Adapted)
    if "anime" in v_style and meta.has_character:
        voice = {
            "model": "eleven-multilingual-v2",
            "provider": "ElevenLabs",
            "unit_cost_usd": 0.000030,
            "unit_name": "character",
            "voice_id": derived.voice_id,
            "reasoning": "Character-driven anime/cartoon format: Selected ElevenLabs acting voice.",
        }
    else:
        voice = {
            "model": derived.voice_id,
            "provider": derived.voice_provider,
            "unit_cost_usd": 0.000016,
            "unit_name": "character",
            "voice_id": derived.voice_id,
            "reasoning": f"Culturally adapted voice ({derived.culture_name}): Selected {derived.voice_id} ({derived.derivation_source}).",
        }

    # 5. Music, Soundtrack & Songs Model Selection (Culturally Adapted)
    if meta.audio_type == "vocal_song" or meta.has_dance or "dance" in v_format:
        music = {
            "model": "suno-v3.5-vocal-pro",
            "provider": "Suno",
            "unit_cost_usd": 0.0800,
            "unit_name": "track",
            "music_type": "full_lyrical_song",
            "style": derived.music_style,
            "reasoning": f"Musical / Dance format: Suno v3.5 Vocal Engine styled to {derived.music_style}.",
        }
    else:
        music = {
            "model": "suno-v3.5-instrumental",
            "provider": "Suno / LocalDSP",
            "unit_cost_usd": 0.0800,
            "unit_name": "track",
            "music_type": "instrumental_bgm",
            "style": derived.music_style,
            "reasoning": f"Culturally matched soundtrack: {derived.music_style} ({derived.culture_name}).",
        }

    # 6. Creative Scriptwriting Model
    script = {
        "model": "gemini-1.5-pro",
        "provider": "Google",
        "unit_cost_usd": 0.00000125,
        "unit_name": "token",
        "reasoning": f"Selected Gemini 1.5 Pro for nuanced cultural storytelling in {derived.culture_name} ({lang.upper()}) with 2M token retention.",
    }

    # 7. Dance & LoRA Resolution
    dance_style = meta.dance_type or ("indian_classical" if "indian" in effective_culture else "contemporary")
    dance_stack = lookup_dance_stack(dance_style) if (meta.dance_type or meta.has_dance or "dance" in v_format) else None
    active_loras: list[dict[str, Any]] = list(derived.recommended_loras)
    if art_info.get("recommended_lora"):
        r_lora = art_info["recommended_lora"]
        if not any(al.get("path") == r_lora.get("path") for al in active_loras):
            active_loras.append(r_lora)
    if dance_stack and "lora_modifiers" in dance_stack:
        for lm in dance_stack["lora_modifiers"]:
            if not any(al.get("name") == lm for al in active_loras):
                active_loras.append({"name": lm, "weight": 0.85})

    if dance_stack:
        m_raw = dance_stack.get("motion_model", "mimic-motion")
        if isinstance(m_raw, dict):
            m_name = m_raw.get("model", "mimic-motion")
            m_prov = m_raw.get("provider", "Fal.ai")
            m_anim = m_raw.get("type", "full_body_dance")
            m_reas = m_raw.get("reasoning", dance_stack.get("reasoning", ""))
        else:
            m_name = "mimic-motion" if "mimic" in str(m_raw) else str(m_raw)
            m_prov = dance_stack.get("motion_provider", "Fal.ai")
            m_anim = "full_body_dance"
            m_reas = dance_stack.get("reasoning", "Dance motion pose transfer")

        motion = {
            "model": m_name,
            "provider": m_prov,
            "unit_cost_usd": 0.0400,
            "unit_name": "second",
            "animation_type": m_anim,
            "reasoning": f"Dance mode ({dance_stack['dance_name']}): {m_reas}",
        }

    cultural_routing = {
        "culture": cult_stack["culture_name"],
        "primary_ethnicity": effective_ethnicity,
        "prompt_anchors": cult_stack["visual_diffusion"].get("prompt_anchors", ""),
        "anti_whitewashing_guard": True,
        "clothing_style": effective_costume,
        "outfit_description": derived.outfit_description,
        "jewelry_description": derived.jewelry_description,
        "derivation_source": derived.derivation_source,
        "confidence_score": derived.confidence_score,
    }

    stack = {
        "metadata_evaluated": meta.model_dump(),
        "scriptwriting": script,
        "visual_diffusion": visual,
        "art_style": art_info,
        "motion_animation": motion,
        "voiceover_tts": voice,
        "soundtrack_music": music,
        "sfx_audio": {
            "model": "audioldm-2" if (meta.has_dance or dance_stack) else "librosa-foley",
            "provider": "Fal.ai" if (meta.has_dance or dance_stack) else "LocalDSP",
            "unit_cost_usd": 0.0050 if (meta.has_dance or dance_stack) else 0.0,
            "unit_name": "clip",
            "sfx_style": derived.sfx_style,
            "reasoning": f"{derived.sfx_style} matched to visual action.",
        },
        "cultural_routing": cultural_routing,
        "recommended_loras": active_loras,
        "character_consistency": {
            "enabled": meta.has_character or bool(meta.character_name),
            "character_name": meta.character_name or "Ananya",
            "visual_anchor": cultural_routing["prompt_anchors"],
            "costume_anchor": derived.outfit_description,
            "jewelry_anchor": derived.jewelry_description,
            "active_loras_count": len(active_loras),
        },
    }
    logger.info(
        f"production_stack_resolved: format={v_format}, style={v_style}, visual_model={visual['model']}, "
        f"motion_model={motion['model']}, music={music['music_type']}, loras={len(active_loras)}"
    )
    return stack


__all__ = ["ScriptMetadata", "resolve_production_stack"]
