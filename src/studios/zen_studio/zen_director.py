"""Directorial Storyboard Generator for Healing Meditation & Relaxing Music."""

import json
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from src.core.telemetry import logger
from src.studios.ambient_world.relax_models import RelaxAudioMasterSpec, RelaxSceneDirective, RelaxScreenplay
from src.services.audio_tag_service import normalize_audio_tags


class ZenScenePrompt(BaseModel):
    """Prompt definition for a Zen Studio scene."""
    scene_index: int
    perspective_type: str  # wide_zen_landscape, intimate_lotus_stream
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class ZenStoryboard(BaseModel):
    """Complete 2-perspective storyboard specification for Zen Studio."""
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/zen"
    sub_genre: str = "zen_healing"
    primary_archetype: str = "zen_garden"
    secondary_archetype: str = ""
    cluster: str = ""
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any
    scenes: List[ZenScenePrompt] = Field(default_factory=list)


ZEN_SUBGENRE_DIRECTIVES = {
    "zen_healing": (
        "Zen healing sanctuary: Kyoto temple gardens, bamboo groves, mossy stone lanterns, raked gravel, "
        "subtle 432Hz bell resonance, and calm reflective water."
    ),
    "lotus_pond": (
        "Sacred lotus pond: blooming lotus flowers, lily pads, a gentle bamboo water basin, "
        "clear pond reflections, and delicate water movement."
    ),
}

ZEN_ARCHETYPE_DIRECTIVES = {
    "zen_garden": (
        "Use authentic Japanese garden composition: restrained asymmetry, carefully placed natural stone, "
        "pruned pines, bamboo, moss, and quiet temple details; no rainforest or alpine scenery."
    ),
}


def generate_zen_storyboard(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
    num_shots: int = 1,
) -> ZenStoryboard:
    """Generate a Zen storyboard with one scene for each requested shot."""
    num_shots = max(1, int(num_shots))
    logger.info(f"generating_zen_storyboard: theme='{theme}' duration={duration_seconds}s shots={num_shots}")

    p1_visual = (
        f"Masterpiece 4K photograph of a sacred tranquil Japanese Zen garden with lotus pond in {theme}. "
        "Glassy mirror-like crystal water surface reflecting weeping cherry blossoms, sculpted green bonsai pine trees, and smooth mossy stone lanterns. "
        "Soft ethereal morning sunlight filtering through golden dawn mist, serene wooden temple bridge in the background, "
        "deeply peaceful spiritual atmosphere, natural balanced 5400K daylight, 35mm Arri Alexa cinematography, 8k resolution, zero humans."
    )
    p1_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Subtle tranquil morning mist slowly drifting across the glassy lotus pond, very gentle water ripples reflecting dawn light, "
        "soft swaying cherry blossom branches in the peaceful breeze."
    )

    p2_visual = (
        f"Close-up 50mm portrait perspective of blooming sacred pink lotus flowers floating on crystal water in {theme}. "
        "Razor-sharp focus on glowing pink and white lotus petals with delicate translucent water droplets, smooth emerald lily pads, "
        "and clear water revealing smooth submerged river stones below. Soft golden sunrise bokeh in the background, pure serenity, zero humans."
    )
    p2_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Delicate water movement gently cradling the floating lotus flower, shimmering golden morning light glinting on water droplets, "
        "peaceful stationary camera."
    )

    perspectives = [
        ("wide_zen_landscape", p1_visual, p1_motion, "landscape_solid"),
        ("intimate_lotus_stream", p2_visual, p2_motion, "water_fluid"),
    ]
    scenes = [
        ZenScenePrompt(
            scene_index=index + 1,
            perspective_type=perspective,
            visual_prompt=visual,
            motion_prompt=motion,
            duration_seconds=duration_seconds / num_shots,
            domain=domain,
        )
        for index in range(num_shots)
        for perspective, visual, motion, domain in [perspectives[index % len(perspectives)]]
    ]

    audio_tags = (
        f"[healing meditation music], 432Hz deep inner peace melody, soothing acoustic piano, Japanese bamboo shakuhachi flute, "
        "gentle Celtic harp, soft distant stream and morning birds, peaceful binaural 48kHz broadcast master, zero hiss"
    )

    return ZenStoryboard(
        title=theme,
        theme=theme,
        total_duration=duration_seconds,
        recommended_fps=24,
        audio_tags=audio_tags,
        scenes=scenes,
    )


async def generate_zen_storyboard_gemini(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
    genre: str = "relax/zen",
    sub_genre: str = "zen_healing",
    primary_archetype: str = "zen_garden",
    num_shots: int = 1,
    raw_output_path: Optional[str | Path] = None,
) -> ZenStoryboard:
    """Dynamically generate 432Hz healing meditation storyboard via Gemini LLM."""
    print(f"\n[GEMINI ZEN STUDIO AGENT INVOKED]")
    print(f"   * Theme:              \"{theme}\"")
    num_shots = max(1, int(num_shots))
    print(f"   * Duration:           {duration_seconds}s ({num_shots} scenes @ {duration_seconds/num_shots:.1f}s each)")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter(strict=True)

        subgenre_directive = ZEN_SUBGENRE_DIRECTIVES.get(sub_genre, "Use a tranquil healing nature setting matching the selected sub-genre.")
        archetype_directive = ZEN_ARCHETYPE_DIRECTIVES.get(primary_archetype, "Preserve the selected ecosystem archetype exactly.")
        system_prompt = (
            "You are the dedicated Zen Studio director, specializing in 432Hz Zen gardens, bamboo temples, and sacred lotus sanctuaries. "
            "Treat the selected genre, sub-genre, and archetype as binding ecosystem constraints. Never replace Zen gardens with rainforest, alpine, canyon, or unrelated river scenes. "
            "When no free-text prompt is supplied, use your built-in geographic knowledge to select a notable real Zen garden or bamboo sanctuary matching the selected archetype. "
            f"SUB-GENRE DIRECTIVE ({sub_genre}): {subgenre_directive} "
            f"ARCHETYPE DIRECTIVE ({primary_archetype}): {archetype_directive} "
            f"Generate exactly {num_shots} 8K UHD cinematic scene(s). Never add scenes beyond the requested count. "
            "For one scene use a wide Zen sanctuary landscape; when multiple are requested, progress from wide landscape to intimate lotus/water details. "
            "CRITICAL ANTI-FATIGUE DIRECTIVES:\n"
            "- ANTI-FATIGUE VIDEO MOTION: Locked tripod framing, hypnotic ultra-slow morning mist drift, glassy water ripples, zero abrupt zooms, zero camera shake, pure tranquility.\n"
            "- ANTI-FATIGUE ACOUSTIC MASTERING: 432Hz meditative Celtic harp, bamboo shakuhachi flute, soft singing bowl resonance, binaural nature foley, zero sharp high-frequency peaks, zero jarring drums, velvet -14 LUFS.\n"
            "- PURE ZEN NATURE PURITY GUARD: Mandate 'zero humans, zero people, zero persons, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero modern clutter, zero animals, zero pets' unless explicitly requested in the theme.\n"
            "For visual prompts: Mandate Arri Alexa 35mm cinematographic specifications, 8K UHD master resolution, exact focal lengths (35mm f/4.0, 50mm f/1.4), soft ethereal morning mist, glowing dawn caustics, and the pure Zen nature purity guard. "
            "Return valid JSON only matching the schema."
        )

        user_msg = (
            f"Optional user prompt: '{theme or '(none supplied)'}'.\n"
            f"Selected genre: {genre}.\nSelected sub-genre: {sub_genre}.\nSelected primary archetype: {primary_archetype}.\n"
            f"Generate exactly {num_shots} scenes and preserve these selections. Duration: {duration_seconds}s; each scene is {duration_seconds/num_shots:.1f}s.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': High-CTR Zen Studio YouTube title\n"
            f"- 'story_topic': Story synopsis for the selected Zen destination\n"
            f"- 'destination_name': Real Zen garden or bamboo sanctuary name\n"
            f"- 'country': Destination country\n"
            f"- 'cluster': Geographic region identifier\n"
            f"- 'audio_tags': 432Hz deep meditative anti-fatigue acoustic tags (bamboo flute, Celtic harp, gentle stream, zero harshness)\n"
            f"- 'scenes': Array of exactly {num_shots} scene object(s), each containing:\n"
            f"    - 'scene_index': int (1, 2)\n"
            f"    - 'perspective_type': 'wide_zen_landscape' or 'intimate_lotus_stream'\n"
            f"    - 'visual_prompt': detailed 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': ultra-soothing anti-fatigue video motion prompt for Wan 2.1 / Kling\n"
            f"    - 'domain': 'water_fluid' or 'landscape_solid'\n"
            f"    - 'location_hub': specific place or perspective name\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_zen_request_sent: theme='{theme}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI ZEN STUDIO REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        if raw_output_path:
            try:
                raw_path = Path(raw_output_path)
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                raw_path.write_text(raw_json, encoding="utf-8")
                logger.info(f"raw_gemini_screenplay_saved: {raw_path}")
            except OSError as save_error:
                logger.warning(f"failed_to_save_raw_gemini_screenplay: {save_error}")
        logger.info(f"gemini_zen_response_received:\n{raw_json}")
        print(f"\n[GEMINI ZEN RESPONSE RECEIVED]\n{raw_json}\n")

        if data and isinstance(data, dict) and isinstance(data.get("scenes"), list) and len(data["scenes"]) == num_shots:
            scenes = []
            for idx, sc in enumerate(data["scenes"]):
                scenes.append(
                    ZenScenePrompt(
                        scene_index=idx + 1,
                        perspective_type=sc.get("perspective_type", "wide_zen_landscape" if idx == 0 else "intimate_lotus_stream"),
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        duration_seconds=duration_seconds / num_shots,
                        domain=sc.get("domain", "water_fluid"),
                        location_hub=sc.get("location_hub", ""),
                    )
                )

            sb = ZenStoryboard(
                title=data.get("title") or theme,
                theme=theme,
                story_topic=data.get("story_topic", ""),
                genre=genre,
                sub_genre=sub_genre,
                primary_archetype=primary_archetype,
                secondary_archetype=data.get("secondary_archetype", ""),
                cluster=data.get("cluster", ""),
                total_duration=duration_seconds,
                recommended_fps=24,
                audio_tags=data.get("audio_tags") or "healing meditation music, 432Hz deep inner peace, bamboo shakuhachi flute, 48kHz master",
                scenes=scenes,
            )
            print(f"[GEMINI ZEN STORYBOARD SUCCESS] Synthesized '{sb.title}' with {num_shots} custom scene(s).")
            return sb
        actual_count = len(data.get("scenes", [])) if isinstance(data, dict) and isinstance(data.get("scenes"), list) else 0
        raise RuntimeError(f"Gemini returned {actual_count} Zen scene(s); exactly {num_shots} requested.")
    except Exception as ex:
        logger.error(f"gemini_zen_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Zen directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini Zen directorial screenplay generation failed: {ex}") from ex


async def generate_zen_screenplay_gemini(
    genre: str,
    sub_genre: str,
    primary_archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    user_id: str,
    num_shots: int = 1,
    raw_output_path: Optional[str | Path] = None,
) -> RelaxScreenplay:
    """Generate a Zen screenplay using the dedicated Zen Studio director."""
    storyboard = await generate_zen_storyboard_gemini(
        theme=custom_prompt,
        duration_seconds=duration_seconds,
        user_id=user_id,
        genre=genre,
        sub_genre=sub_genre,
        primary_archetype=primary_archetype,
        num_shots=num_shots,
        raw_output_path=raw_output_path,
    )
    return RelaxScreenplay(
        title=storyboard.title,
        story_topic=storyboard.story_topic or storyboard.theme or storyboard.title,
        genre=genre,
        sub_genre=sub_genre,
        primary_archetype=primary_archetype,
        secondary_archetype=storyboard.secondary_archetype or None,
        cluster=storyboard.cluster or None,
        recommended_fps=storyboard.recommended_fps,
        total_duration_seconds=storyboard.total_duration,
        cast=[],
        audio_master=RelaxAudioMasterSpec(
            audio_mode="ambient_nature",
            suno_musical_tags=normalize_audio_tags(storyboard.audio_tags),
            target_lufs=-14.0,
        ),
        scenes=[
            RelaxSceneDirective(
                scene_index=scene.scene_index,
                location_hub=scene.location_hub or scene.perspective_type,
                shot_type=scene.perspective_type,
                camera_rig="locked_tripod",
                visual_prompt=scene.visual_prompt,
                motion_prompt=scene.motion_prompt,
                domain=scene.domain,
                duration_seconds=scene.duration_seconds,
            )
            for scene in storyboard.scenes
        ],
    )


__all__ = [
    "ZenScenePrompt",
    "ZenStoryboard",
    "generate_zen_storyboard",
    "generate_zen_storyboard_gemini",
    "generate_zen_screenplay_gemini",
]
