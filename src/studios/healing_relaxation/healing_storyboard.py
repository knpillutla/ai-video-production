"""Directorial Storyboard Generator for Healing Meditation & Relaxing Music."""

import json
from typing import List
from pydantic import BaseModel, Field
from src.core.telemetry import logger


class HealingScenePrompt(BaseModel):
    """Prompt definition for a healing relaxation scene."""
    scene_index: int
    perspective_type: str  # wide_zen_landscape, intimate_lotus_stream
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"


class HealingStoryboard(BaseModel):
    """Complete 2-perspective storyboard specification for Healing Relaxation."""
    title: str
    theme: str
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str
    scenes: List[HealingScenePrompt] = Field(default_factory=list)


def generate_healing_storyboard(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
) -> HealingStoryboard:
    """Generate the 2-perspective healing meditation directorial storyboard."""
    logger.info(f"generating_healing_storyboard: theme='{theme}' duration={duration_seconds}s")

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

    s1 = HealingScenePrompt(
        scene_index=1,
        perspective_type="wide_zen_landscape",
        visual_prompt=p1_visual,
        motion_prompt=p1_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="landscape_solid",
    )
    s2 = HealingScenePrompt(
        scene_index=2,
        perspective_type="intimate_lotus_stream",
        visual_prompt=p2_visual,
        motion_prompt=p2_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="water_fluid",
    )

    audio_tags = (
        f"[healing meditation music], 432Hz deep inner peace melody, soothing acoustic piano, Japanese bamboo shakuhachi flute, "
        "gentle Celtic harp, soft distant stream and morning birds, peaceful binaural 48kHz broadcast master, zero hiss"
    )

    return HealingStoryboard(
        title=theme,
        theme=theme,
        total_duration=duration_seconds,
        recommended_fps=24,
        audio_tags=audio_tags,
        scenes=[s1, s2],
    )


async def generate_healing_storyboard_gemini(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
) -> HealingStoryboard:
    """Dynamically generate 432Hz healing meditation storyboard via Gemini LLM."""
    print(f"\n[GEMINI HEALING RELAXATION AGENT INVOKED]")
    print(f"   * Theme:              \"{theme}\"")
    print(f"   * Duration:           {duration_seconds}s (2 Perspectives @ {duration_seconds/2.0}s each)")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter()

        system_prompt = (
            "You are a master meditation director and acoustic sound healer specializing in 432Hz sacred geometry, Zen gardens, and healing lotus sanctuaries. "
            "Generate an 8K UHD 2-perspective cinematic storyboard (Perspective 1: Wide Zen Sanctuary Landscape, Perspective 2: Intimate Lotus Macro/Stream Reflection). "
            "CRITICAL ANTI-FATIGUE DIRECTIVES:\n"
            "- ANTI-FATIGUE VIDEO MOTION: Locked tripod framing, hypnotic ultra-slow morning mist drift, glassy water ripples, zero abrupt zooms, zero camera shake, pure tranquility.\n"
            "- ANTI-FATIGUE ACOUSTIC MASTERING: 432Hz meditative Celtic harp, bamboo shakuhachi flute, soft singing bowl resonance, binaural nature foley, zero sharp high-frequency peaks, zero jarring drums, velvet -14 LUFS.\n"
            "- PURE ZEN NATURE PURITY GUARD: Mandate 'zero humans, zero people, zero persons, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero modern clutter, zero animals, zero pets' unless explicitly requested in the theme.\n"
            "For visual prompts: Mandate Arri Alexa 35mm cinematographic specifications, 8K UHD master resolution, exact focal lengths (35mm f/4.0, 50mm f/1.4), soft ethereal morning mist, glowing dawn caustics, and the pure Zen nature purity guard. "
            "Return valid JSON only matching the schema."
        )

        user_msg = (
            f"Generate an 8K UHD 2-perspective anti-fatigue healing meditation storyboard for theme: '{theme}'. Duration: {duration_seconds}s.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': High-CTR healing relaxation YouTube title\n"
            f"- 'audio_tags': 432Hz deep meditative anti-fatigue acoustic tags (bamboo flute, Celtic harp, gentle stream, zero harshness)\n"
            f"- 'scenes': Array of 2 scene objects each containing:\n"
            f"    - 'scene_index': int (1, 2)\n"
            f"    - 'perspective_type': 'wide_zen_landscape' or 'intimate_lotus_stream'\n"
            f"    - 'visual_prompt': detailed 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': ultra-soothing anti-fatigue video motion prompt for Wan 2.1 / Kling\n"
            f"    - 'domain': 'water_fluid' or 'landscape_solid'\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_healing_request_sent: theme='{theme}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI HEALING REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_healing_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI HEALING RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 2:
            scenes = []
            for idx, sc in enumerate(data["scenes"][:2]):
                scenes.append(
                    HealingScenePrompt(
                        scene_index=idx + 1,
                        perspective_type=sc.get("perspective_type", "wide_zen_landscape" if idx == 0 else "intimate_lotus_stream"),
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        duration_seconds=duration_seconds / 2.0,
                        domain=sc.get("domain", "water_fluid"),
                    )
                )

            sb = HealingStoryboard(
                title=data.get("title") or theme,
                theme=theme,
                total_duration=duration_seconds,
                recommended_fps=24,
                audio_tags=data.get("audio_tags") or "healing meditation music, 432Hz deep inner peace, bamboo shakuhachi flute, 48kHz master",
                scenes=scenes,
            )
            print(f"[GEMINI HEALING STORYBOARD SUCCESS] Synthesized '{sb.title}' with 2 custom perspectives.")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed healing storyboard data: {data}")
    except Exception as ex:
        logger.error(f"gemini_healing_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Healing directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini healing directorial screenplay generation failed: {ex}") from ex


__all__ = ["HealingScenePrompt", "HealingStoryboard", "generate_healing_storyboard", "generate_healing_storyboard_gemini"]
