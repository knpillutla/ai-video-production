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
            "[soothing & joyful meditation], deep soothing wood fireplace crackle, resonant handpan and warm singing bowl vibration, velvet sleep master, -21 LUFS"
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
            "[soothing & joyful meditation], gentle autumn breeze rustling dry leaves, soft flowing brook, uplifting Celtic harp and celestial chimes, "
            "warm biophilic grounding, -21 LUFS sleep master, zero guitar"
        ),
        default_domain="water_fluid",
        tags=["autumn", "leaves", "river", "golden", "nature"],
    ),
    "desert": AtmosphericArchetype(
        key="desert",
        display_name="Desert Starlit Campfire & Bedouin Pavilion",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a luxury open-air Bedouin desert pavilion on a high sand dune ridge at starlit midnight. "
            "Rich hand-woven Persian tribal carpets, embroidered floor cushions, intricately pierced Moroccan brass lanterns casting warm geometric shadows. "
            "Outside, a gentle circular stone hearth campfire with glowing golden embers. In the background, majestic curved golden sand dunes under a crystal-clear deep velvet indigo sky filled with the glittering Milky Way galaxy and shooting stars, 35mm Arri cinematography, 8k resolution, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an ornate pierced brass Moroccan lantern glowing with warm golden candlelight resting on an antique wooden chest atop a rich crimson Persian rug. "
            "In the background, soft crackling campfire embers and sweeping starlit desert sand dunes in creamy optical bokeh (f/1.4), hypnotic cozy warmth, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle, hypnotic ambient living wallpaper motion. Perfectly steady tripod perspective. "
            "Gentle slow pulse of warm lantern glow, soft ember micro-sparks rising from stone hearth, fine silk sand wisps skimming dune crests in distant desert breeze, slow twinkling stars in deep night sky, zero morphing, rock-solid stability."
        ),
        intimate_motion_prompt=(
            "Soft, rhythmic warm breathing flicker of lantern flame casting dancing amber light patterns, gentle drift of smoke wisps from campfire embers into cool night air, serene stationary camera."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], deep soothing desert night breeze, soft crackling campfire embers, uplifting resonant handpan, airy wooden nay flute, 432Hz warm velvet pads, deep stress relief, peaceful sleep drone, zero guitar, zero harshness, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sand_dunes", "bedouin", "campfire", "lanterns", "stars", "sleep", "432hz", "asmr"],
    ),
    "desert_pavilion": AtmosphericArchetype(
        key="desert_pavilion",
        display_name="Desert Starlit Campfire & Bedouin Pavilion",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph of a luxury open-air Bedouin desert pavilion on a high sand dune ridge at starlit midnight. "
            "Rich hand-woven Persian tribal carpets, embroidered floor cushions, intricately pierced Moroccan brass lanterns casting warm geometric shadows. "
            "Outside, a gentle circular stone hearth campfire with glowing golden embers. In the background, majestic curved golden sand dunes under a crystal-clear deep velvet indigo sky filled with the glittering Milky Way galaxy and shooting stars, 35mm Arri cinematography, 8k resolution, zero humans."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an ornate pierced brass Moroccan lantern glowing with warm golden candlelight resting on an antique wooden chest atop a rich crimson Persian rug. "
            "In the background, soft crackling campfire embers and sweeping starlit desert sand dunes in creamy optical bokeh (f/1.4), hypnotic cozy warmth, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle, hypnotic ambient living wallpaper motion. Perfectly steady tripod perspective. "
            "Gentle slow pulse of warm lantern glow, soft ember micro-sparks rising from stone hearth, fine silk sand wisps skimming dune crests in distant desert breeze, slow twinkling stars in deep night sky, zero morphing, rock-solid stability."
        ),
        intimate_motion_prompt=(
            "Soft, rhythmic warm breathing flicker of lantern flame casting dancing amber light patterns, gentle drift of smoke wisps from campfire embers into cool night air, serene stationary camera."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], deep soothing desert night breeze, soft crackling campfire embers, uplifting resonant handpan, airy wooden nay flute, 432Hz warm velvet pads, deep stress relief, peaceful sleep drone, zero guitar, zero harshness, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sand_dunes", "bedouin", "campfire", "lanterns", "stars", "sleep", "432hz", "asmr"],
    ),
    "desert_luxury_tent": AtmosphericArchetype(
        key="desert_luxury_tent",
        display_name="Luxury Desert Tent & Daytime Dunes",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward through the open entrance of an ultra-luxury desert glamping pavilion onto vast majestic golden sand dunes in natural daytime sunlight. "
            "Sheer cream linen draperies billow gently at the frame edges. Inside the shaded pavilion, rich hand-woven Berber kilim rugs, plush geometric floor cushions, and a low carved wooden table with an ornate Moroccan brass tea set. "
            "Outside, sculptured undulating golden sand dunes with delicate wind-carved ripples stretch endlessly under a crystal-clear cerulean blue sky in balanced 5500K natural daylight. Symmetrical 16:9 cinematic framing, shot on a locked tripod, 35mm Arri cinematography, zero tourists, zero footprints, zero modern clutter, zero vehicles."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an ornate engraved Moroccan brass teapot and mint tea glasses on a low carved wooden table inside a shaded luxury desert tent. "
            "In the background through the open cream linen drapery, sunlit golden sand dunes and pristine ripple patterns glow under bright daytime sky in creamy optical bokeh (f/1.4), serene luxurious tranquility, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle living wallpaper cinemagraph motion. Completely stationary locked tripod framing. "
            "Sheer cream linen curtains gently flutter and sway in the cool desert breeze. Subtle micro-wisps of golden sand skimming distant dune crests. "
            "The majestic sand dunes, furniture, and clear sky remain 100% rigid, frozen, and temporally stable, zero camera movement, zero panning, zero morphing."
        ),
        intimate_motion_prompt=(
            "Gentle, slow rhythmic flutter of sheer cream curtains in desert breeze, soft subtle glint of daylight on polished brass teapot, stationary tripod shot, peaceful living wallpaper cadence."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], gentle whispering desert breeze through linen, uplifting resonant handpan in major pentatonic mode, crystalline singing bowls, airy wooden nay flute, warm 432Hz velvet pads, deep stress relief, peaceful restful focus, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sand_dunes", "luxury_tent", "glamping", "daytime", "bedouin", "sheer_curtains", "432hz", "asmr"],
    ),
    "desert_tent": AtmosphericArchetype(
        key="desert_tent",
        display_name="Luxury Desert Tent & Daytime Dunes",
        cluster="desert",
        wide_visual_prompt=(
            "Masterpiece 4K photograph looking outward through the open entrance of an ultra-luxury desert glamping pavilion onto vast majestic golden sand dunes in natural daytime sunlight. "
            "Sheer cream linen draperies billow gently at the frame edges. Inside the shaded pavilion, rich hand-woven Berber kilim rugs, plush geometric floor cushions, and a low carved wooden table with an ornate Moroccan brass tea set. "
            "Outside, sculptured undulating golden sand dunes with delicate wind-carved ripples stretch endlessly under a crystal-clear cerulean blue sky in balanced 5500K natural daylight. Symmetrical 16:9 cinematic framing, shot on a locked tripod, 35mm Arri cinematography, zero tourists, zero footprints, zero modern clutter, zero vehicles."
        ),
        intimate_visual_prompt=(
            "Close-up 50mm portrait perspective of an ornate engraved Moroccan brass teapot and mint tea glasses on a low carved wooden table inside a shaded luxury desert tent. "
            "In the background through the open cream linen drapery, sunlit golden sand dunes and pristine ripple patterns glow under bright daytime sky in creamy optical bokeh (f/1.4), serene luxurious tranquility, zero humans."
        ),
        wide_motion_prompt=(
            "Ultra-subtle living wallpaper cinemagraph motion. Completely stationary locked tripod framing. "
            "Sheer cream linen curtains gently flutter and sway in the cool desert breeze. Subtle micro-wisps of golden sand skimming distant dune crests. "
            "The majestic sand dunes, furniture, and clear sky remain 100% rigid, frozen, and temporally stable, zero camera movement, zero panning, zero morphing."
        ),
        intimate_motion_prompt=(
            "Gentle, slow rhythmic flutter of sheer cream curtains in desert breeze, soft subtle glint of daylight on polished brass teapot, stationary tripod shot, peaceful living wallpaper cadence."
        ),
        acoustic_tags=(
            "[soothing & joyful meditation], gentle whispering desert breeze through linen, uplifting resonant handpan in major pentatonic mode, crystalline singing bowls, airy wooden nay flute, warm 432Hz velvet pads, deep stress relief, peaceful restful focus, zero guitar, -21 LUFS"
        ),
        default_domain="landscape_solid",
        tags=["desert", "sand_dunes", "luxury_tent", "glamping", "daytime", "bedouin", "sheer_curtains", "432hz", "asmr"],
    ),
}


