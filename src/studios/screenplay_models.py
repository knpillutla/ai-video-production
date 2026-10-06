"""Universal Screenplay and Storyboard Models for Studio Productions.

Self-contained contract for living wallpapers, soundscapes, and cinematic scenes.
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
    unidirectional_flow: bool = True
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


class RelaxSceneDirective(BaseModel):
    """Single Scene / Shot Directorial Specification for Living Wallpapers."""
    scene_index: int = 1
    location_hub: str = "Scenic Vista"
    shot_type: str = "wide_panoramic_picturesque"
    camera_rig: str = "locked_tripod"
    color_temp_kelvin: Optional[int] = None
    visual_prompt: str = Field(..., description="Photorealistic living wallpaper prompt")
    motion_prompt: str = Field(..., description="Video diffusion prompt with locked tripod and fluid vector alignment")
    motion_negative_prompt: Optional[str] = Field(None, description="Director-specified negative constraints")
    model_configs: Dict[str, RelaxModelConfigDirective] = Field(default_factory=dict)
    image_model_configs: Dict[str, Any] = Field(default_factory=dict)
    domain: str = "landscape_solid"
    motion_type: str = "ai_diffusion"
    camera_movement: str = "slow_zoom_in"
    motion_rationale: Optional[str] = None
    duration_seconds: float = 30.0
    narration_text: Optional[str] = None
    camera_waypoints: List[CameraWaypointDirective] = Field(default_factory=list)
    kinetic_micro_zones: Optional[KineticMicroSpec] = None


class KineticSpriteSpec(BaseModel):
    """Moving sprite specification (car, pedestrian, boat, animal) for wide shots."""
    label: str = "moving_object"
    bbox: List[float] = Field(default_factory=list)
    delta_pct: List[float] = Field(default_factory=lambda: [0.03, 0.0])
    bobbing: bool = False


class KineticMicroSpec(BaseModel):
    """Tier-0 micro-kinetic zones for wide architectural & landscape shots."""
    sprites: List[KineticSpriteSpec] = Field(default_factory=list)
    tree_sway_zones: List[List[float]] = Field(default_factory=list)
    water_zones: List[List[float]] = Field(default_factory=list)
    celestial_zone: Optional[Dict[str, Any]] = None


class CameraWaypointDirective(BaseModel):
    """Single timed camera kinetic waypoint for multi-phase drone choreography."""
    motion: str = "slow_drone_forward"
    duration_seconds: float = 5.0


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


class RelaxScreenplay(BaseModel):
    """Dedicated Directorial Screenplay Schema for Studio Productions."""
    production_id: str = Field(default="EP-001", validation_alias=AliasChoices("production_id", "episode_id", "id"))
    title: str = Field(default="Natural Sanctuary Soundscape", validation_alias=AliasChoices("title", "production_title", "video_title"))
    story_topic: str = Field(default="Scenic living wallpaper sanctuary", validation_alias=AliasChoices("story_topic", "synopsis", "story_synopsis", "description"))
    genre: str = "relax/nature"
    sub_genre: Optional[str] = "waterfall_gorge"
    primary_archetype: Optional[str] = None
    secondary_archetype: Optional[str] = None
    cluster: Optional[str] = None
    primary_language: str = "en"
    target_dubbing_languages: List[str] = Field(default_factory=lambda: ["en", "de", "fr", "ja", "es"])
    recommended_fps: int = 24
    aspect_ratio: str = "16:9"
    total_duration_seconds: float = 60.0
    tier: str = Field(default="balanced", validation_alias=AliasChoices("tier", "motion_tier"))
    
    global_culture: Optional[RelaxGlobalCultureSpec] = None
    travel_tourism: Optional[RelaxTravelTourismSpec] = None
    cast: List[Any] = Field(default_factory=list)
    audio_master: RelaxAudioMasterSpec = Field(default_factory=RelaxAudioMasterSpec)
    scenes: List[RelaxSceneDirective] = Field(default_factory=list)
    publishing: Optional[RelaxPublishingPackage] = None

    @field_validator("audio_master", mode="before")
    @classmethod
    def coerce_audio_master(cls, v: Any) -> Any:
        if isinstance(v, str):
            return RelaxAudioMasterSpec(suno_musical_tags=v)
        return v or RelaxAudioMasterSpec()


class AmbientScenePrompt(BaseModel):
    """Scene prompt specification for backward-compatible pipeline execution."""
    scene_index: int = 1
    perspective_type: str = "wide_panoramic"
    visual_prompt: str = ""
    motion_prompt: str = ""
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    motion_type: str = "ai_diffusion"
    camera_movement: str = "slow_zoom_in"
    motion_rationale: Optional[str] = None
    image_model_configs: dict = Field(default_factory=dict)
    model_configs: dict = Field(default_factory=dict)


class AmbientStoryboard(BaseModel):
    """Directorial storyboard representation."""
    title: str = "Studio Production"
    story_topic: Optional[str] = ""
    primary_archetype: str = "waterfall"
    secondary_archetype: Optional[str] = None
    cluster: str = "waterfall"
    tier: str = "balanced"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str = ""
    spoken_narration_script: Optional[str] = ""
    scenes: List[AmbientScenePrompt] = Field(default_factory=list)

    @field_validator("audio_tags", mode="before")
    @classmethod
    def normalize_audio_tags(cls, v: Any) -> str:
        return normalize_audio_tags(v)


def relax_to_ambient_storyboard(sp: RelaxScreenplay) -> AmbientStoryboard:
    """Convert RelaxScreenplay to AmbientStoryboard representation."""
    scenes = []
    for idx, s in enumerate(sp.scenes, 1):
        scenes.append(
            AmbientScenePrompt(
                scene_index=idx,
                perspective_type=s.shot_type,
                visual_prompt=s.visual_prompt,
                motion_prompt=s.motion_prompt,
                duration_seconds=s.duration_seconds,
                domain=s.domain,
                motion_type=getattr(s, "motion_type", "ai_diffusion"),
                camera_movement=getattr(s, "camera_movement", "slow_zoom_in"),
                motion_rationale=getattr(s, "motion_rationale", None),
                image_model_configs=s.image_model_configs,
                model_configs={k: v.model_dump() for k, v in s.model_configs.items()} if s.model_configs else {},
            )
        )
    return AmbientStoryboard(
        title=sp.title,
        story_topic=sp.story_topic,
        primary_archetype=sp.sub_genre or sp.primary_archetype or "waterfall",
        cluster="waterfall",
        tier=sp.tier or "balanced",
        total_duration=sp.total_duration_seconds or sum(s.duration_seconds for s in sp.scenes) or 60.0,
        recommended_fps=sp.recommended_fps or 24,
        audio_tags=sp.audio_master.suno_musical_tags if sp.audio_master else "",
        spoken_narration_script=getattr(sp.audio_master, "spoken_narration_script", "") if sp.audio_master else "",
        scenes=scenes,
    )
