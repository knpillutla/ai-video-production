"""Directorial Storyboard Generator for Ambient World & Sleep Productions.

Autonomously derives master duration (60s vs 120s) and shot count (2 vs 3 vs 4 shots) based on the atmospheric archetype and relaxation context.
"""

from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from src.core.telemetry import logger
from src.studios.ambient_world.ambient_catalog import ARCHETYPES, AtmosphericArchetype


class AmbientScenePrompt(BaseModel):
    """Scene prompt specification for an ambient production."""
    scene_index: int
    perspective_type: str  # wide_atmospheric, intimate_macro, mid_environmental, golden_canopy
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"


class AmbientStoryboard(BaseModel):
    """Directorial storyboard for Ambient & Relaxation productions."""
    title: str
    primary_archetype: str
    secondary_archetype: Optional[str] = None
    cluster: str
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str
    scenes: List[AmbientScenePrompt] = Field(default_factory=list)


def resolve_archetype(key_or_name: str) -> AtmosphericArchetype:
    """Resolve archetype key from slug or fuzzy name."""
    clean = key_or_name.lower().strip().replace("-", "_").replace(" ", "_")
    if clean in ARCHETYPES:
        return ARCHETYPES[clean]
    for k, arch in ARCHETYPES.items():
        if k in clean or clean in k or arch.display_name.lower() in clean:
            return arch
    return ARCHETYPES["swiss_alps"]


def resolve_contextual_defaults(cluster: str, user_duration: Optional[float], user_shots: Optional[int]) -> Tuple[float, int, str]:
    """Autonomously determine optimal master duration and shot count with explicit directorial rationale."""
    if user_duration is None:
        if cluster in ("alpine", "aquatic", "forest_seasonal"):
            dur, default_shots = 120.0, 4
            rationale = "Scenic Nature & Mountain Retreat: 120s master across 4 distinct perspectives (Panoramic Valley, Alpine Stream/Meadow, Macro Flora/Texture, Golden Ridge) to deliver dynamic scenic progression and eliminate visual fatigue over multi-hour broadcasts."
        elif cluster in ("deep_sleep", "cozy_hearth"):
            dur, default_shots = 90.0, 3
            rationale = "Deep Sleep & Insomnia Sanctuary: 90s master across 3 steady hypnotic perspectives (Wide Snowy Cabin Exterior, Warm Hearth Ember Macro, Cozy Bedside/Window Nook) to maximize continuous tranquility and rich visual atmosphere."
        else:
            dur, default_shots = 90.0, 3
            rationale = "Study Focus & Cozy Cafe: 90s master across 3 cozy focal zones (Ambient Window Desk, Steaming Mug Macro, Rainy Glass Nook) to maintain calm flow-state immersion."
    else:
        dur = user_duration
        if cluster in ("deep_sleep", "cozy_hearth"):
            default_shots = 3
            rationale = f"Custom Duration {dur}s in Deep Sleep: Utilizing 3 long, hypnotic shots ({dur/3:.1f}s each) to protect delta-wave entrainment."
        elif dur <= 60.0:
            default_shots = 2
            rationale = f"Custom Duration {dur}s: Using 2 balanced perspectives (Wide Atmospheric + Intimate Macro) for compact loop cadence."
        elif cluster in ("alpine", "aquatic", "forest_seasonal"):
            default_shots = 4
            rationale = f"Custom Duration {dur}s in Nature Retreat: Utilizing 4 progressive angles ({dur/4:.1f}s each) for comprehensive scenic coverage."
        else:
            default_shots = 3
            rationale = f"Custom Duration {dur}s in Focus Setting: Utilizing 3 balanced focal angles ({dur/3:.1f}s each)."

    shots = user_shots if (user_shots and user_shots in (1, 2, 3, 4)) else default_shots
    if shots == 1 and user_duration is None:
        dur = 30.0
        rationale = "Single Shot Minimalist Master: 1 steady hypnotic living wallpaper perspective (30s loop) for uninterrupted tranquility."
    return dur, shots, rationale


def generate_ambient_storyboard(
    primary: str = "swiss_alps",
    secondary: Optional[str] = None,
    custom_title: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    num_shots: Optional[int] = None,
) -> AmbientStoryboard:
    """Generate adaptive directorial storyboard tailored to duration and retreat context."""
    arch1 = resolve_archetype(primary)
    arch2 = resolve_archetype(secondary) if secondary else None
    
    total_dur, shots_count, rationale = resolve_contextual_defaults(arch1.cluster, duration_seconds, num_shots)
    shot_dur = round(total_dur / shots_count, 1)

    logger.info(f"directorial_decision: archetype='{arch1.key}' cluster='{arch1.cluster}' duration={total_dur}s shots={shots_count} shot_dur={shot_dur}s custom_prompt={bool(custom_prompt)}")
    logger.info(f"decision_rationale: {rationale}")
    print(f"\n[AGENT DIRECTORIAL DECISION]")
    print(f"   * Theme / Cluster:     {arch1.display_name} ({arch1.cluster.upper()})")
    print(f"   * Master Set Duration: {int(total_dur)}s ({shots_count} Shot{'s' if shots_count > 1 else ''} @ {shot_dur}s each)")
    if custom_prompt:
        print(f"   * Custom Mood Prompt:  \"{custom_prompt.strip()}\"")
    print(f"   * Strategic Rationale: {rationale}\n")

    title = custom_title or (f"{arch1.display_name} with {arch2.display_name}" if (arch2 and arch2.key != arch1.key) else arch1.display_name)
    audio_tags = f"{arch1.acoustic_tags}" + (f", layered with {arch2.display_name.lower()} velvet foley" if arch2 else "")

    scenes: List[AmbientScenePrompt] = []

    # Shot 1: Wide establishing atmospheric perspective or customized single shot
    if shots_count == 1 and custom_prompt:
        s1_vis = f"Masterpiece 4K photograph of {custom_prompt.strip()}. Warm cinematic natural lighting, 50mm lens, 8k resolution, zero humans, photorealistic detail."
        s1_motion = f"Ultra-slow organic motion of {custom_prompt.strip()}, rock-steady camera perspective, zero rapid movement, zero timelapse, peaceful living wallpaper."
    else:
        s1_vis = f"{arch1.wide_visual_prompt}" + (f" Blended with {arch2.display_name.lower()} atmosphere." if arch2 else "")
        s1_motion = arch1.wide_motion_prompt
        if custom_prompt:
            s1_vis += f" Accented with {custom_prompt.strip()}."
            s1_motion += f" Featuring {custom_prompt.strip()}."

    scenes.append(AmbientScenePrompt(
        scene_index=1, perspective_type="wide_atmospheric", visual_prompt=s1_vis,
        motion_prompt=s1_motion, duration_seconds=shot_dur, domain=arch1.default_domain,
    ))
    print(f"   [Shot 1 / Wide Establishing] Scale: Monumental panorama to establish deep environmental immersion.")

    # Shot 2 (if 2, 3, or 4 shots): Intimate macro / focal detail perspective
    if shots_count >= 2:
        s2_vis = (arch2.intimate_visual_prompt if arch2 else arch1.intimate_visual_prompt)
        scenes.append(AmbientScenePrompt(
            scene_index=2, perspective_type="intimate_macro", visual_prompt=s2_vis,
            motion_prompt=(arch2.intimate_motion_prompt if arch2 else arch1.intimate_motion_prompt),
            duration_seconds=shot_dur,
            domain="water_fluid" if any(k in f"{primary} {secondary}" for k in ("rain", "beach", "ocean", "river", "lake")) else "landscape_solid",
        ))
        print(f"   [Shot 2 / Intimate Macro] Sensory: Tactile micro-textures (rain droplets, water ripples, hearth embers) for soothing focus.")

    # Shot 3 (if 3 or 4 shots): Contextual third perspective
    if shots_count >= 3:
        if arch1.cluster in ("deep_sleep", "cozy_hearth"):
            s3_vis = (
                f"Masterpiece 4K photograph of a cozy rustic cabin interior reading nook with a frosted panoramic window looking out at gentle night snowfall. "
                f"Warm glowing amber candlelight and soft wool throw blanket on deep leather armchair, steaming mug on cedar side table, extreme coziness, 50mm portrait lens, 8k resolution, zero humans."
            )
            s3_motion = "Gentle dancing candlelight flame, soft snowfall drifting peacefully outside frosted window pane, warm steady cozy interior perspective, zero timelapse."
            domain_s3 = "landscape_solid"
            shot3_title = "Cozy Hearth Nook & Frosted Window"
        elif arch1.cluster in ("alpine", "aquatic", "forest_seasonal"):
            s3_vis = (
                f"Masterpiece 4K photograph of a serene turquoise glacial mountain lake reflecting towering granite alpine peaks, "
                f"dense emerald green pine forest, smooth natural shoreline pebbles, soft 5400K natural daylight, 50mm lens, 8k resolution, zero humans, zero buildings."
            )
            s3_motion = "Ultra-slow calm glassy water ripples on lake surface, barely perceptible mountain breeze in pine branches, rock-steady tripod camera, zero timelapse."
            domain_s3 = "water_fluid"
            shot3_title = "Glacial Lake & Pines"
        else:
            s3_vis = (
                f"Masterpiece 4K photograph of an intimate rainy cafe window nook, raindrops trickling down glass, warm ambient interior lights, soft bokeh, 50mm lens, 8k resolution, zero humans."
            )
            s3_motion = "Slow gentle rain droplets trickling down window glass, warm soothing cafe ambient lights in soft blur, peaceful stationary camera, zero timelapse."
            domain_s3 = "water_fluid"
            shot3_title = "Rainy Glass Nook"

        scenes.append(AmbientScenePrompt(
            scene_index=3, perspective_type="mid_environmental", visual_prompt=s3_vis,
            motion_prompt=s3_motion, duration_seconds=shot_dur, domain=domain_s3,
        ))
        print(f"   [Shot 3 / {shot3_title}] Setting: Atmospheric {shot3_title.lower()} to enrich visual depth.")

    # Shot 4 (if 4 shots): Atmospheric golden canopy / high ridge sunset horizon
    if shots_count >= 4:
        s4_vis = (
            f"Masterpiece 4K panoramic golden hour photograph of high alpine mountain pass with warm amber twilight light washing over the peaks and ridges. "
            f"Ethereal low-hanging mountain mist, tranquil stillness, 35mm Arri cinematography, 8k resolution, zero humans, zero buildings."
        )
        scenes.append(AmbientScenePrompt(
            scene_index=4, perspective_type="golden_canopy", visual_prompt=s4_vis,
            motion_prompt="Ultra-slow tranquil amber twilight glow over high mountain ridges, almost stationary mist in the valley, steady peaceful perspective, zero timelapse.",
            duration_seconds=shot_dur, domain="landscape_solid",
        ))
        print(f"   [Shot 4 / Golden Ridge] Lighting: Warm amber twilight shift to eliminate visual monotony.\n")

    return AmbientStoryboard(
        title=title, primary_archetype=arch1.key, secondary_archetype=arch2.key if arch2 else None,
        cluster=arch1.cluster, total_duration=total_dur, recommended_fps=24,
        audio_tags=audio_tags, scenes=scenes,
    )
