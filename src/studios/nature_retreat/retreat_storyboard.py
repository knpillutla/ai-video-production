"""Directorial Storyboard Generator for 4K Biophilic Nature Retreats & Soundscapes."""

from typing import Any


def generate_nature_storyboard(
    theme: str = "Rainforest Waterfall Patio",
    duration_seconds: float = 20.0,
    scenes_count: int = 4,
    language: str = "en",
) -> dict[str, Any]:
    """Autonomously synthesize a 4-angle directorial storyboard tailored to biophilic retreats."""
    t_lower = (theme or "").lower()
    dur_per_scene = round(duration_seconds / max(1, scenes_count), 2)

    is_waterfall = any(k in t_lower for k in ("waterfall", "cascade", "plunge", "rapids"))
    is_ocean = any(k in t_lower for k in ("ocean", "beach", "coastal", "surf", "santorini", "sea"))
    is_zen = any(k in t_lower for k in ("zen", "koi", "japan", "kyoto", "bamboo", "temple"))

    if is_waterfall:
        water_scene_domain = "water_impact_collision"
        water_motion_prompt = (
            "Powerful natural waterfall cascading continuously over dark mossy stone rocks into turquoise pool below, "
            "heavy volumetric water flow with realistic splash mist plume, dynamic expanding impact ripples, 24fps."
        )
        suno_tags = "ambient nature, crystal-clear mountain waterfall, soothing gentle water splash and babbling brook, soft acoustic meditative harp and bamboo flute, zero hiss, 48kHz broadcast master"
    elif is_ocean:
        water_scene_domain = "water_fluid"
        water_motion_prompt = (
            "Continuous smooth laminar ocean wave swells rolling rhythmically toward the shore, gentle coastal sea breeze, specular light glints, 24fps."
        )
        suno_tags = "ambient ocean, tranquil sea waves, soothing calm breeze, gentle acoustic guitar and warm meditative pads, zero hiss, 48kHz broadcast master"
    else:
        water_scene_domain = "water_fluid"
        water_motion_prompt = (
            "Tranquil crystal-clear stream flowing gently through mossy stones, delicate natural surface ripples, soft bamboo water fountain motion, 24fps."
        )
        suno_tags = "ambient zen garden, gentle trickling bamboo stream, soft koto and meditative harp, peaceful nature sounds, zero hiss, 48kHz broadcast master"

    scenes: list[dict[str, Any]] = [
        {
            "scene_index": 0,
            "duration_seconds": dur_per_scene,
            "shot_type": "wide_shot",
            "motion_domain": "landscape_solid",
            "motion_type": "steadycam_vista",
            "camera_movement": "slow_zoom_in",
            "visual_prompt": (
                f"Raw cinematic 35mm film photograph, wide establishing panoramic view of an opulent {theme}, "
                f"lush tropical rainforest foliage, blooming vibrant bougainvillea, weathered teak wood deck, polished river stones, "
                f"crystal-clear turquoise plunge pool, warm glowing brass lanterns, soft morning mist, crisp 5400K natural daylight, "
                f"Arri Alexa 35mm Master Prime lens at f/4.0, zero plastic CGI sheen, zero people."
            ),
            "motion_prompt": "Slow tranquil steadycam forward glide over teak wood deck toward the lush tropical garden and water, gentle breeze fluttering fern leaves, 24fps.",
            "dialogue": "Welcome to your secluded sanctuary, where cascading waters and pristine nature bring timeless tranquility.",
        },
        {
            "scene_index": 1,
            "duration_seconds": dur_per_scene,
            "shot_type": "medium_shot",
            "motion_domain": water_scene_domain,
            "motion_type": "kinetic_video",
            "camera_movement": "tilt_down",
            "visual_prompt": (
                f"Raw cinematic 35mm film still, medium eye-level perspective of a {theme} water feature, "
                f"natural dark basalt rock formation, cascading crystal water pouring into a tranquil pool, "
                f"dew-kissed emerald monstera leaves, warm ambient lantern light on stone edges, Arri Alexa 50mm lens at f/2.8, zero people."
            ),
            "motion_prompt": water_motion_prompt,
            "dialogue": "Listen to the soothing rhythm of living water flowing endlessly over ancient stones.",
        },
        {
            "scene_index": 2,
            "duration_seconds": dur_per_scene,
            "shot_type": "close_up",
            "motion_domain": "water_fluid",
            "motion_type": "kinetic_video",
            "camera_movement": "pan_right",
            "visual_prompt": (
                f"Raw cinematic 35mm film still, close-up macro framing of glowing lanterns beside the {theme} pool, "
                f"floating pink lotus blossoms on glassy turquoise water, gentle surface ripples reflecting warm golden light, "
                f"creamy optical bokeh background with lush bamboo stalks, Arri Alexa 85mm portrait lens at f/1.4, zero people."
            ),
            "motion_prompt": "Smooth liquid surface displacement with gentle expanding circular wavelets, soft lantern flicker reflection, 24fps.",
            "dialogue": "Every droplet and soft reflection creates a calm space to breathe and rejuvenate your mind.",
        },
        {
            "scene_index": 3,
            "duration_seconds": dur_per_scene,
            "shot_type": "wide_shot",
            "motion_domain": "landscape_solid",
            "motion_type": "steadycam_vista",
            "camera_movement": "slow_zoom_out",
            "visual_prompt": (
                f"Raw cinematic 35mm film photograph, grand atmospheric evening perspective of the entire {theme}, "
                f"soft twilight sky with warm ambient lanterns illuminating the patio lounge and surrounding botanical canopy, "
                f"serene peaceful stillness, Arri Alexa 24mm cinema prime lens at f/4.0, zero people."
            ),
            "motion_prompt": "Tranquil slow camera pull-back revealing the full peaceful luxury retreat illuminated in the evening glow, 24fps.",
            "dialogue": "May this tranquil haven bring peace, focus, and deep restful relaxation into your day.",
        },
    ]

    return {
        "title_en": theme.lower().replace(" ", "_"),
        "title_localized": theme,
        "hook_thesis": f"Experience pure 4K tranquil immersion at the {theme}.",
        "recommended_fps": 24,
        "vocal_gender": "none",
        "suno_tags": suno_tags,
        "characters": [],
        "scenes": scenes[:scenes_count],
    }


async def generate_nature_storyboard_gemini(
    theme: str = "Rainforest Waterfall Patio",
    duration_seconds: float = 20.0,
    scenes_count: int = 4,
    language: str = "en",
    user_id: str = "user_krishna_01",
) -> dict[str, Any]:
    """Dynamically generate novel nature storyboard via Gemini with pre-flight topic deduplication."""
    from src.mcp.topic_memory.server import check_topic_duplicate
    topic_check = await check_topic_duplicate(
        topic=theme,
        metadata={"genre": "nature_retreat", "format": "4k_cinematic", "theme": theme},
        final_story=theme,
        user_id=user_id,
        threshold=0.80,
    )
    if topic_check.get("is_duplicate"):
        raise ValueError(topic_check.get("alert_message") or f"Duplicate retreat topic detected: '{theme}'")

    try:
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        from src.compositor.pipeline_prompts import build_storyboard_prompt
        llm = GeminiLLMAdapter()
        prompt = build_storyboard_prompt(
            title=theme,
            duration_seconds=int(duration_seconds),
            language=language,
            fmt_str="cozy_ambient_retreat",
            genre="nature_retreat",
            idea=f"Opulent biophilic {theme} with cascading waterfall, warm glowing lanterns, and 48kHz nature soundscape.",
        )
        data = await llm.generate_structured(prompt)
        if data and data.get("scenes"):
            return data
    except Exception as ex:
        from src.core.telemetry import logger
        logger.warning(f"gemini_storyboard_fallback: {ex}. Using deterministic directorial storyboard.")

    return generate_nature_storyboard(theme=theme, duration_seconds=duration_seconds, scenes_count=scenes_count, language=language)


__all__ = ["generate_nature_storyboard", "generate_nature_storyboard_gemini"]

