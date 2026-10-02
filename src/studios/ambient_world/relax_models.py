"""Dedicated Relaxation & Living Wallpaper Genre Schema.

Self-contained contract for pure nature soundscapes, cozy living spaces,
ocean havens, and zen relaxation living wallpapers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field, field_validator
from src.services.audio_tag_service import normalize_audio_tags


class LoopStrategySpec(BaseModel):
    """Loop and crossfade specifications for living wallpapers."""
    target_clip_duration_seconds: float = 30.0
    generation_segment_seconds: float = 5.0
    continuity_mode: str = "cyclic_temporal_flow"
    seam_strategy: str = "forward_phase_aligned_crossfade"
    unidirectional_flow: bool = True  # Prevents water from reversing
    crossfade_seconds: float = 1.2
    loop_validation: bool = True


class RelaxModelPromptsSpec(BaseModel):
    """Model-specific positive and negative prompt pair."""
    positive_prompt: str = ""
    negative_prompt: Optional[str] = ""


class RelaxModelConfigDirective(BaseModel):
    """Model-specific execution configuration and parameters."""
    model: str = ""
    prompts: RelaxModelPromptsSpec = Field(default_factory=RelaxModelPromptsSpec)
    settings: Dict[str, Any] = Field(default_factory=dict)


class RelaxTravelTourismSpec(BaseModel):
    """Geospatial and natural landmark discovery specification."""
    destination_name: str = "Natural Landmark"
    country: str = "Natural Sanctuary"
    province_state: Optional[str] = None
    attraction_type: str = "Natural Sanctuary"
    best_season_and_lighting: Optional[str] = None


class RelaxGlobalCultureSpec(BaseModel):
    """Architectural materials and cultural atmosphere specification."""
    continent_region: str = "Global Wilderness"
    culture_heritage: str = "Natural Heritage"
    authentic_textiles_and_fabrics: str = "Weathered timber, slate, stone"
    cultural_gestures_and_rituals: str = "Tranquil mindful contemplation"


class RelaxAudioMasterSpec(BaseModel):
    """Audio and acoustic foley specification for relaxation."""
    audio_mode: str = "ambient_nature"
    spoken_narration_script: Optional[str] = ""
    singing_lyrics_spec: Optional[str] = ""
    suno_musical_tags: str = "432Hz ambient, natural foley, soft acoustic drone, stereo spatial acoustics, -14 LUFS"
    vocal_gender: str = "female"
    tempo_bpm: int = 64
    speech_cadence_wpm: int = 125
    traditional_instruments: List[str] = Field(default_factory=list)
    target_lufs: float = -14.0
    ducking_db: float = -18.0

    @field_validator("suno_musical_tags", mode="before")
    @classmethod
    def coerce_suno_musical_tags(cls, value: Any) -> str:
        return normalize_audio_tags(value)


class RelaxSceneDirective(BaseModel):
    """Single Scene / Shot Directorial Specification for Living Wallpapers."""
    scene_index: int = 1
    location_hub: str = "Scenic Vista"
    shot_type: str = "wide_panoramic_picturesque"
    camera_rig: str = "locked_tripod"
    color_temp_kelvin: Optional[int] = None  # Autonomously determined by director
    visual_prompt: str = Field(..., description="Photorealistic living wallpaper prompt")
    motion_prompt: str = Field(..., description="Video diffusion prompt with locked tripod and fluid vector alignment")
    motion_negative_prompt: Optional[str] = Field(None, description="Director-specified negative constraints")
    model_configs: Dict[str, RelaxModelConfigDirective] = Field(default_factory=dict)
    image_model_configs: Dict[str, Any] = Field(default_factory=dict)
    loop_strategy: Optional[LoopStrategySpec] = None
    domain: str = "landscape_solid"  # landscape_solid, water_fluid
    duration_seconds: float = 30.0


class RelaxPublishingPackage(BaseModel):
    """YouTube Publishing & SEO Metadata for Relaxation Living Wallpapers."""
    ctr_titles: List[str] = Field(default_factory=list, validation_alias=AliasChoices("ctr_titles", "seo_titles", "titles"))
    description_with_timestamps: str = Field(default="", validation_alias=AliasChoices("description_with_timestamps", "seo_description", "description"))
    seo_tags: List[str] = Field(default_factory=list, validation_alias=AliasChoices("seo_tags", "tags"))
    has_synthetic_media: bool = True
    ypp_monetization_safety: str = "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)"
    thumbnail_concept_prompts: List[str] = Field(default_factory=list, validation_alias=AliasChoices("thumbnail_concept_prompts", "thumbnail_prompts"))

    @field_validator("thumbnail_concept_prompts", mode="before")
    @classmethod
    def coerce_thumbnails(cls, v: Any) -> List[str]:
        if isinstance(v, dict):
            return [str(val) for val in v.values() if val]
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(item) for item in v if item]
        return []


from pydantic import AliasChoices, BaseModel, Field, field_validator


class RelaxScreenplay(BaseModel):
    """Dedicated Directorial Screenplay Schema for Relaxation & Living Wallpapers."""
    production_id: str = Field(default="EP-001", validation_alias=AliasChoices("production_id", "episode_id", "id"))
    title: str = Field(default="Natural Sanctuary Soundscape", validation_alias=AliasChoices("title", "production_title", "video_title"))
    story_topic: str = Field(default="Scenic living wallpaper sanctuary", validation_alias=AliasChoices("story_topic", "synopsis", "story_synopsis", "description"))
    genre: str = "relax/nature"
    sub_genre: Optional[str] = "nature_sanctuary"
    primary_archetype: Optional[str] = None
    secondary_archetype: Optional[str] = None
    cluster: Optional[str] = None
    primary_language: str = "en"
    target_dubbing_languages: List[str] = Field(default_factory=lambda: ["en", "de", "fr", "ja", "es"])
    recommended_fps: int = 24
    aspect_ratio: str = "16:9"
    total_duration_seconds: float = 60.0
    
    global_culture: Optional[RelaxGlobalCultureSpec] = None
    travel_tourism: Optional[RelaxTravelTourismSpec] = None
    cast: List[Any] = Field(default_factory=list)  # Strictly empty for pure nature
    audio_master: RelaxAudioMasterSpec = Field(default_factory=RelaxAudioMasterSpec)
    scenes: List[RelaxSceneDirective] = Field(default_factory=list)
    publishing: Optional[RelaxPublishingPackage] = None

    @field_validator("audio_master", mode="before")
    @classmethod
    def coerce_audio_master(cls, v: Any) -> Any:
        if isinstance(v, str):
            return RelaxAudioMasterSpec(suno_musical_tags=v)
        return v or RelaxAudioMasterSpec()
