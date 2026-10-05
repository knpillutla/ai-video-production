"""Desert Studio Diurnal Atmospheric Archetypes Catalog.

Encapsulates 6 distinct diurnal timings and sensory settings for desert living wallpapers:
1. Daytime Luxury Tent (5500K crisp daylight, sheer linen curtains, sunlit dunes)
2. Sunrise Dawn Tent (3800K pastel peach/amber, first sun rays, steaming tea)
3. Sunset Golden Hour Tent (2800K fiery terracotta, long dune shadows, evening peace)
4. Starlit Night Tent (Deep indigo, Milky Way galaxy, soft candle lantern, zero fire)
5. Night Campfire & Hearth (2200K pulsing embers, open-air Bedouin stone hearth, starlight)
6. Rare Desert Rain on Tent (4800K overcast, rain on canvas ASMR, petrichor, damp sand)
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class AtmosphericArchetype(BaseModel):
    """Detailed visual, motion, and acoustic profile for a desert environment."""
    key: str
    display_name: str
    cluster: str = "desert"
    wide_visual_prompt: str
    intimate_visual_prompt: str
    wide_motion_prompt: str
    intimate_motion_prompt: str
    acoustic_tags: str
    default_domain: str = "landscape_solid"
    tags: List[str] = Field(default_factory=list)


DESERT_ARCHETYPES: Dict[str, AtmosphericArchetype] = {
    "desert_daytime_tent": AtmosphericArchetype(
        key="desert_daytime_tent",
        display_name="Luxury Desert Tent & Daytime Dunes",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward through the open entrance of an ultra-luxury desert glamping pavilion "
            "onto vast majestic golden sand dunes in natural daytime sunlight. Sheer cream linen draperies billow gently at the frame edges. "
            "Inside the shaded pavilion, rich hand-woven Berber kilim rugs, plush geometric floor cushions, and a low carved wooden table "
            "with an ornate Moroccan brass tea set. Outside, sculptured undulating golden sand dunes with delicate wind-carved ripples stretch endlessly "
            "under a crystal-clear cerulean blue sky in balanced 5500K natural daylight. Symmetrical 16:9 cinematic framing, shot on a locked tripod, "
            "35mm Arri cinematography, zero tourists, zero footprints, zero modern clutter, zero vehicles."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an ornate engraved Moroccan brass teapot and mint tea glasses on a low carved wooden table "
            "inside a shaded luxury desert tent. In the background through the open cream linen drapery, sunlit golden sand dunes and pristine ripple "
            "patterns glow under bright daytime sky in creamy optical bokeh (f/1.4), serene luxurious tranquility, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle living wallpaper cinemagraph motion. Completely stationary locked tripod framing. "
            "Sheer cream linen curtains gently flutter and sway in the cool desert breeze. Subtle micro-wisps of golden sand skimming distant dune crests. "
            "The majestic sand dunes, furniture, and clear sky remain 100% rigid, frozen, and temporally stable, zero camera movement, zero panning, zero morphing."
        ),
        intimate_motion_prompt=(
            "Gentle, slow rhythmic flutter of sheer cream curtains in desert breeze, soft subtle glint of daylight on polished brass teapot, "
            "stationary tripod shot, peaceful living wallpaper cadence."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], gentle whispering desert breeze through linen, uplifting resonant handpan in major pentatonic mode, "
            "crystalline singing bowls, airy wooden nay flute, warm 432Hz velvet pads, deep stress relief, peaceful restful focus, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "daytime", "sand_dunes", "luxury_tent", "glamping", "sheer_curtains", "432hz", "asmr"],
    ),
    "desert_sunrise_tent": AtmosphericArchetype(
        key="desert_sunrise_tent",
        display_name="Luxury Desert Tent & Sunrise Dawn",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward through the open drape of an ultra-luxury desert glamping pavilion at early morning dawn. "
            "The first radiant rays of the rising sun crest over towering curved golden sand dunes, casting long soft shadows and illuminating "
            "wind-sculpted ripples in warm pastel peach and soft amber light (3800K). Sheer cream linen curtains gently part to frame the vista. "
            "Inside, low carved wooden table with an engraved brass teapot and steaming glasses of mint tea, hand-woven tribal rugs. "
            "Pristine dawn sky transitioning from pale violet to warm golden radiance, locked tripod, symmetrical 16:9 framing, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of delicate morning steam gently rising from a traditional Moroccan tea glass beside an engraved brass teapot "
            "on a low table inside the open tent. Through the parted cream drapes, the golden sunrise light illuminates the distant dune crests in soft, "
            "dreamy optical bokeh (f/1.4), serene peaceful awakening, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-gentle living wallpaper cinemagraph motion. Completely stationary locked tripod. Sheer linen curtains sway softly in the crisp morning breeze. "
            "Delicate morning light caustics shift imperceptibly across dune ridges. Micro-fine wisps of steam rise from the tea glass. Sand dunes and horizon remain 100% rigid and static."
        ),
        intimate_motion_prompt=(
            "Hypnotic slow swirl of steam wisps rising into cool morning air, soft breathing flutter of tent curtain edge, rock-solid camera on tripod."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], crisp morning desert breeze, delicate steam foley, resonant dawn handpan in uplifting major mode, "
            "celestial singing bowls, airy wooden bamboo flute, 432Hz morning awakening, deep peaceful serenity, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sunrise", "dawn", "sand_dunes", "steaming_tea", "luxury_tent", "432hz", "peaceful"],
    ),
    "desert_sunset_tent": AtmosphericArchetype(
        key="desert_sunset_tent",
        display_name="Luxury Desert Tent & Sunset Golden Hour",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking out from an ultra-luxury Bedouin desert tent onto majestic sand dunes at sunset golden hour. "
            "The low sinking sun bathes the curved dunes in deep fiery terracotta, burnt orange, and warm crimson light (2800K), casting dramatic "
            "sweeping purple shadows across the desert floor. Sheer linen curtains frame the glowing horizon. Inside the tent, a warm pierced brass lantern "
            "glows gently on a low cedar table with plush crimson floor cushions. 35mm Arri cinematography, locked tripod, symmetrical 16:9 framing, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an intricately pierced brass lantern casting warm geometric candlelight patterns on an antique wooden table "
            "and crimson kilim rug. In the background, sweeping sunset-lit terracotta dunes glow beneath a burning amber twilight sky in creamy optical bokeh (f/1.4)."
        ),
        wide_motion_prompt=(
            "Living wallpaper cinemagraph. Stationary tripod perspective. Soft, rhythmic fluttering of linen curtains in evening desert wind. "
            "Gentle warm pulse of candlelight inside the lantern. Sand dunes, table, and dramatic sunset clouds remain 100% locked and temporally stable."
        ),
        intimate_motion_prompt=(
            "Slow, soothing amber pulse of lantern candlelight, delicate air movement through sheer drapes, calming twilight stationary view."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], gentle evening desert wind, soft lantern hum, grounding 432Hz ambient cello drone, "
            "resonant handpan harmonics, warm velvet synth pads, deep stress relief, evening unwinding, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sunset", "golden_hour", "terracotta_dunes", "lantern", "luxury_tent", "432hz"],
    ),
    "desert_night_tent": AtmosphericArchetype(
        key="desert_night_tent",
        display_name="Luxury Desert Tent & Starlit Night (Deep Sleep)",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward from the dark, cozy interior of a luxury desert glamping tent into a vast starlit night sky. "
            "The entrance drapes part to reveal the glittering Milky Way galaxy and millions of stars stretching across a deep velvet indigo sky (2000K). "
            "Silvery starlight gently illuminates the soft crests of dark golden sand dunes outside. Inside the shaded tent, a single dim brass candle lantern "
            "glows softly on a low wooden chest beside plush navy floor cushions. Strictly zero campfire, zero smoke, pure starlit nocturnal stillness, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait of a dim pierced brass candle lantern glowing softly with tranquil amber light on an antique chest inside the tent. "
            "Through the parted drapes, deep velvet starlit sky and glittering stars dissolve into dreamy optical bokeh (f/1.4), absolute silence, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-slow, tranquil living wallpaper cinemagraph. Completely locked tripod framing. Sheer linen curtains breathe softly in the cool night air. "
            "Slow crystalline twinkle of stars in the deep cosmos. Soft, steady lantern glow without harsh flicker. Dunes and furniture 100% frozen."
        ),
        intimate_motion_prompt=(
            "Subtle warm candle breathing flicker, gentle drift of cool night air across sheer linen, deeply hypnotic stationary view."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], deep 432Hz delta-wave sleep soundbath, celestial Tibetan singing bowls, warm velvet night pads, "
            "subtle whisper of cool night breeze, zero campfire crackle, zero drums, zero guitar, deep restful sleep master, -22 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "night", "starlight", "milky_way", "sleep", "delta_waves", "luxury_tent", "no_fire"],
    ),
    "desert_campfire_hearth": AtmosphericArchetype(
        key="desert_campfire_hearth",
        display_name="Desert Campfire & Bedouin Starlit Hearth",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a luxury open-air Bedouin desert pavilion on a high sand dune ridge at starlit midnight. "
            "Rich hand-woven Persian tribal carpets, embroidered floor cushions, intricately pierced Moroccan brass lanterns casting warm geometric shadows. "
            "Outside the pavilion canopy, a gentle circular stone hearth campfire with glowing golden embers (2200K). "
            "In the background, majestic curved golden sand dunes under a crystal-clear deep velvet indigo sky filled with the glittering Milky Way galaxy, 35mm Arri, locked tripod, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of glowing red-hot embers and delicate golden micro-sparks rising from a circular sandstone hearth. "
            "In the background, pierced brass Moroccan lanterns and sweeping starlit desert dunes glow in creamy optical bokeh (f/1.4), hypnotic cozy warmth, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle, hypnotic ambient living wallpaper motion. Perfectly steady tripod perspective. "
            "Gentle slow pulse of warm lantern glow, soft ember micro-sparks rising from stone hearth, fine silk sand wisps skimming dune crests, slow twinkling stars, rock-solid stability."
        ),
        intimate_motion_prompt=(
            "Hypnotic slow flicker of campfire embers, subtle micro-sparks ascending into cool night air, serene stationary camera."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], deep soothing desert night breeze, soft crackling cedar campfire embers, uplifting resonant handpan, "
            "airy wooden nay flute, 432Hz warm velvet pads, deep stress relief, peaceful sleep drone, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "campfire", "hearth", "bedouin", "lanterns", "stars", "sleep", "asmr"],
    ),
    "desert_rain_sanctuary": AtmosphericArchetype(
        key="desert_rain_sanctuary",
        display_name="Luxury Desert Tent & Rare Rain (Canvas ASMR)",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward from a cozy luxury desert glamping tent during a rare, gentle desert rainfall. "
            "Fine raindrops pitter-patter softly across the taut cream canvas roof and create delicate damp speckles on the golden sand dunes outside. "
            "The sky is a calm, diffused silver-slate overcast (4800K) with soft mist hovering over distant dune ridges. "
            "Inside the dry, warm tent, plush woolen blankets, steaming mint tea glasses, and sheer drapes drawn back. Symmetrical 16:9 framing, locked tripod, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm macro perspective of fresh raindrops beading on taut cream canvas tent fabric and dripping onto damp golden sand ripples. "
            "In the background, soft misty desert sand dunes under rain in creamy optical bokeh (f/1.4), rich petrichor ambiance, zero humans."
        ),
        wide_motion_prompt=(
            "Living wallpaper cinemagraph. Completely stationary locked camera. Delicate continuous raindrops falling across the frame onto the sand. "
            "Subtle water droplet vibration on canvas tent roof. Misty rain veil drifting slowly across the far horizon. Dunes and tent structure 100% frozen."
        ),
        intimate_motion_prompt=(
            "Rhythmic tiny water drops trickling down waterproof canvas seam, gentle droplet splash caustics on wet sand, calming stationary shot."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], gentle rain on canvas tent ASMR, soft distant desert thunder rumble, fresh petrichor foley, "
            "warm 432Hz ambient sleep pads, deep calming handpan resonance, anti-anxiety deep sleep master, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "rain", "rain_on_tent", "canvas_asmr", "luxury_tent", "petrichor", "sleep", "432hz"],
    ),
}

# Backward compatibility aliases
DESERT_ARCHETYPES["desert_luxury_tent"] = DESERT_ARCHETYPES["desert_daytime_tent"]
DESERT_ARCHETYPES["desert_tent"] = DESERT_ARCHETYPES["desert_daytime_tent"]
DESERT_ARCHETYPES["desert_daytime"] = DESERT_ARCHETYPES["desert_daytime_tent"]
DESERT_ARCHETYPES["desert"] = DESERT_ARCHETYPES["desert_campfire_hearth"]
DESERT_ARCHETYPES["desert_pavilion"] = DESERT_ARCHETYPES["desert_campfire_hearth"]
