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
}


def get_beach_lounge_archetype(key: str) -> Dict[str, Any]:
    """Retrieve beach lounge archetype by key with graceful fallback."""
    return BEACH_LOUNGE_ARCHETYPES.get(key, BEACH_LOUNGE_ARCHETYPES["beach_luxury_cabana_day"])


def get_all_beach_lounge_archetypes() -> list[Dict[str, Any]]:
    """Return all beach lounge archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in BEACH_LOUNGE_ARCHETYPES.items()]
