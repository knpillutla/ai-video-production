"""Relaxation & Nature Genre Directorial Engine for CineAI Studio."""
from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional

from src.core.telemetry import logger
from src.studios.ambient_world.ambient_directorial_prompt import build_ambient_directorial_prompt
from src.studios.screenplay_models import (
    BaseScenePrompt,
    BaseStoryboard,
    AmbientScenePrompt,
    AmbientStoryboard,
    relax_to_ambient_storyboard,
)
from src.studios.ambient_world.relax_models import (
    LoopStrategySpec, RelaxAudioMasterSpec, RelaxGlobalCultureSpec,
    RelaxModelConfigDirective, RelaxModelPromptsSpec, RelaxSceneDirective,
    RelaxScreenplay, RelaxTravelTourismSpec,
)
from src.services.topic_memory import topic_memory

async def generate_relax_screenplay_gemini(
    primary: str = "",
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    genre: str = "relax/nature",
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    tier: str = "balanced",
) -> RelaxScreenplay:
    """Synthesize fresh relaxation directorial screenplay via Gemini with Relax Genre Directives & Channel Topic Memory."""
    # Retrieve recently generated topics for this user channel to strictly prevent repeats (Rule 10)
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)
    eff_prompt = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else ""

    from src.core.config import settings
    google_search_enabled = bool(settings.llm.gemini_google_search_enabled and not eff_prompt)

    # Genre-Specific Relaxation Directorial System Prompt with Negative Topic Exclusions
    sys_prompt = build_ambient_directorial_prompt(
        genre=genre,
        archetype=primary,
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=recent_topics,
        image_model=image_model,
        google_search_enabled=google_search_enabled,
        tier=tier,
    )
    discovery_mode = "grounded_search" if google_search_enabled else ("knowledge_base" if not eff_prompt else "user_prompt")
    logger.info(f"gemini_relax_director_dispatch: mode='{discovery_mode}' archetype='{primary}' prompt='{eff_prompt}' exclusions={len(recent_topics)} chan='{channel_id}'")

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    screenplay = await execute_directorial_screenplay(
        sys_prompt=sys_prompt,
        raw_output_path=raw_output_path,
        tier=tier or "balanced",
        genre=genre,
        cluster=primary,
        primary_archetype=primary,
        google_search_enabled=google_search_enabled,
    )

    # Commit to Topic Memory so future runs on this channel will NEVER repeat this destination (Rule 10)
    try:
        await topic_memory.remember_topic(
            topic=screenplay.title,
            genre=genre,
            tags=screenplay.publishing.seo_tags if screenplay.publishing else [],
            story_synopsis=screenplay.story_topic,
            episode_id=screenplay.production_id,
            user_id=user_id,
            channel_id=channel_id,
        )
    except Exception as mem_ex:
        logger.warning(f"topic_memory_commit_failed: {mem_ex}")

    return screenplay


def _build_deterministic_relax_screenplay(
    primary: str, prompt: str, duration_seconds: float, num_shots: int
) -> RelaxScreenplay:
    """Deterministic fallback satisfying all relaxation living wallpaper rules."""
    shot_dur = round(duration_seconds / max(1, num_shots), 1)
    clean_title = prompt.replace("_", " ").title()

    scenes = []
    for i in range(num_shots):
        scenes.append(
            RelaxSceneDirective(
                scene_index=i + 1,
                location_hub=f"{clean_title} - Vista {i + 1}",
                shot_type="wide_panoramic_picturesque",
                camera_rig="locked_tripod",
                color_temp_kelvin=5500,
                visual_prompt=(
                    f"Dead-center symmetrical frontal vantage point, head-on straight perspective, centered bilateral composition with zero side-angle. "
                    f"Living wallpaper framing, ultra-wide panoramic picturesque landscape under soft diffused moody overcast skies. "
                    f"Cinematic 8K UHD shot on Hasselblad H6D-100c with 24mm prime lens, {prompt}. "
                    f"Low-hanging clouds, dense billowing vapor mist, cool dark wet stone, strictly zero humans, zero vehicles, zero sunlight."
                ),
                image_model_configs={
                    "flux_1_1_pro_ultra": {
                        "model": "fal-ai/flux-pro/v1.1-ultra",
                        "prompt": (
                            f"Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. "
                            f"Dead-center symmetrical frontal vantage point, eye-level head-on straight perspective, centered bilateral composition with zero side-angle, zero three-quarter view. "
                            f"Living wallpaper framing, ultra-wide panoramic picturesque landscape under soft moody overcast skies with low clouds and dense rising vapor mist. "
                            f"{prompt}. Cool slate stones, dark wet rocks, emerald water, and billowing mist. "
                            f"Pristine untouched wilderness, strictly zero humans, zero modern structures, zero vehicles, zero sunlight, zero blue sky."
                        ),
                        "aspect_ratio": "16:9",
                        "raw": True,
                    }
                },
                motion_prompt=(
                    "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, "
                    "zero panning, zero tilting, zero zooming. The rock cliffs, horizon line, and overall landscape structure "
                    "remain 100% frozen and static. Only the water moves: continuous, downward flowing cataract curtains "
                    "directly following the paths in the source image, into the churning turquoise basin below. "
                    "Soft, slow-moving vapor mist steadily rises up from the bottom center chasm without shifting the landscape."
                ),
                motion_negative_prompt=(
                    "clouds, cloudy, overcast sky, moving clouds, timelapse clouds, camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, "
                    "hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, "
                    "structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, "
                    "changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, "
                    "melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings"
                ),
                model_configs={
                    "kling_v1_6_pro": RelaxModelConfigDirective(
                        model="fal-ai/kling-video/v1.6/pro/image-to-video",
                        prompts=RelaxModelPromptsSpec(
                            positive_prompt="Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous downward flowing water cascades directly matching the source image into the churning emerald basin, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans.",
                            negative_prompt="camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
                        ),
                        settings={"mode": "pro", "duration": "5", "aspect_ratio": "16:9"},
                    ),
                    "wan_2_1": RelaxModelConfigDirective(
                        model="fal-ai/wan-i2v",
                        prompts=RelaxModelPromptsSpec(
                            positive_prompt="Living wallpaper cinemagraph, completely stationary static frame. Rock cliffs and landscape structure remain 100% frozen and unmoving. Smooth continuous laminar water cascades flowing steadily downwards into the basin, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible.",
                            negative_prompt="camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
                        ),
                        settings={"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"},
                    ),
                },
                loop_strategy=LoopStrategySpec(
                    target_clip_duration_seconds=shot_dur,
                    generation_segment_seconds=5.0,
                    continuity_mode="cyclic_temporal_flow",
                    seam_strategy="forward_phase_aligned_crossfade",
                    unidirectional_flow=True,
                    crossfade_seconds=1.2,
                    loop_validation=True,
                ),
                domain="water_fluid",
                duration_seconds=shot_dur,
            )
        )

    return RelaxScreenplay(
        production_id="EP-001",
        title=f"8K Living Wallpaper: {clean_title}",
        story_topic=f"Ultra-tranquil living wallpaper soundscape capturing {prompt} with stationary picturesque cinematography and velvet binaural audio.",
        genre="relax/nature",
        sub_genre=prompt.lower().replace(" ", "_"),
        recommended_fps=24,
        total_duration_seconds=duration_seconds,
        global_culture=RelaxGlobalCultureSpec(
            continent_region="Global Nature Sanctuary",
            culture_heritage="Natural Heritage Conservation",
            authentic_textiles_and_fabrics="Natural stone, native moss, weathered timber, and crystal water",
            cultural_gestures_and_rituals="Tranquil mindful contemplation of nature",
        ),
        travel_tourism=RelaxTravelTourismSpec(
            destination_name=clean_title,
            country="Scenic Nature Sanctuary",
            attraction_type="Natural Landmark & Scenic Wonder",
            best_season_and_lighting="Moody Diffused Overcast & Dense Mist",
        ),
        cast=[],  # Zero humans mandate for relaxation
        audio_master=RelaxAudioMasterSpec(
            audio_mode="ambient_nature",
            suno_musical_tags=f"432Hz meditation, joyful handpan, singing bowls, velvet synth pads, {prompt}, deep stress relief, sleep drone, zero guitar, -21 LUFS",
            tempo_bpm=60,
            target_lufs=-14.0,
        ),
        scenes=scenes,
    )


# relax_to_ambient_storyboard is imported directly from screenplay_models
__all__ = [
    "generate_relax_screenplay_gemini",
    "relax_to_ambient_storyboard",
    "AmbientScenePrompt",
    "AmbientStoryboard",
    "BaseScenePrompt",
    "BaseStoryboard",
]
