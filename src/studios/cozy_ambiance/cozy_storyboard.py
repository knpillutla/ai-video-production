"""Directorial Storyboard Generator for Cozy Ambiance & Biophilic Living Spaces."""

import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.telemetry import logger


class CozyScenePrompt(BaseModel):
    """Directorial prompt definition for a single cozy ambiance scene."""
    scene_index: int
    perspective_type: str  # wide_architectural, intimate_hearth
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "water_fluid"  # water_fluid, flame_ember, rain_glass


class CozyStoryboard(BaseModel):
    """Complete 2-perspective storyboard specification for Cozy Ambiance."""
    title: str
    theme: str
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str
    scenes: List[CozyScenePrompt] = Field(default_factory=list)


def generate_cozy_storyboard(
    theme: str = "Cozy Oceanfront Terrace Fireplace & Ocean Waves",
    duration_seconds: float = 60.0,
) -> CozyStoryboard:
    """Generate the 2-perspective directorial storyboard."""
    logger.info(f"generating_cozy_storyboard: theme='{theme}' duration={duration_seconds}s")

    # Perspective 1: Wide Architectural Oceanfront Terrace
    p1_visual = (
        f"Masterpiece 4K architectural photograph of a luxurious open-air modern coastal terrace overlooking {theme}. "
        "On the right foreground, a sleek minimalist stone fireplace with glowing warm orange embers and flickering natural flames. "
        "On the teak hardwood deck, comfortable plush cream lounge sofas, a low wooden coffee table with a ceramic teapot and steaming ceramic mug, "
        "and potted tropical monstera and fiddle leaf fig plants. In the background, expansive panoramic opening looking out at rolling turquoise ocean waves "
        "crashing gently along the shoreline during golden twilight. Warm ambient interior lighting contrasting with cool ocean blues, "
        "crisp architectural lines, balanced 5400K natural daylight, photorealistic 35mm Arri Alexa cinematography, 8k resolution, zero humans."
    )
    p1_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Slow hypnotic rolling ocean waves in the background, gentle flickering flames and glowing embers in the stone fireplace, "
        "subtle soft breeze gently swaying the palm leaves, continuous fluid wave dynamics, zero abrupt motion, tranquil flow."
    )

    # Perspective 2: Intimate Hearth & Ambiance
    p2_visual = (
        f"Cozy 50mm portrait perspective of the modern stone fireplace hearth in {theme}. "
        "Crisp focus on the crackling cedar wood fire with rich dancing orange flames, glowing incandescent embers, and delicate rising heat distortion. "
        "Next to the hearth on a low rustic wooden side table sits a warm ceramic mug of chamomile tea with delicate visible steam rising. "
        "In the soft-focus optical bokeh background, continuous rolling ocean surf under a pastel twilight sky. "
        "Warm, deeply comforting ambiance, high dynamic range lighting, ultra-sharp texture details on stone and flame, zero humans."
    )
    p2_motion = (
        "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. "
        "Gentle natural flame dancing in the fireplace, incandescent wood embers softly pulsing, delicate tea steam slowly rising and dissipating, "
        "distant ocean waves gently rolling in soft bokeh background, calm stationary camera."
    )

    s1 = CozyScenePrompt(
        scene_index=1,
        perspective_type="wide_architectural",
        visual_prompt=p1_visual,
        motion_prompt=p1_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="water_fluid",
    )
    s2 = CozyScenePrompt(
        scene_index=2,
        perspective_type="intimate_hearth",
        visual_prompt=p2_visual,
        motion_prompt=p2_motion,
        duration_seconds=duration_seconds / 2.0,
        domain="water_fluid",
    )

    audio_tags = (
        f"[ambient asmr soundscape], crystal-clear ocean waves rolling on shore, cozy crackling wood fireplace embers, "
        "subtle warm acoustic piano melody, peaceful binaural 48kHz broadcast master, zero hiss, zero noise"
    )

    return CozyStoryboard(
        title=theme,
        theme=theme,
        total_duration=duration_seconds,
        recommended_fps=24,
        audio_tags=audio_tags,
        scenes=[s1, s2],
    )


async def generate_cozy_storyboard_gemini(
    theme: str = "Cozy Oceanfront Terrace Fireplace & Ocean Waves",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
) -> CozyStoryboard:
    """Dynamically generate rich 2-perspective cozy ambiance storyboard via Gemini LLM."""
    print(f"\n[GEMINI COZY AMBIANCE AGENT INVOKED]")
    print(f"   * Theme:              \"{theme}\"")
    print(f"   * Duration:           {duration_seconds}s (2 Perspectives @ {duration_seconds/2.0}s each)")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter()

        system_prompt = (
            "You are a master architectural photographer and ASMR sound designer specializing in ultra-luxury biophilic living spaces and cozy hearth sanctuaries. "
            "Generate an 8K UHD 2-perspective cinematic storyboard (Perspective 1: Wide Architectural Living Space, Perspective 2: Intimate Hearth/Macro Ambiance). "
            "CRITICAL ANTI-FATIGUE DIRECTIVES:\n"
            "- ANTI-FATIGUE VIDEO MOTION: Locked tripod framing, hypnotic ultra-slow flame dancing, gentle steam drift, slow lazy embers, zero jarring zooms, zero camera shake, zero fast movements.\n"
            "- ANTI-FATIGUE ACOUSTIC MASTERING: Warm crackling wood ASMR, soft deep cello/piano pads, 432Hz tuning, gentle room resonance, zero sharp high-frequency pops/hiss, zero sudden loud transients, velvet -14 LUFS.\n"
            "- PURE SANCTUARY PURITY GUARD: Mandate 'zero humans, zero people, zero persons, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero modern clutter, zero animals, zero pets' unless explicitly requested in the theme.\n"
            "For visual prompts: Mandate Arri Alexa 35mm cinematographic specifications, 8K UHD master resolution, exact focal lengths (35mm f/4.0, 50mm f/1.4), warm glowing ambient light, steam motes, and the pure sanctuary purity guard. "
            "Return valid JSON only matching the schema."
        )

        user_msg = (
            f"Generate an 8K UHD 2-perspective anti-fatigue cozy ambiance storyboard for theme: '{theme}'. Duration: {duration_seconds}s.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': High-CTR cozy YouTube title\n"
            f"- 'audio_tags': Anti-fatigue binaural ASMR fireplace/hearth soundscape and warm acoustic pads (zero harsh transients)\n"
            f"- 'scenes': Array of 2 scene objects each containing:\n"
            f"    - 'scene_index': int (1, 2)\n"
            f"    - 'perspective_type': 'wide_architectural' or 'intimate_hearth'\n"
            f"    - 'visual_prompt': detailed 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': hypnotic anti-fatigue video motion prompt for Wan 2.1 / Kling\n"
            f"    - 'domain': 'water_fluid' or 'landscape_solid'\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_cozy_request_sent: theme='{theme}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI COZY REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_cozy_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI COZY RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 2:
            scenes = []
            for idx, sc in enumerate(data["scenes"][:2]):
                scenes.append(
                    CozyScenePrompt(
                        scene_index=idx + 1,
                        perspective_type=sc.get("perspective_type", "wide_architectural" if idx == 0 else "intimate_hearth"),
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        duration_seconds=duration_seconds / 2.0,
                        domain=sc.get("domain", "water_fluid"),
                    )
                )

            sb = CozyStoryboard(
                title=data.get("title") or theme,
                theme=theme,
                total_duration=duration_seconds,
                recommended_fps=24,
                audio_tags=data.get("audio_tags") or "ambient asmr soundscape, cozy crackling wood fireplace, warm acoustic piano, 48kHz master",
                scenes=scenes,
            )
            print(f"[GEMINI COZY STORYBOARD SUCCESS] Synthesized '{sb.title}' with 2 custom perspectives.")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed cozy storyboard data: {data}")
    except Exception as ex:
        logger.error(f"gemini_cozy_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Cozy directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini cozy directorial screenplay generation failed: {ex}") from ex


__all__ = ["CozyScenePrompt", "CozyStoryboard", "generate_cozy_storyboard", "generate_cozy_storyboard_gemini"]
