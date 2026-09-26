"""Seasonal, hearth, and deep sleep ambient archetype definitions."""

from typing import Dict
from src.studios.ambient_world.archetype_model import AtmosphericArchetype


SEASONAL_HEARTH_ARCHETYPES: Dict[str, AtmosphericArchetype] = {
    "fireplace": AtmosphericArchetype(
        key="fireplace",
        display_name="Rustic Stone Hearth & Crackling Embers",
        cluster="cozy_hearth",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a grand rustic stone fireplace with roaring warm amber flames in a cozy cedar cabin. "
            "Stack of split pine firewood, wool rug, soft warm ambient lighting, peaceful evening atmosphere, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm macro perspective of glowing red-hot pine embers and dancing yellow flames inside stone hearth."
        ),
        wide_motion_prompt=(
            "Gentle natural dance of warm flames, slow rising heat shimmers, soft ember glow pulsing, calm stationary camera."
        ),
        intimate_motion_prompt=(
            "Slow hypnotic flicker of campfire embers, subtle micro-sparks rising, warm comforting stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], deep soothing wood fireplace crackle, soft warm acoustic guitar, anti-fatigue sleep master, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["fireplace", "fire", "hearth", "cozy", "asmr"],
    ),
    "night_sky": AtmosphericArchetype(
        key="night_sky",
        display_name="Luminous Full Moon & Deep Starlit Night",
        cluster="deep_sleep",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a luminous full moon illuminating soft ethereal clouds and starry night sky. "
            "Deep velvet indigo atmosphere, distant mountain silhouette bathed in silvery moonlight, serene cosmos, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of cozy candle lantern glowing on dark wooden windowsill looking out into starlit night."
        ),
        wide_motion_prompt=(
            "Ultra-slow graceful drift of silvery clouds across luminous moon, subtle twinkling stars, hypnotic tranquil camera."
        ),
        intimate_motion_prompt=(
            "Soft warm flicker of candle flame, gentle moonlight reflection on window glass, deeply peaceful stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], deep delta wave sleep music, 432Hz solfeggio drone, warm ambient synth pads, soft night foley, "
            "deep sleep master, -22 LUFS anti-fatigue"
        ),
        default_domain="landscape_solid",
        tags=["night", "sleep", "moon", "stars", "delta_waves"],
    ),
    "blizzard": AtmosphericArchetype(
        key="blizzard",
        display_name="Cozy Timber Cabin in Mountain Blizzard",
        cluster="cozy_hearth",
        wide_visual_prompt=(
            "Masterpiece 4K photograph from inside a warm timber cabin looking out large bay window at snowstorm blizzard. "
            "Frost crystals on window corners, swirling snow outside, warm stone fireplace glowing inside, knitted blanket on chair, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm framing of delicate frost lace on double-pane glass with warm glowing fireplace reflection inside."
        ),
        wide_motion_prompt=(
            "Swirling blizzard snow outside cabin window, steady warm amber firelight glowing inside, calm stationary perspective."
        ),
        intimate_motion_prompt=(
            "Soft dancing firelight flickering across window frost, gentle outside snow drift, deeply comforting stillness."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], muted arctic blizzard wind outside, cozy stone fireplace crackle inside, warm acoustic cello, "
            "comforting sleep master, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["blizzard", "cabin", "snow", "fireplace", "cozy"],
    ),
    "winter": AtmosphericArchetype(
        key="winter",
        display_name="Pristine Winter Forest & Snowfall",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a serene winter forest with heavy pristine snow on pine boughs and frozen crystalline brook. "
            "Soft gentle snowflakes falling peacefully through crisp winter air, soft blue-white winter light, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait of perfect hexagonal snowflakes resting on deep green pine needles, glistening ice crystals."
        ),
        wide_motion_prompt=(
            "Slow hypnotic vertical drift of fluffy snowflakes through winter pines, tranquil stillness, stationary camera."
        ),
        intimate_motion_prompt=(
            "Gentle snowflakes settling on pine bough, delicate winter sparkle in soft daylight, calm stationary view."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], soft gentle snowfall stillness, muted winter atmosphere, warm acoustic piano and crystal chimes, "
            "432Hz sleep tuning, anti-fatigue master"
        ),
        default_domain="landscape_solid",
        tags=["winter", "snow", "forest", "peaceful", "silence"],
    ),
    "autumn": AtmosphericArchetype(
        key="autumn",
        display_name="Golden Autumn Foliage & River Stream",
        cluster="forest_seasonal",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a vibrant autumn forest with golden yellow, amber, and crimson maple trees along a clear river. "
            "Fallen autumn leaves floating on clear water surface, mossy rocks, warm golden afternoon sunlight, 35mm lens, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm perspective of crisp golden and red maple leaf resting on smooth wet river pebble with clear water flowing by."
        ),
        wide_motion_prompt=(
            "Gentle autumn leaves slowly drifting down from maple trees, tranquil river current carrying floating leaves, calm camera."
        ),
        intimate_motion_prompt=(
            "Delicate water ripple parting around fallen autumn leaf, golden sunlight sparkle on clear stream, peaceful motion."
        ),
        acoustic_tags=(
            "[velvet acoustic ambient], gentle autumn breeze rustling dry leaves, soft flowing brook, acoustic guitar and Celtic harp, "
            "warm biophilic grounding, -21 LUFS sleep master"
        ),
        default_domain="water_fluid",
        tags=["autumn", "leaves", "river", "golden", "nature"],
    ),
}
