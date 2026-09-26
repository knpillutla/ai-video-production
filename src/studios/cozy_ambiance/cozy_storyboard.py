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
