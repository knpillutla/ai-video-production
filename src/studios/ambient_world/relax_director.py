"""Relaxation & Nature Genre Directorial Engine for CineAI Studio.

Enforces 100% Genre-Specific Directorial Prompts for Relax/Nature:
- Dedicated RelaxScreenplay Contract
- Living Wallpaper Framing ("wide_panoramic_picturesque")
- Ultra-Slow Gentle Kinetics for Water, Clouds, Plants, Grass, Flowers
- Multi-Model Directives (Wan 2.1 & Kling v1.6 Pro) with Custom API Settings
- Zero Humans (cast: [])
- Strict 5500K Balanced Natural Daylight Uniformity Across All Scenes
- Fresh Live Synthesis on Every Production Run (No Screenplay Cache)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from src.core.telemetry import logger
from src.studios.ambient_world.ambient_directorial_prompt import build_ambient_directorial_prompt
from src.studios.ambient_world.ambient_storyboard import AmbientScenePrompt, AmbientStoryboard
from src.studios.ambient_world.relax_models import (
    LoopStrategySpec,
    RelaxAudioMasterSpec,
    RelaxGlobalCultureSpec,
    RelaxModelConfigDirective,
    RelaxModelPromptsSpec,
    RelaxSceneDirective,
    RelaxScreenplay,
    RelaxTravelTourismSpec,
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
    image_model: str = "flux_1_1_pro_ultra",
) -> RelaxScreenplay:
    """Synthesize fresh relaxation directorial screenplay via Gemini with Relax Genre Directives & Channel Topic Memory."""
    # Retrieve recently generated topics for this user channel to strictly prevent repeats (Rule 10)
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)

    eff_prompt = custom_prompt.strip() if custom_prompt and custom_prompt.strip() else ""

    from src.core.config import settings
    from src.providers.base import HTTPClientPool

    api_key = (
        settings.llm.gemini_api_key
        or settings.llm.google_api_key
        or os.getenv("GEMINI_API_KEY", "")
        or os.getenv("GOOGLE_API_KEY", "")
    )
    if not api_key:
        raise RuntimeError("Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY.")

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
    )
    discovery_mode = "grounded_search" if google_search_enabled else ("knowledge_base" if not eff_prompt else "user_prompt")
    logger.info(f"gemini_relax_director_dispatch: mode='{discovery_mode}' archetype='{primary}' prompt='{eff_prompt}' exclusions={len(recent_topics)} chan='{channel_id}'")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": sys_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7,
            },
        }
        if google_search_enabled:
            payload["tools"] = [{"google_search": {}}]
        client = HTTPClientPool.get_client()
        request_body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        logger.info(f"gemini_api_request: model=gemini-flash-latest payload={request_body}")
        response = await client.post(url, json=payload, timeout=45.0)
        response_body = response.text
        logger.info(f"gemini_api_response: status={response.status_code} body={response_body}")

        if response.status_code != 200:
            error_body = response_body[:2000]
            logger.error(f"gemini_api_http_error: status={response.status_code} body={error_body}")
            raise RuntimeError(f"Gemini API request failed (HTTP {response.status_code}): {error_body}")

        data = response.json()
        candidates = data.get("candidates") if isinstance(data, dict) else None
        if not isinstance(candidates, list) or not candidates:
            details = data.get("error") or data.get("promptFeedback") or data
            detail_text = json.dumps(details, ensure_ascii=True)[:2000]
            logger.error(f"gemini_response_missing_candidates: body={detail_text}")
            raise RuntimeError(f"Gemini returned no screenplay candidates (HTTP 200): {detail_text}")

        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        raw_json = next(
            (part.get("text", "").strip() for part in parts if isinstance(part, dict) and part.get("text")),
            "",
        )
        if not raw_json:
            reason = candidate.get("finishReason") or candidate.get("safetyRatings") or candidate
            detail_text = json.dumps(reason, ensure_ascii=True)[:2000]
            logger.error(f"gemini_candidate_missing_text: details={detail_text}")
            raise RuntimeError(f"Gemini returned a candidate without screenplay text: {detail_text}")

        # Save raw Gemini response JSON for permanent reference
        if raw_output_path:
            try:
                from pathlib import Path
                raw_p = Path(raw_output_path)
                raw_p.parent.mkdir(parents=True, exist_ok=True)
                raw_p.write_text(raw_json, encoding="utf-8")
                logger.info(f"raw_gemini_screenplay_saved: {raw_p}")
                grounding = candidate.get("groundingMetadata")
                if grounding:
                    grounding_path = raw_p.with_suffix(".grounding.json")
                    grounding_path.write_text(json.dumps(grounding, indent=2), encoding="utf-8")
                    logger.info(f"gemini_grounding_metadata_saved: {grounding_path}")
            except Exception as raw_save_err:
                logger.warning(f"failed_to_save_raw_gemini_json: {raw_save_err}")

        parsed = json.loads(raw_json)

        # Validate RelaxScreenplay contract
        screenplay = RelaxScreenplay(**parsed)

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

    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception(f"gemini_relax_director_failed: {exc}")
        raise RuntimeError(f"Gemini screenplay generation failed: {exc}") from exc


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
                    "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, "
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
            suno_musical_tags=f"432Hz ambient, natural foley, {prompt}, tranquil water and wind, -14 LUFS",
            tempo_bpm=60,
            target_lufs=-14.0,
        ),
        scenes=scenes,
    )


def relax_to_ambient_storyboard(sp: RelaxScreenplay) -> AmbientStoryboard:
    """Convert RelaxScreenplay to backward-compatible AmbientStoryboard contract with autonomous cluster."""
    primary_arch = sp.primary_archetype or sp.sub_genre or sp.genre or "nature_sanctuary"
    sec_arch = sp.secondary_archetype
    cluster_val = sp.cluster or sp.sub_genre or primary_arch
    return AmbientStoryboard(
        title=sp.title,
        story_topic=sp.story_topic,
        primary_archetype=primary_arch,
        secondary_archetype=sec_arch,
        cluster=cluster_val,
        total_duration=sp.total_duration_seconds,
        recommended_fps=sp.recommended_fps,
        audio_tags=sp.audio_master.suno_musical_tags if sp.audio_master else "",
        scenes=[
            AmbientScenePrompt(
                scene_index=s.scene_index,
                perspective_type=s.shot_type,
                visual_prompt=s.visual_prompt,
                motion_prompt=s.motion_prompt,
                duration_seconds=s.duration_seconds,
                domain=s.domain,
                image_model_configs=getattr(s, "image_model_configs", {}),
                model_configs=getattr(s, "model_configs", {}),
            )
            for s in sp.scenes
        ],
    )
