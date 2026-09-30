"""Directorial Storyboard Generator for Rain Retreat & River ASMR."""

import json
from typing import List
from pydantic import BaseModel, Field
from src.core.telemetry import logger


class RainScenePrompt(BaseModel):
    """Prompt definition for a rain retreat scene."""
    scene_index: int
    perspective_type: str  # wide_forest_river, macro_water_ripples
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "water_fluid"


class RainStoryboard(BaseModel):
    """Complete 2-perspective storyboard specification for Rain Retreat."""
    title: str
    theme: str
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str
    scenes: List[RainScenePrompt] = Field(default_factory=list)


def generate_rain_storyboard(
    theme: str = "Lush Forest River in Gentle Rain",
    duration_seconds: float = 60.0,
) -> RainStoryboard:
    """Generate the 2-perspective rain retreat directorial storyboard."""
    logger.info(f"generating_rain_storyboard: theme='{theme}' duration={duration_seconds}s")

    p1_visual = (
        f"Masterpiece 4K nature photograph of a serene forest river during gentle steady rainfall in {theme}. "
        "Emerald clear stream winding gracefully through ancient moss-covered granite boulders, deep lush green pine trees and ferns, "
        "rain droplets falling continuously onto the water surface creating thousands of expanding circular ripples. "
        "Soft misty atmosphere drifting through the trees, glistening wet foliage, natural cool diffused daylight (5500K), "
        "photorealistic 35mm Arri Alexa cinematography, 8k resolution, zero humans, zero artificial flares."
    )
    p1_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Continuous steady rainfall with realistic vertical raindrops hitting the water surface, fluid river current flowing gently downstream, "
        "expanding water droplet ripples across the stream surface, subtle swaying wet foliage in the calm forest breeze."
    )

    p2_visual = (
        f"Macro close-up 50mm perspective of pristine rain droplets falling on calm river water in {theme}. "
        "Razor-sharp focus on expanding circular ripples on translucent emerald water, smooth river pebbles visible below, "
        "overhanging wet cedar leaves dripping sparkling raindrops. Soft forest background with gentle misty bokeh, ultra-detailed water physics, zero humans."
    )
    p2_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Hypnotic expanding circular water ripples from falling raindrops, sparkling water reflections, delicate water drops falling from green leaves, "
        "smooth laminar liquid physics, stationary close-up camera."
    )

    s1 = RainScenePrompt(
        scene_index=1,
        perspective_type="wide_forest_river",
        visual_prompt=p1_visual,
        motion_prompt=p1_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="water_fluid",
    )
    s2 = RainScenePrompt(
        scene_index=2,
        perspective_type="macro_water_ripples",
        visual_prompt=p2_visual,
        motion_prompt=p2_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="water_fluid",
    )

    audio_tags = (
        f"[ambient asmr soundscape], pure natural rain falling on river water, gentle babbling mountain brook, "
        "wet foliage dripping sounds, soothing ASMR sleep white noise, binaural 48kHz broadcast master, zero hiss"
    )

    return RainStoryboard(
        title=theme,
        theme=theme,
        total_duration=duration_seconds,
        recommended_fps=24,
        audio_tags=audio_tags,
        scenes=[s1, s2],
    )


async def generate_rain_storyboard_gemini(
    theme: str = "Forest River Rain & Water Droplets",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
) -> RainStoryboard:
    """Dynamically generate binaural rain & water droplet storyboard via Gemini LLM."""
    print(f"\n[GEMINI RAIN RETREAT AGENT INVOKED]")
    print(f"   * Theme:              \"{theme}\"")
    print(f"   * Duration:           {duration_seconds}s (2 Perspectives @ {duration_seconds/2.0}s each)")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter()

        system_prompt = (
            "You are a master nature director and binaural ASMR sound designer specializing in tranquil forest rainfall and water droplet soundscapes. "
            "Generate an 8K UHD 2-perspective cinematic storyboard (Perspective 1: Wide Forest River Rain, Perspective 2: Intimate Water Droplet Macro/Ripple Detail). "
            "CRITICAL ANTI-FATIGUE DIRECTIVES:\n"
            "- ANTI-FATIGUE VIDEO MOTION: Locked tripod framing, continuous soothing fine falling rain streaks, expanding circular water ripples on river surface, slow tranquil flow, zero camera shake, zero rapid pans.\n"
            "- ANTI-FATIGUE ACOUSTIC MASTERING: Binaural soft rain ASMR, gentle stream trickle, warm low-end rumble, zero harsh high-frequency sizzle/hiss (>8kHz), zero sudden claps of thunder, velvet -14 LUFS.\n"
            "- PURE RAIN NATURE PURITY GUARD: Mandate 'zero humans, zero people, zero persons, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero modern clutter, zero animals, zero pets' unless explicitly requested in the theme.\n"
            "For visual prompts: Mandate Arri Alexa 35mm cinematographic specifications, 8K UHD master resolution, exact focal lengths (35mm f/4.0, 50mm f/1.4), glistening wet moss, rain droplets splashing on calm water, and the pure rain nature purity guard. "
            "Return valid JSON only matching the schema."
        )

        user_msg = (
            f"Generate an 8K UHD 2-perspective anti-fatigue forest rain storyboard for theme: '{theme}'. Duration: {duration_seconds}s.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': High-CTR rain relaxation YouTube title\n"
            f"- 'audio_tags': Binaural anti-fatigue ASMR rain and river foley tags (warm rain, gentle trickle, zero harsh hiss, 48kHz)\n"
            f"- 'scenes': Array of 2 scene objects each containing:\n"
            f"    - 'scene_index': int (1, 2)\n"
            f"    - 'perspective_type': 'wide_forest_river_rain' or 'intimate_macro_water_droplet'\n"
            f"    - 'visual_prompt': detailed 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': continuous soothing anti-fatigue video motion prompt for Wan 2.1 / Kling\n"
            f"    - 'domain': 'water_fluid'\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_rain_request_sent: theme='{theme}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI RAIN REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_rain_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI RAIN RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 2:
            scenes = []
            for idx, sc in enumerate(data["scenes"][:2]):
                scenes.append(
                    RainScenePrompt(
                        scene_index=idx + 1,
                        perspective_type=sc.get("perspective_type", "wide_forest_river_rain" if idx == 0 else "intimate_macro_water_droplet"),
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        duration_seconds=duration_seconds / 2.0,
                        domain="water_fluid",
                    )
                )

            sb = RainStoryboard(
                title=data.get("title") or theme,
                theme=theme,
                total_duration=duration_seconds,
                recommended_fps=24,
                audio_tags=data.get("audio_tags") or "ambient asmr soundscape, pure natural rain falling on river, wet foliage, 48kHz master",
                scenes=scenes,
            )
            print(f"[GEMINI RAIN STORYBOARD SUCCESS] Synthesized '{sb.title}' with 2 custom perspectives.")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed rain storyboard data: {data}")
    except Exception as ex:
        logger.error(f"gemini_rain_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Rain directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini rain directorial screenplay generation failed: {ex}") from ex


__all__ = ["RainScenePrompt", "RainStoryboard", "generate_rain_storyboard", "generate_rain_storyboard_gemini"]
