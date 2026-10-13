"""Universal Screenplay and Storyboard Models for Studio Productions.

Self-contained contract for living wallpapers, soundscapes, and cinematic scenes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
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
    movement: Optional[str] = None
    start_pan: Optional[str] = "center"
    start_zoom: Optional[str] = "normal"
    start_tilt: Optional[str] = "center"
    curve: Optional[str] = "cosine"
    speed_factor: Optional[float] = 1.0
    rationale: Optional[str] = None

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
    camera_movement: Union[List[Dict[str, Any]], List[Any], str] = Field(
        default="slow_zoom_in",
        description="Array of movement stages with durations or single movement"
    )
    motion_rationale: Optional[str] = None
    duration_seconds: float = 30.0
    narration_text: Optional[str] = None
    day_number: Optional[int] = 1
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    visit_duration: Optional[str] = None
    transit_duration: Optional[str] = None
    is_itinerary_overview: bool = False
    is_map_transition: bool = False
    is_itinerary_summary: bool = False
    is_vacation_scope: bool = False
    attraction_name: Optional[str] = None
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    origin_coords: Optional[List[float]] = None
    destination_coords: Optional[List[float]] = None
    distance_local: Optional[str] = None
    transit_mode: Optional[str] = "walk"
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
    sprites: List[Any] = Field(default_factory=list)
    tree_sway_zones: List[Any] = Field(default_factory=list)
    water_zones: List[Any] = Field(default_factory=list)
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
    itinerary_summary: Optional[List[Dict[str, Any]]] = None
    scenes: List[RelaxSceneDirective] = Field(default_factory=list)
    publishing: Optional[RelaxPublishingPackage] = None

    @field_validator("audio_master", mode="before")
    @classmethod
    def coerce_audio_master(cls, v: Any) -> Any:
        if isinstance(v, str):
            return RelaxAudioMasterSpec(suno_musical_tags=v)
        return v or RelaxAudioMasterSpec()


class BaseScenePrompt(BaseModel):
    """Universal scene prompt specification for studio pipeline execution."""
    scene_index: int = 1
    shot_type: Optional[str] = None
    perspective_type: str = "wide_panoramic"
    location_hub: Optional[str] = ""
    visual_prompt: str = ""
    motion_prompt: str = ""
    motion_negative_prompt: Optional[str] = None
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    motion_type: str = "ai_diffusion"
    camera_rig: str = "locked_tripod"
    camera_movement: Union[List[Dict[str, Any]], List[Any], str] = "slow_zoom_in"
    motion_rationale: Optional[str] = None
    narration_text: Optional[str] = None
    camera_waypoints: List[CameraWaypointDirective] = Field(default_factory=list)
    kinetic_micro_zones: Optional[KineticMicroSpec] = None
    image_model_configs: dict = Field(default_factory=dict)
    model_configs: dict = Field(default_factory=dict)
    # Tour & Itinerary Metadata
    is_itinerary_overview: bool = False
    is_map_transition: bool = False
    is_itinerary_summary: bool = False
    day_number: Optional[int] = 1
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    visit_duration: Optional[str] = None
    transit_duration: Optional[str] = None
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    origin_coords: Optional[List[float]] = None
    destination_coords: Optional[List[float]] = None
    distance_local: Optional[str] = None
    transit_mode: Optional[str] = "walk"


class BaseStoryboard(BaseModel):
    """Universal directorial storyboard representation across all channels and genres."""
    title: str = "Studio Production"
    story_topic: Optional[str] = ""
    primary_archetype: str = "cities"
    secondary_archetype: Optional[str] = None
    cluster: str = "travel"
    tier: str = "balanced"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str = ""
    audio_prompt: Optional[str] = ""
    spoken_narration_script: Optional[str] = ""
    itinerary_summary: Optional[List[Dict[str, Any]]] = None
    scenes: List[BaseScenePrompt] = Field(default_factory=list)

    @field_validator("audio_tags", mode="before")
    @classmethod
    def normalize_audio_tags(cls, v: Any) -> str:
        return normalize_audio_tags(v)

# Universal base aliases for full backward compatibility
AmbientScenePrompt = StudioScenePrompt = TravelScenePrompt = BaseScenePrompt
AmbientStoryboard = StudioStoryboard = TravelStoryboard = BaseStoryboard

def relax_to_ambient_storyboard(sp: RelaxScreenplay) -> BaseStoryboard:
    """Convert RelaxScreenplay to universal BaseStoryboard without dropping voiceover or kinetics."""
    scenes = []
    for idx, s in enumerate(sp.scenes, 1):
        scenes.append(
            BaseScenePrompt(
                scene_index=idx,
                shot_type=s.shot_type,
                perspective_type=s.shot_type,
                location_hub=getattr(s, "location_hub", "") or "",
                visual_prompt=s.visual_prompt,
                motion_prompt=s.motion_prompt,
                motion_negative_prompt=getattr(s, "motion_negative_prompt", None),
                duration_seconds=s.duration_seconds,
                domain=s.domain,
                motion_type=getattr(s, "motion_type", "ai_diffusion"),
                camera_rig=getattr(s, "camera_rig", "locked_tripod"),
                camera_movement=getattr(s, "camera_movement", "slow_zoom_in"),
                motion_rationale=getattr(s, "motion_rationale", None),
                narration_text=getattr(s, "narration_text", None),
                camera_waypoints=getattr(s, "camera_waypoints", []),
                kinetic_micro_zones=getattr(s, "kinetic_micro_zones", None),
                image_model_configs=s.image_model_configs,
                model_configs={k: v.model_dump() for k, v in s.model_configs.items()} if s.model_configs else {},
                is_itinerary_overview=getattr(s, "is_itinerary_overview", False),
                is_map_transition=getattr(s, "is_map_transition", False),
                is_itinerary_summary=getattr(s, "is_itinerary_summary", False),
                day_number=getattr(s, "day_number", 1),
                start_time=getattr(s, "start_time", None),
                end_time=getattr(s, "end_time", None),
                visit_duration=getattr(s, "visit_duration", None),
                transit_duration=getattr(s, "transit_duration", None),
                origin_name=getattr(s, "origin_name", None), destination_name=getattr(s, "destination_name", None),
                origin_coords=getattr(s, "origin_coords", None), destination_coords=getattr(s, "destination_coords", None),
                distance_local=getattr(s, "distance_local", None), transit_mode=getattr(s, "transit_mode", "walk"),
            )
        )
    return BaseStoryboard(
        title=sp.title, story_topic=sp.story_topic,
        primary_archetype=sp.primary_archetype or sp.sub_genre or "cities",
        secondary_archetype=sp.secondary_archetype, cluster=sp.cluster or "travel",
        tier=getattr(sp, "tier", None) or "balanced",
        total_duration=sp.total_duration_seconds or sum(s.duration_seconds for s in sp.scenes) or 60.0,
        recommended_fps=sp.recommended_fps or 24,
        audio_tags=sp.audio_master.suno_musical_tags if sp.audio_master else "",
        spoken_narration_script=getattr(sp.audio_master, "spoken_narration_script", "") if sp.audio_master else "",
        itinerary_summary=getattr(sp, "itinerary_summary", None), scenes=scenes,
    )

relax_to_studio_storyboard = relax_to_ambient_storyboard
