"""Forest Studio Archetype Catalog & Diurnal Visual Specifications."""
from __future__ import annotations
from typing import Any, Dict

FOREST_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "forest_mossy_canopy_day": {
        "title": "Ancient Mossy Rainforest & Sunbeam Canopy",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5400,
        "lighting_desc": "Natural 5400K daylight with ethereal golden sunbeams (komorebi) piercing an ancient temperate rainforest canopy",
        "visual_prompt": (
            "Masterpiece 4K photograph inside an ancient temperate rainforest glade. Towering moss-draped Douglas fir and cedar trees "
            "reach toward the sky while lush green sword ferns carpet the forest floor. Spectacular volumetric sunbeams filter through "
            "the high emerald canopy, illuminating motes of dust and glowing moss. A crystal brook murmurs in the background. "
            "35mm Arri cinematography, locked tripod framing, 16:9 aspect ratio, pure pristine nature, zero tourists."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod framing. The massive mossy cedar trunks, "
            "foreground ferns, and forest floor remain 100% frozen, rigid, and temporally stable. Only subtle shimmering dust motes drift "
            "through the sunbeam rays, and high canopy leaves flutter gently in the soft breeze. Zero camera movement, zero panning."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep forest peace], Japanese bamboo shakuhachi flute, organic wooden wind chimes, peaceful songbird calls, babbling forest brook, warm 432Hz ambient pads, -21 LUFS",
    },
    "forest_babbling_brook": {
        "title": "Gentle Forest River & Mossy Riverbank Stones",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5200,
        "lighting_desc": "Soft diffused forest daylight with shimmering water caustics reflecting off rounded river stones",
        "visual_prompt": (
            "Masterpiece 4K photograph capturing a clear, gentle forest river winding over smooth rounded river stones and submerged "
            "green moss. Giant ancient cedar roots clasp mossy granite banks on either side with lush overhanging ferns. Filtered morning "
            "sunlight creates dancing golden caustics on the shallow river bed. Symmetrical 16:9 framing, locked tripod, 35mm film grain."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely locked tripod framing. The cedar trunks, mossy banks, and river rocks "
            "remain 100% rigid and temporally stable. Continuous smooth laminar stream currents flow peacefully around the stones with tiny glassy ripples. "
            "Zero camera translation, zero jitter."
        ),
        "domain": "water_fluid",
        "audio_tags": "[stress relief brook], continuous gentle bubbling river foley, resonant handpan in major pentatonic, soft wood flute, 432Hz velvet drone, -21 LUFS",
    },
    "forest_morning_sunbeams": {
        "title": "Misty Redwood Cathedral & Golden Morning Sunbeams",
        "diurnal_timing": "dawn",
        "color_temp_kelvin": 4500,
        "lighting_desc": "Luminous golden dawn sunbeams cutting through morning coastal fog in a giant Redwood cathedral",
        "visual_prompt": (
            "Masterpiece 4K photograph looking up from the forest floor of a giant California Redwood cathedral grove at dawn. "
            "Colossal cinnamon-red bark trunks soar 300 feet into the mist while intense diagonal golden sunbeams pierce the moist morning fog. "
            "Deep green sorrel and maidenhair ferns glisten with fresh dew. Cinematic 16:9 framing, locked tripod, Hasselblad medium format clarity."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod. The giant redwood trunks and fern-covered "
            "ground remain 100% frozen and temporally stable. Only thin ethereal layers of morning fog slowly drift across the sunbeams. "
            "Zero camera movement, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[sacred forest meditation], deep resonant Tibetan singing bowls, Celtic harp harmonics, gentle redwood canopy wind whisper, restorative 432Hz, -21 LUFS",
    },
    "forest_twilight_fireflies": {
        "title": "Ethereal Twilight Forest Glade & Bioluminescent Fireflies",
        "diurnal_timing": "twilight",
        "color_temp_kelvin": 2400,
        "lighting_desc": "Deep cobalt blue-hour twilight with warm pulsing golden fireflies glowing over a quiet woodland pond",
        "visual_prompt": (
            "Masterpiece 4K photograph in a secluded mossy forest glade at deep twilight. A mirror-still forest pond reflects the dark "
            "indigo tree canopy. Dozens of soft glowing golden fireflies hover peacefully over the water and among lush ferns, casting delicate "
            "warm points of light into the dark blue woods. Strictly zero artificial lights, 16:9 cinematic framing on locked tripod."
        ),
        "motion_prompt": (
            "Ultra-subtle living wallpaper cinemagraph. Completely stationary locked tripod perspective. The ancient tree silhouettes, "
            "ferns, and pond remain 100% rigid, frozen, and temporally stable. Delicate glowing fireflies gently pulse and drift with slow, "
            "peaceful trajectories above the water. Zero panning, zero camera movement."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep restorative sleep], warm 432Hz velvet sleep pads, distant evening forest cricket chorus, gentle night breeze, calming stress relief, -21 LUFS",
    },
}


def get_forest_archetype(key: str) -> Dict[str, Any]:
    """Retrieve forest archetype by key with graceful fallback."""
    return FOREST_ARCHETYPES.get(key, FOREST_ARCHETYPES["forest_mossy_canopy_day"])


def get_all_forest_archetypes() -> list[Dict[str, Any]]:
    """Return all forest archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in FOREST_ARCHETYPES.items()]
