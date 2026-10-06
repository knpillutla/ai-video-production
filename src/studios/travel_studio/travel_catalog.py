"""Travel & Scenic Wonders Studio Archetype Catalog & Diurnal Visual Specs."""
from __future__ import annotations
from typing import Any, Dict

TRAVEL_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "cities": {
        "title": "Metropolises, City Skylines & Twilight Drone Aerials",
        "diurnal_timing": "twilight_blue_hour",
        "color_temp_kelvin": 3800,
        "lighting_desc": "Cinematic blue-hour twilight with warm amber architectural lighting and glowing vehicular trails",
        "visual_prompt": (
            "Masterpiece 4K aerial drone photograph cruising gracefully over the illuminated modern and historic skyline of a world metropolis "
            "at twilight. Sweeping panoramic view revealing illuminated glass skyscrapers, iconic heritage domes, and shimmering reflections "
            "across urban waters. Hasselblad aerial medium format clarity, 16:9 framing, ultra-smooth drone glide, crisp architectural details."
        ),
        "motion_prompt": (
            "Slow cinematic aerial drone tracking glide moving smoothly forward over the city skyline. Towers, bridges, and architectural "
            "facades remain 100% rigid and temporally stable. Micro glints of evening traffic lights, shimmering urban water reflections. "
            "Zero jitter, zero aggressive turns, perfectly level gimbal horizon."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[midnight city jazz], smooth upright acoustic bass, brushed drums, warm muted trumpet, Rhodes electric piano, mellow saxophone, nighttime urban lounge, 48kHz, -14 LUFS",
    },
    "nature": {
        "title": "Untamed Wilderness, Mountain Gorges & Glacial Rivers",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Crisp 5500K balanced natural sunlight sweeping over emerald canopies, river bends, and granite ridges",
        "visual_prompt": (
            "Masterpiece 4K aerial drone photograph soaring high above an untamed mountain river valley and dense emerald pine forest. "
            "A turquoise glacial river winds through smooth granite boulders and lush riverbanks, with distant snow-dusted crags under "
            "a pristine sky. Arri Alexa 65 aerial cinematography, 16:9 framing, pure untouched nature, zero modern clutter."
        ),
        "motion_prompt": (
            "Ultra-smooth aerial drone forward glide tracking downstream along the winding glacial river. The granite peaks and dense pine forests "
            "remain rigid and temporally stable. Smooth laminar river currents ripple cleanly over rocks. Fluid camera velocity, zero judder."
        ),
        "domain": "water_fluid",
        "audio_tags": "[peaceful nature], soaring ambient acoustic orchestral, gentle acoustic guitar, airy wooden bansuri flute harmonics, mountain breeze, babbling river current, 432Hz, -14 LUFS",
    },
    "remote_places": {
        "title": "Remote Frontiers, Untouched Glaciers & Solitary Sanctuaries",
        "diurnal_timing": "golden_hour",
        "color_temp_kelvin": 4800,
        "lighting_desc": "Low-angled golden sun rays raking across windswept plateaus, solitary ice fields, and rugged ridges",
        "visual_prompt": (
            "Masterpiece 4K aerial drone vista capturing a remote, isolated frontier landscape such as the windswept spires of Patagonia "
            "or high Himalayan plateaus. Crystalline glacial lakes reflect jagged granite needles with dramatic cloud shadows drifting across "
            "the vast expanse. 16:9 panoramic perspective, epic geological scale, zero human footprint."
        ),
        "motion_prompt": (
            "Epic slow high-altitude drone tracking glide drifting across the remote wilderness. Colossal granite cliffs remain completely rigid "
            "and rock-solid. Wisps of wind-drifted snow or light mist dance across the ridgeline. Rock-solid horizon stabilization."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[remote frontier], cinematic atmospheric cello drone, ethereal duduk flute, acoustic guitar harmonics, windswept solitary silence, expansive soundstage, 432Hz, -14 LUFS",
    },
    "tourist_places": {
        "title": "World-Renowned Leisure Havens, Coastal Promenades & Harbors",
        "diurnal_timing": "golden_sunset",
        "color_temp_kelvin": 3200,
        "lighting_desc": "Warm golden hour sunlight bathing colorful coastal cliffside villas, azure harbors, and vibrant promenades",
        "visual_prompt": (
            "Masterpiece 4K aerial drone shot flying along an iconic world-renowned coastal destination like the Amalfi Coast, Santorini, "
            "or French Riviera. Pastel-hued hillside villas cascade toward crystal turquoise sea with white luxury sailboats resting in the cove. "
            "Cinematic 16:9 aerial photography, glowing golden sunset atmosphere, rich holiday aesthetic."
        ),
        "motion_prompt": (
            "Smooth cinematic coastal drone flyby gliding parallel to the cliffside architecture. Colorful villas and stone terraces remain "
            "temporally stable and crisp. Gentle rolling waves wash against the rocky cove with specular sun glints. Zero camera shaking."
        ),
        "domain": "water_fluid",
        "audio_tags": "[mediterranean breeze], breezy acoustic Spanish guitar, warm accordion melodies, gentle coastal percussion, tranquil seaside vacation lounge, 48kHz, -14 LUFS",
    },
    "spiritual_places": {
        "title": "Sacred Shrines, Ancient Temple Ghats & Spiritual Sanctuaries",
        "diurnal_timing": "sunrise_dawn",
        "color_temp_kelvin": 4000,
        "lighting_desc": "Mystical pastel sunrise dawn with soft morning mist, holy river reflections, and warm diya brass lanterns",
        "visual_prompt": (
            "Masterpiece 4K aerial drone view drifting gracefully above sacred ancient temple ghats along a revered river at sunrise dawn. "
            "Carved stone temple spires, ancient sandstone steps, glowing brass oil lamps, and wisps of sacred incense rising into pastel dawn light. "
            "Hasselblad aerial clarity, 16:9 framing, sacred reverent atmosphere."
        ),
        "motion_prompt": (
            "Tranquil low-altitude aerial drone glide floating over sacred water and temple steps. Sandstone carvings, spires, and stone ghats "
            "remain rigid and temporally stable. Gentle river ripples mirror the rising dawn and lantern glows. Sublime peaceful cadence."
        ),
        "domain": "water_fluid",
        "audio_tags": "[sacred serenity], meditative sitar raga, soothing tanpura resonance, airy bansuri flute, gentle temple brass chimes, morning river lapping, 432Hz, -14 LUFS",
    },
    "iconic_places": {
        "title": "Iconic World Heritage Monuments, Citadels & Historic Forts",
        "diurnal_timing": "sunset",
        "color_temp_kelvin": 3000,
        "lighting_desc": "Warm molten amber alpenglow illuminating ancient stone fortresses, royal arches, and colossal ramparts",
        "visual_prompt": (
            "Masterpiece 4K aerial drone orbit revealing an iconic historical fortress or ancient monument like Golconda Fort, Charminar, "
            "the Colosseum, or Petra. Colossal carved granite ramparts, royal battlements, and arched gateways glowing intensely under the setting sun. "
            "Cinematic 16:9 composition, monumental heritage majesty."
        ),
        "motion_prompt": (
            "Slow cinematic curved drone orbit shot circling the ancient stone ramparts. The granite battlements and citadel walls remain "
            "100% frozen, rigid, and razor-sharp. Faint dust particles catch the setting sunbeams in the distance. Smooth level gimbal trajectory."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[heritage majesty], regal fusion sitar and acoustic strings, resonant orchestral cello, subtle frame drum heartbeat, royal ambient brass fanfare, 48kHz, -14 LUFS",
    },
    "natural_wonders": {
        "title": "Monumental Geological Wonders, Colossal Canyons & Cataracts",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5400,
        "lighting_desc": "Vivid midday natural sunlight sculpting colossal rock layers, deep chasms, and roaring waterfalls",
        "visual_prompt": (
            "Masterpiece 4K aerial drone flight sweeping over a monumental natural wonder such as the Grand Canyon, Iguazu Falls, or Norwegian Fjords. "
            "Colossal layered sandstone precipices plunging thousands of feet into mist-veiled gorges, dramatic depth of field. "
            "Arri Alexa 65 aerial perspective, 16:9 framing, monumental natural grandeur."
        ),
        "motion_prompt": (
            "Sweeping high-altitude aerial drone flyover revealing the immense geological chasm. Layered canyon walls and stone precipices "
            "remain completely rigid and temporally stable. Distant river mist plumes gently billow in the gorge. Fluid forward velocity."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[natural wonder], epic cinematic orchestral brass, soaring string crescendo, thunderous deep timpani, roaring canyon wind foley, panoramic immersion, 48kHz, -14 LUFS",
    },
}


def get_travel_archetype(key: str) -> Dict[str, Any]:
    """Retrieve travel archetype by key with graceful fallback."""
    k = key.lower()
    for arch_key, data in TRAVEL_ARCHETYPES.items():
        if arch_key in k or k in arch_key:
            return data
    return TRAVEL_ARCHETYPES["cities"]


def get_all_travel_archetypes() -> list[Dict[str, Any]]:
    """Return all travel archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in TRAVEL_ARCHETYPES.items()]
