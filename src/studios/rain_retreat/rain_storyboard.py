"""Directorial Storyboard Generator for Rain Retreat & River ASMR."""

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
        "Continuous steady rainfall with realistic vertical raindrops hitting the water surface, fluid river current flowing gently downstream, "
        "expanding water droplet ripples across the stream surface, subtle swaying wet foliage in the forest breeze, calm stationary camera."
    )

    p2_visual = (
        f"Macro close-up 50mm perspective of pristine rain droplets falling on calm river water in {theme}. "
        "Razor-sharp focus on expanding circular ripples on translucent emerald water, smooth river pebbles visible below, "
        "overhanging wet cedar leaves dripping sparkling raindrops. Soft forest background with gentle misty bokeh, ultra-detailed water physics, zero humans."
    )
    p2_motion = (
        "Hypnotic expanding circular water ripples from falling raindrops, sparkling water reflections, delicate water drops falling from green leaves, "
        "smooth laminar liquid physics, stationary close-up camera with zero camera shake."
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
