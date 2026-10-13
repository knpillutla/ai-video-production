"""Beach Lounge Studio Archetype Catalog & Diurnal Visual Specifications."""
from __future__ import annotations
from typing import Any, Dict

BEACH_LOUNGE_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "beach_luxury_cabana_day": {
        "title": "Ultra-Luxury Seaside Cabana & Turquoise Waves",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Brilliant 5500K natural tropical daylight with specular ocean caustics and soft shaded pergola contrast",
        "visual_prompt": (
            "Masterpiece 4K photograph looking outward from a shaded teak beach cabana daybed onto a pristine powdery white "
            "sand beach and turquoise ocean swells under bright 5500K natural daylight. Billowing sheer white linen drapes "
            "frame the shot. A low carved driftwood table features two glasses of chilled coconut water with lime wedges. "
            "In the background, gentle rhythmic waves break on an offshore coral reef under a pure blue sky. 35mm Arri cinematography, "
            "locked tripod, 16:9 aspect ratio, pure pristine luxury, zero tourists, zero clutter."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The teak cabana, daybed, and "
            "driftwood table remain 100% frozen, rigid, and temporally stable. Sheer white linen drapes flutter gently in the warm "
            "sea breeze, while smooth laminar turquoise waves roll steadily in the background. Zero camera movement, zero panning."
        ),
        "domain": "water_fluid",
        "audio_tags": "[tropical relaxation], gentle rhythmic ocean surf, Hawaiian slack-key guitar harmonics, resonant handpan in major pentatonic, soft 432Hz ambient pads, -21 LUFS",
    },
    "beach_sunset_terrace": {
        "title": "Cliffside Beach Terrace & Molten Gold Sunset",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 2800,
        "lighting_desc": "Molten gold and fiery crimson sunset reflecting across rolling ocean swells with long amber shadows",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from a weathered limestone cliffside beach terrace with plush linen lounge cushions "
            "out toward a panoramic ocean horizon during a fiery golden sunset. The sun sits on the water edge casting a shimmering "
            "path of molten amber light across the waves. An unlit frosted glass hurricane candle lantern rests on a stone ledge. "
            "Cinematic 16:9 framing, locked tripod, Hasselblad medium format clarity, pure untouched coastline."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod framing. The stone terrace, cushions, and cliffside "
            "remain 100% rigid and temporally stable. Continuous rhythmic ocean waves gently crest and reflect the golden sunset glow. "
            "Zero camera movement, zero panning, zero morphing."
        ),
        "domain": "water_fluid",
        "audio_tags": "[sunset peace], warm nylon guitar chords, gentle rolling ocean swells, resonant singing bowls, warm sunset velvet synth pads, 432Hz, -21 LUFS",
    },
    "beach_twilight_pergola": {
        "title": "Sheltered Timber Pergola & Velvet Twilight Surf",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 2400,
        "lighting_desc": "Deep velvet cobalt evening sky with warm 2400K amber fairy lights strung across driftwood pergola beams",
        "visual_prompt": (
            "Masterpiece 4K photograph looking out from a sheltered rustic timber pergola right on the water edge at blue-hour twilight. "
            "Warm amber fairy lights cast a cozy glow over plush sand-colored daybed cushions and a low bamboo table. In the background, "
            "dark cobalt ocean waves roll peacefully under the first evening stars. 16:9 framing, locked tripod, pure serene luxury."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The timber pergola, fairy lights, and daybed "
            "remain 100% frozen, rigid, and temporally stable. Dark evening ocean surf rolls rhythmically against the shore. "
            "Zero panning, zero camera translation."
        ),
        "domain": "water_fluid",
        "audio_tags": "[restful sleep], deep velvet 432Hz ambient drone, rhythmic evening ocean surf, soft wooden wind chimes, peaceful stress relief, -21 LUFS",
    },
    "beach_starlit_hammock": {
        "title": "Starlit Beach Palm Canopy & Midnight Shoreline",
        "diurnal_timing": "starlight",
        "color_temp_kelvin": 2000,
        "lighting_desc": "Deep velvet indigo midnight sky with glittering Milky Way arching over breezy palm fronds and glowing dark surf",
        "visual_prompt": (
            "Masterpiece 4K long-exposure photograph from an open-air beach pavilion looking out over a wide woven hammock slung between "
            "two leaning palm trees onto the midnight ocean. The Milky Way galaxy shines brilliantly in the deep indigo sky, casting a faint "
            "pearly reflection along the wet shoreline. Strictly zero fire, zero artificial lights, 16:9 cinematic framing on locked tripod."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The palm trunks, hammock, and sand remain "
            "100% rigid, frozen, and temporally stable. Faint ocean waves gently foam against the shore, and high palm fronds sway almost imperceptibly. "
            "Zero camera movement, zero distortion."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep delta sleep], warm 432Hz velvet sleep pads, distant rhythmic midnight ocean waves, soft sea shell chimes, calming stress relief, -21 LUFS",
    },
    "beach_infinity_pool_terrace": {
        "title": "Luxury Villa Infinity Pool Terrace & Panoramic Ocean View",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 2600,
        "lighting_desc": "Warm 2600K glowing architectural terrace illumination, soft underwater pool glow, and deep golden sunset sky over the ocean",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from an elevated ultra-luxury modern villa terrace across an illuminated crystal-clear "
            "infinity swimming pool seamlessly blending into the panoramic open ocean horizon at golden twilight. Symmetrical 16:9 composition "
            "on a locked tripod. In the foreground, smooth travertine marble decking with low designer loungers, glowing recessed architectural "
            "floor LED lights, and soft turquoise underwater pool illumination. In the background, majestic rolling ocean swells, silhouette of "
            "coastal palm trees, and a gradient twilight sky glowing with deep amber, lavender, and dusky rose. Pure architectural perfection, "
            "zero people, pristine water caustics, cinematic luxury lounge ambiance."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The modern villa terrace, loungers, "
            "and infinity pool structure remain 100% frozen, rigid, and temporally stable. Gentle glassy water ripples gently across the illuminated "
            "pool surface while calm rhythmic ocean waves roll in the distant sea under the sunset sky. Zero camera movement, zero panning."
        ),
        "domain": "water_fluid",
        "audio_tags": "[chillout lounge], 432Hz deep relaxed velvet synth pads, gentle water ripples, soothing distant ocean swell, sophisticated chillout lounge guitar harmonics, -21 LUFS",
    },
    "pool_terrace": {
        "title": "Luxury Villa Infinity Pool Terrace & Panoramic Ocean View",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 2400,
        "lighting_desc": "Warm 2400K glowing architectural terrace illumination, soft turquoise underwater pool glow, and twilight sky",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from an elevated ultra-luxury modern villa terrace across an illuminated crystal-clear "
            "infinity swimming pool seamlessly blending into the panoramic open ocean horizon at golden twilight. Symmetrical 16:9 composition "
            "on a locked tripod. In the foreground, smooth travertine marble decking with low designer loungers, glowing recessed architectural "
            "floor LED lights, and soft turquoise underwater pool illumination. In the background, majestic rolling ocean swells and evening sky. "
            "Pure architectural perfection, zero people, pristine luxury chillout lounge ambiance."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The villa terrace and infinity pool remain "
            "100% frozen and rigid. Gentle glassy water ripples across the illuminated pool surface while calm ocean swells roll in the background."
        ),
        "domain": "water_fluid",
        "audio_tags": "[chillout lounge], 432Hz deep relaxed velvet synth pads, gentle water ripples, soothing ocean swells, -21 LUFS",
    },
    "pool_terrace_twilight": {
        "title": "Twilight Infinity Pool Terrace & Ocean Horizon",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 2400,
        "lighting_desc": "Blue-hour twilight sky with warm 2400K recessed architectural LED floor lights and soft turquoise underwater pool illumination",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from an elevated ultra-luxury modern villa terrace across an illuminated crystal-clear "
            "infinity swimming pool seamlessly blending into the panoramic open ocean horizon at deep blue-hour twilight. Symmetrical 16:9 composition "
            "on a locked tripod. In the foreground, smooth polished stone decking with low designer chaise loungers, warm glowing floor LED uplights, "
            "and glowing turquoise underwater pool lights. In the background, gentle rhythmic ocean waves glide past the coastline under a serene violet "
            "and deep indigo evening sky. Zero people, pure tranquility, high-end chillout lounge aesthetic."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod. The terrace, loungers, and pool walls remain 100% still and rigid. "
            "Soft glassy water caustics pulse gently on the pool surface, while slow rhythmic ocean waves roll smoothly in the distance. Zero camera motion."
        ),
        "domain": "water_fluid",
        "audio_tags": "[chillout lounge], 432Hz deep relaxed velvet synth pads, gentle water ripples, soothing distant ocean swell, sophisticated chillout lounge guitar harmonics, -21 LUFS",
    },
    "pool_terrace_sunset": {
        "title": "Sunset Infinity Pool Terrace & Molten Gold Horizon",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 2800,
        "lighting_desc": "Molten gold sunset glowing directly on the ocean horizon with fiery amber reflections across the glassy pool surface",
        "visual_prompt": (
            "Masterpiece 4K photograph looking from a luxury clifftop villa terrace across an infinity swimming pool edge merging with the open sea horizon "
            "during a breathtaking golden hour sunset. Warm 2800K molten amber sunlight reflects across the glassy pool surface and ocean waves. "
            "Low teak loungers, frosted glass cocktail table, silhouette of swaying palm trees, and radiant crimson-gold sky. Symmetrical 16:9 framing, "
            "locked tripod, Hasselblad medium format clarity."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Stationary locked camera. The terrace and furniture remain completely still. "
            "Subtle water reflections glint across the infinity pool edge and distant sunset ocean waves roll continuously."
        ),
        "domain": "water_fluid",
        "audio_tags": "[sunset peace], warm nylon guitar chords, gentle rolling ocean swells, warm sunset velvet synth pads, 432Hz, -21 LUFS",
    },
    "pool_terrace_daylight": {
        "title": "Daytime Infinity Pool & Turquoise Ocean View",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Brilliant 5500K crisp tropical sunlight, specular water caustics, and vivid turquoise ocean expanse",
        "visual_prompt": (
            "Masterpiece 4K photograph looking out from a sunlit luxury villa terrace over a pristine turquoise infinity swimming pool overflowing toward "
            "a boundless turquoise ocean under bright natural daylight. Crisp white stone decking, luxury daybeds with cream parasols, and deep blue sky. "
            "Pure tropical luxury, locked tripod, 16:9 aspect ratio."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Locked tripod. Shimmering sunlight caustics dancing on the pool surface and rolling ocean waves."
        ),
        "domain": "water_fluid",
        "audio_tags": "[tropical relaxation], gentle rhythmic ocean surf, 432Hz ambient pads, -21 LUFS",
    },
    "pool_terrace_starlit": {
        "title": "Starlit Midnight Infinity Pool & Ambient Glow",
        "diurnal_timing": "starlight",
        "color_temp_kelvin": 2000,
        "lighting_desc": "Deep velvet midnight sky with glittering Milky Way, soft underwater turquoise pool glow, and dark ocean horizon",
        "visual_prompt": (
            "Masterpiece 4K long-exposure photograph from an elevated luxury villa terrace overlooking a glowing turquoise infinity pool merging into a midnight ocean. "
            "The Milky Way galaxy shines brilliantly above, reflected faintly in the still pool water. Recessed amber step lights, locked tripod, 16:9 framing."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Locked tripod. Gentle pool water ripples and faint rhythmic dark ocean surf."
        ),
        "domain": "water_fluid",
        "audio_tags": "[deep delta sleep], warm 432Hz velvet sleep pads, distant rhythmic midnight ocean waves, -21 LUFS",
    },
}


def get_beach_lounge_archetype(key: str) -> Dict[str, Any]:
    """Retrieve beach lounge archetype by key with graceful fallback."""
    return BEACH_LOUNGE_ARCHETYPES.get(key, BEACH_LOUNGE_ARCHETYPES["beach_luxury_cabana_day"])


def get_all_beach_lounge_archetypes() -> list[Dict[str, Any]]:
    """Return all beach lounge archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in BEACH_LOUNGE_ARCHETYPES.items()]
