"""Directorial Storyboard Generator for Ambient World & Sleep Productions.

Autonomously derives master duration (60s vs 120s) and shot count (2 vs 3 vs 4 shots) based on the atmospheric archetype and relaxation context.
"""

import json
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator
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
    story_topic: Optional[str] = ""
    primary_archetype: str
    secondary_archetype: Optional[str] = None
    cluster: str
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: str = ""
    scenes: List[AmbientScenePrompt] = Field(default_factory=list)

    @field_validator("audio_tags", mode="before")
    @classmethod
    def normalize_audio_tags(cls, v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        return str(v) if v is not None else ""


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
    camera_motion: Optional[str] = "locked_tripod",
) -> AmbientStoryboard:
    """Generate adaptive directorial storyboard tailored to duration, shots count, and camera motion style."""
    arch1 = resolve_archetype(primary)
    arch2 = resolve_archetype(secondary) if secondary else None
    
    total_dur, shots_count, rationale = resolve_contextual_defaults(arch1.cluster, duration_seconds, num_shots)
    shot_dur = round(total_dur / shots_count, 1)

    logger.info(f"directorial_decision: archetype='{arch1.key}' cluster='{arch1.cluster}' duration={total_dur}s shots={shots_count} shot_dur={shot_dur}s camera_motion='{camera_motion}' custom_prompt={bool(custom_prompt)}")
    print(f"\n[AGENT DIRECTORIAL DECISION]")
    print(f"   * Theme / Cluster:     {arch1.display_name} ({arch1.cluster.upper()})")
    print(f"   * Master Set Duration: {int(total_dur)}s ({shots_count} Shot{'s' if shots_count > 1 else ''} @ {shot_dur}s each)")
    print(f"   * Camera Style:        {camera_motion or 'locked_tripod'}")
    if custom_prompt:
        print(f"   * Custom Mood Prompt:  \"{custom_prompt.strip()}\"")
    print(f"   * Strategic Rationale: {rationale}\n")

    title = custom_title or (f"{arch1.display_name} with {arch2.display_name}" if (arch2 and arch2.key != arch1.key) else arch1.display_name)
    audio_tags = f"{arch1.acoustic_tags}" + (f", layered with {arch2.display_name.lower()} velvet foley" if arch2 else "")

    scenes: List[AmbientScenePrompt] = []

    # Derive base motion modifier based on user camera selection
    if camera_motion == "slow_steadycam":
        motion_prefix = "Ultra-slow tranquil steadycam walking cadence (~1.5 km/h) with subtle organic sway, smooth leisurely forward glide. "
    elif camera_motion == "aerial_crane":
        motion_prefix = "Slow cinematic aerial crane descent over natural landscape, gentle smooth forward glide, deep optical depth of field. "
    elif camera_motion == "locked_tripod":
        motion_prefix = "Fixed locked tripod camera, completely stationary camera perspective, zero camera movement, zero panning, zero zooming. Pure environmental micro-motion: "
    else:
        motion_prefix = ""

    p_lower = (custom_prompt or "").lower()
    has_rain = any(k in p_lower for k in ("rain", "raining", "rainfall", "raindrop", "drizzle", "downpour", "shower")) or (arch2 and arch2.key == "rain")
    has_snow = any(k in p_lower for k in ("snow", "snowing", "blizzard", "frost", "winter")) or (arch2 and arch2.key == "blizzard")

    purity_vis = "zero humans, zero cars, zero vehicles, zero vans, zero trucks, zero traffic, zero modern street clutter, untouched natural alpine scenery, pristine wilderness setting."
    purity_motion = "zero cars, zero vehicles, zero moving vans, zero people, zero modern traffic. "

    rain_vis = "gentle steady rainfall over the landscape, glistening wet stone rooftops, rain droplets falling from wooden eaves, dewdrops on lush green grass and alpine wildflowers, soft overcast rainy daylight, " if has_rain else ""
    rain_motion = "Continuous gentle steady rainfall with visible fine rain streaks falling smoothly, soft water droplet ripples on wet ground and puddles, calm breeze swaying wet grass and pine branches. " if has_rain else ""

    # Shot 1: Wide establishing atmospheric perspective or customized single shot
    if shots_count == 1 and custom_prompt:
        s1_vis = f"Masterpiece 4K photograph of {custom_prompt.strip()}. {rain_vis}Warm cinematic natural 5400K daylight, 50mm lens, 8k resolution, {purity_vis}"
        s1_motion = f"{motion_prefix or 'Fixed locked tripod camera, zero camera movement. '}{rain_motion}{purity_motion}gentle breeze swaying foliage and wildflowers, natural water ripples, peaceful living wallpaper."
    else:
        s1_vis = f"{arch1.wide_visual_prompt}" + (f" Blended with {arch2.display_name.lower()} atmosphere." if arch2 else "")
        s1_motion = f"{motion_prefix}{arch1.wide_motion_prompt}" if motion_prefix else arch1.wide_motion_prompt
        if custom_prompt:
            s1_vis += f" Featuring {custom_prompt.strip()}. {rain_vis}{purity_vis}"
            s1_motion += f" Featuring {custom_prompt.strip()} with locked stationary camera framing. {rain_motion}{purity_motion}"
        else:
            s1_vis += f" {purity_vis}"
            s1_motion += f" {purity_motion}"

    s1_domain = "water_fluid" if (has_rain or arch1.default_domain == "water_fluid") else arch1.default_domain

    scenes.append(AmbientScenePrompt(
        scene_index=1, perspective_type="wide_atmospheric", visual_prompt=s1_vis,
        motion_prompt=s1_motion, duration_seconds=shot_dur, domain=s1_domain,
    ))

    # Shot 2 (if 2, 3, or 4 shots): Intimate macro / focal detail perspective
    if shots_count >= 2:
        s2_vis = (arch2.intimate_visual_prompt if arch2 else arch1.intimate_visual_prompt) + f" {purity_vis}"
        s2_motion = f"{motion_prefix}{arch2.intimate_motion_prompt if arch2 else arch1.intimate_motion_prompt} {purity_motion}" if motion_prefix else f"{arch2.intimate_motion_prompt if arch2 else arch1.intimate_motion_prompt} {purity_motion}"
        scenes.append(AmbientScenePrompt(
            scene_index=2, perspective_type="intimate_macro", visual_prompt=s2_vis,
            motion_prompt=s2_motion,
            duration_seconds=shot_dur,
            domain="water_fluid" if any(k in f"{primary} {secondary}" for k in ("rain", "beach", "ocean", "river", "lake")) or has_rain else "landscape_solid",
        ))
        print(f"   [Shot 2 / Intimate Macro] Sensory: Tactile micro-textures (rain droplets, water ripples, hearth embers) for soothing focus.")

    # Shot 3 (if 3 or 4 shots): Contextual third perspective
    if shots_count >= 3:
        if arch1.cluster in ("deep_sleep", "cozy_hearth"):
            s3_vis = (
                f"Masterpiece 4K photograph of a cozy rustic cabin interior reading nook with a frosted panoramic window looking out at gentle night snowfall. "
                f"Warm glowing amber candlelight and soft wool throw blanket on deep leather armchair, steaming mug on cedar side table, extreme coziness, 50mm portrait lens, 8k resolution, zero humans."
            )
            s3_motion = "Fixed locked tripod camera, gentle dancing candlelight flame, soft snowfall drifting peacefully outside frosted window pane, steady cozy interior perspective, zero camera movement."
            domain_s3 = "landscape_solid"
            shot3_title = "Cozy Hearth Nook & Frosted Window"
        elif arch1.cluster in ("alpine", "aquatic", "forest_seasonal"):
            s3_vis = (
                f"Masterpiece 4K photograph of a serene turquoise glacial mountain lake reflecting towering granite alpine peaks, "
                f"dense emerald green pine forest, smooth natural shoreline pebbles, soft 5400K natural daylight, 50mm lens, 8k resolution, zero humans, zero buildings."
            )
            s3_motion = "Fixed locked tripod camera, ultra-slow calm glassy water ripples on lake surface, barely perceptible mountain breeze in pine branches and flowers, zero camera movement."
            domain_s3 = "water_fluid"
            shot3_title = "Glacial Lake & Pines"
        else:
            s3_vis = (
                f"Masterpiece 4K photograph of an intimate rainy cafe window nook, raindrops trickling down glass, warm ambient interior lights, soft bokeh, 50mm lens, 8k resolution, zero humans."
            )
            s3_motion = "Fixed locked tripod camera, slow gentle rain droplets trickling down window glass, warm soothing cafe ambient lights in soft blur, peaceful stationary camera, zero camera movement."
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
            motion_prompt="Fixed locked tripod camera, ultra-slow tranquil amber twilight glow over high mountain ridges, almost stationary mist in the valley, steady peaceful perspective, zero camera movement.",
            duration_seconds=shot_dur, domain="landscape_solid",
        ))
        print(f"   [Shot 4 / Golden Ridge] Lighting: Warm amber twilight shift to eliminate visual monotony.\n")

    return AmbientStoryboard(
        title=title, primary_archetype=arch1.key, secondary_archetype=arch2.key if arch2 else None,
        cluster=arch1.cluster, total_duration=total_dur, recommended_fps=24,
        audio_tags=audio_tags, scenes=scenes,
    )


async def generate_ambient_storyboard_gemini(
    primary: str = "swiss_alps",
    secondary: Optional[str] = None,
    custom_title: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    num_shots: Optional[int] = None,
    camera_motion: Optional[str] = "locked_tripod",
    user_id: Optional[str] = "user_krishna_01",
) -> AmbientStoryboard:
    """Dynamically generate rich directorial storyboard via Gemini LLM with camera optics, weather dynamics, and acoustic scoring."""
    arch1 = resolve_archetype(primary)
    arch2 = resolve_archetype(secondary) if secondary else None
    total_dur, shots_count, rationale = resolve_contextual_defaults(arch1.cluster, duration_seconds, num_shots)
    shot_dur = round(total_dur / shots_count, 1)

    theme_seed = custom_prompt or arch1.display_name
    print(f"\n[GEMINI DIRECTORIAL AGENT INVOKED]")
    print(f"   * Creative Theme:     \"{theme_seed}\"")
    print(f"   * Master Duration:    {int(total_dur)}s ({shots_count} Shot{'s' if shots_count > 1 else ''} @ {shot_dur}s)")
    print(f"   * Camera Motion:      {camera_motion or 'locked_tripod'}")

    try:
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter()
        
        system_prompt = (
            "You are an award-winning cinematic director and acoustic sound designer for NatGeo and BBC 8K Nature Documentaries and Living Wallpapers. "
            "Generate a comprehensive, detailed multi-scene 8K UHD storyboard based on the user's theme. "
            "CRITICAL ANTI-FATIGUE & SEAMLESS 3-HOUR LONG-PLAY DIRECTIVES:\n"
            "1. NATURAL GENTLE MICRO-KINEMATICS: Motion MUST be tranquil, ultra-subtle, smooth, and organic for all environmental elements:\n"
            "   - Water Fluid: Gentle continuous ripples, slow tranquil stream currents, soft circular droplet ripples (zero violent splashes, zero boiling waves).\n"
            "   - Clouds & Mist: Dreamy, slow continuous drifting clouds and soft mountain mist (zero fast storm rushes or jarring time-lapses).\n"
            "   - Flowers & Foliage: Delicate rhythmic swaying of wildflowers and pine boughs in a faint, soothing mountain breeze.\n"
            "   - Grass & Lawns: Subtle, gentle undulating wave motion across alpine meadows matching a light breeze.\n"
            "2. SEAMLESS 3-HOUR STRETCHING & FORWARD LOOPING COMPATIBILITY:\n"
            "   - Since 5-second video clips will be stitched and stretched into 1-hour, 3-hour, and 8-hour living wallpapers, motion vectors MUST be constant, forward-flowing, and seam-free.\n"
            "   - Camera MUST be locked-tripod (or ultra-slow steadycam <=0.5 m/s) with 100% rock-solid background structures (chalets, mountains, rocks, trees) so only natural fluid elements gently move.\n"
            "   - Strictly prohibit rapid panning, sudden zooms, erratic motion, high-frequency jitters, flashing lights, or fast object movements that cause visual fatigue.\n"
            "3. ANTI-FATIGUE ACOUSTIC MASTERING: Audio/music MUST feature warm, soft acoustic textures, smooth harmonic pads, gentle low-pass rolloff, and -14.0 LUFS velvet mastering. Strictly prohibit harsh high frequencies (>8 kHz sharp hiss), jarring percussion, repetitive sharp loops, sudden volume spikes, or discordant sounds that cause ear fatigue.\n"
            "4. MANDATORY PURE NATURE PURITY GUARD (ZERO VEHICLES, ZERO HUMANS, ZERO ANIMALS BY DEFAULT):\n"
            "   - In all relaxation/nature themes, unless explicitly requested in the user's prompt, mandate pure untouched nature with: 'zero humans, zero people, zero persons, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero asphalt roads, zero modern clutter, zero animals, zero wildlife, zero birds, zero pets, zero livestock, pristine untouched natural landscape'.\n"
            "For visual prompts: Mandate Arri/Hasselblad 35mm cinematographic specifications, 8K UHD master resolution, exact focal lengths, f-stops (f/1.4, f/2.8, f/8.0), lighting color temperature (5400K natural daylight), "
            "tactile micro-textures (wet stone shingles, dewdrops, moss, rain ripples), and the mandatory pure nature purity guard. "
            "For motion prompts: Mandate exact smooth fluid displacement (fine rain streaks, gentle water ripples, slow drifting clouds/mist, subtle grass and wildflower sway) and steady camera rules. "
            "Return valid JSON only matching the schema."
        )

        user_msg = (
            f"Generate a {shots_count}-shot 8K UHD anti-fatigue ambient video storyboard for theme: '{theme_seed}'.\n"
            f"Cluster: {arch1.cluster}. Camera Motion Style: {camera_motion or 'locked_tripod'}.\n"
            f"Duration per shot: {shot_dur} seconds. Total Duration: {total_dur} seconds.\n"
            f"Purity Guard: Pure untouched nature (zero vehicles, zero humans, zero animals unless specified in theme).\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': High-CTR evocative YouTube title\n"
            f"- 'story_topic': Poetic environmental lore and tranquil scene context\n"
            f"- 'audio_tags': Commercially cleared Velvet 432Hz anti-fatigue ambient acoustic tags (warm piano, gentle pads, binaural nature foley, zero harshness)\n"
            f"- 'scenes': Array of {shots_count} scene objects each containing:\n"
            f"    - 'scene_index': int (1..{shots_count})\n"
            f"    - 'perspective_type': string ('wide_atmospheric', 'intimate_macro', 'mid_environmental', 'twilight_haven')\n"
            f"    - 'visual_prompt': detailed 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': smooth anti-fatigue video motion prompt for Wan 2.1 / Kling (gentle water ripples, slow clouds, subtle grass/flower sway, locked framing for seamless 3h looping)\n"
            f"    - 'duration_seconds': {shot_dur}\n"
            f"    - 'domain': 'water_fluid' if scene has rain/water else 'landscape_solid'\n"
        )

        full_gemini_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_request_sent: theme='{theme_seed}' shots={shots_count}\n--- PROMPT SENT TO GEMINI ---\n{full_gemini_prompt}\n-----------------------------")
        print(f"\n[GEMINI DIRECTORIAL REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_gemini_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_gemini_prompt)
        logger.info(f"gemini_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI DIRECTORIAL RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= shots_count:
            parsed_scenes = []
            for idx, sc in enumerate(data["scenes"][:shots_count]):
                parsed_scenes.append(AmbientScenePrompt(
                    scene_index=idx + 1,
                    perspective_type=sc.get("perspective_type", "wide_atmospheric"),
                    visual_prompt=sc.get("visual_prompt", ""),
                    motion_prompt=sc.get("motion_prompt", ""),
                    duration_seconds=shot_dur,
                    domain=sc.get("domain", "landscape_solid" if "rain" not in theme_seed.lower() else "water_fluid"),
                ))
            
            sb = AmbientStoryboard(
                title=data.get("title") or custom_title or arch1.display_name,
                story_topic=data.get("story_topic") or custom_title or arch1.display_name,
                primary_archetype=primary,
                secondary_archetype=secondary,
                cluster=arch1.cluster,
                total_duration=total_dur,
                recommended_fps=24,
                audio_tags=data.get("audio_tags") or arch1.acoustic_tags,
                scenes=parsed_scenes,
            )
            logger.info(f"gemini_storyboard_synthesized: title='{sb.title}' scenes={len(sb.scenes)}")
            print(f"[GEMINI STORYBOARD SUCCESS] Synthesized '{sb.title}' with {len(sb.scenes)} custom directorial scenes.")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed storyboard data: {data}")
    except Exception as ex:
        logger.error(f"gemini_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini directorial screenplay generation failed: {ex}") from ex


__all__ = ["AmbientScenePrompt", "AmbientStoryboard", "generate_ambient_storyboard", "generate_ambient_storyboard_gemini"]
