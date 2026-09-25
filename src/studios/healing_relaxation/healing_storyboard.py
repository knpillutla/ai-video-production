"""Directorial Storyboard Generator for Healing Meditation & Relaxing Music."""

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
        "Subtle tranquil morning mist slowly drifting across the glassy lotus pond, very gentle water ripple reflecting dawn light, "
        "soft swaying cherry blossom branches in the peaceful breeze, slow meditative stationary camera with zero camera shake."
    )

    p2_visual = (
        f"Close-up 50mm portrait perspective of blooming sacred pink lotus flowers floating on crystal water in {theme}. "
        "Razor-sharp focus on glowing pink and white lotus petals with delicate translucent water droplets, smooth emerald lily pads, "
        "and clear water revealing smooth submerged river stones below. Soft golden sunrise bokeh in the background, pure serenity, zero humans."
    )
    p2_motion = (
        "Delicate water movement gently cradling the floating lotus flower, shimmering golden morning light glinting on water droplets, "
        "soft harmonic background breathing, calm stationary camera."
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
