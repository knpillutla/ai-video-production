"""Static Fallback Storyboard Templates for Documentary Studio Genres."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class DocGenre(str, Enum):
    PLACES = "places"
    BEACHES = "beaches"
    MOUNTAINS = "mountains"
    NATURE = "nature"
    OCEAN = "ocean"
    DESERT = "desert"
    WILDLIFE = "wildlife"
    ART = "art"
    ANCIENT_STRUCTURES = "ancient_structures"


@dataclass
class DocScene:
    """A single documentary visual scene with matched narration, camera choreography, and model routing."""
    scene_index: int
    duration_seconds: float
    shot_type: str
    motion_domain: str
    recommended_model: str
    visual_prompt: str
    motion_prompt: str
    narration_text: str
    motion_engine: str = "local_drone"
    drone_choreography: Optional[List[Dict[str, Any]]] = None
    start_framing: Optional[Dict[str, str]] = None
    motion_curve: str = "cosine"
    weather: str = "none"
    is_map_transition: bool = False
    attraction_name: Optional[str] = None
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    origin_coords: Optional[List[float]] = None
    destination_coords: Optional[List[float]] = None
    distance_local: Optional[str] = None
    transit_mode: Optional[str] = "walk"
    day_number: Optional[int] = 1
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    visit_duration: Optional[str] = None
    transit_duration: Optional[str] = None
    attraction_cost: Optional[str] = None
    is_itinerary_overview: bool = False
    is_itinerary_summary: bool = False
    is_vacation_scope: bool = False
    camera_rig: Optional[str] = "heavy_lift_cine_drone"
    camera_movement: Optional[str] = "slow_drone_forward"
    motion_type: Optional[str] = "ken_burns"
    motion_rationale: Optional[str] = None
    location_hub: Optional[str] = None
    color_temp_kelvin: Optional[int] = 5500
    model_configs: Optional[Dict[str, Any]] = None
    image_model_configs: Optional[Dict[str, Any]] = None
    motion_negative_prompt: Optional[str] = None


@dataclass
class DocStoryboard:
    """Complete documentary production storyboard with metadata and scenes."""
    title: str
    genre: DocGenre
    total_duration: float
    scenes: List[DocScene] = field(default_factory=list)
    language: str = "en"
    audio_tags: str = "cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master"
    itinerary_summary: Optional[List[Dict[str, Any]]] = None


DOC_TEMPLATES: Dict[DocGenre, Dict[str, Any]] = {
    DocGenre.WILDLIFE: {
        "title": "Untamed Majesty: Predators of the Serengeti",
        "audio_tags": "bbc nature documentary score, subtle acacia wind, distant savannah foley, sparse cellos",
        "scenes": [
            ("Wide establishing vista of the golden African savannah at dawn", "Slow forward cinematic drone glide over golden savannah grass, warm morning haze", "Across the sun-drenched plains of the Serengeti, life moves to the timeless rhythm of the great migration."),
            ("Telephoto close-up of an African lioness scanning the horizon", "Subtle biological micro-motion: slow natural breathing, blinking amber eyes, ears flicking wind", "Every muscle is tuned for survival. In this unforgiving wilderness, patience is the predator's greatest weapon."),
            ("Medium tracking perspective of a herd of zebras moving in unison", "Smooth synchronized animal walking cadence through dust, natural biological movement", "For thousands of years, these ancient migratory corridors have sustained the heartbeat of the continent."),
            ("Dramatic twilight silhouette of cheetah atop an ancient termite mound", "Fixed locked tripod camera, gentle evening breeze rustling mane, dramatic sunset clouds", "As the sun sets below the horizon, the savanna transforms into an entirely different realm of shadow and instinct."),
        ]
    },
    DocGenre.OCEAN: {
        "title": "Abyssal Realms: Secrets of the Deep Coral Sea",
        "audio_tags": "underwater ocean documentary, deep hydrophone rumble, subtle melodic harp and ambient strings",
        "scenes": [
            ("Sweeping wide view of a pristine coral reef bathed in turquoise sunlight", "Slow smooth underwater camera glide parallel to the coral shelf, caustic sunbeam rays dancing", "Beneath the ocean surface lies a vibrant metropolis, older and more diverse than any terrestrial forest."),
            ("Close-up macro of a sea turtle gliding effortlessly past giant sea fans", "Fluid biological swimming motion, gentle flipper strokes, tiny natural air bubbles rising", "Reptiles of ancient lineage have navigated these ocean currents for over a hundred million years."),
            ("Mesmerizing shot of bioluminescent deep-sea jellyfish drifting in dark water", "Smooth undulating bell contraction, pulsing neon blue and emerald light emission in black water", "In the abyssal midnight zone, creatures generate their own living light to communicate and hunt."),
            ("Panoramic wide pull-back of a coral atoll meeting the deep blue abyss", "Slow majestic pull-back revealing monumental underwater drop-off into deep ocean indigo", "This fragile aquatic ecosystem remains our planet's greatest frontier of wonder and discovery."),
        ]
    },
    DocGenre.NATURE: {
        "title": "Ancient Canopies: Whispers of the Temperate Rainforest",
        "audio_tags": "pacific northwest rainforest documentary, gentle canopy wind, soft stream foley, warm acoustic pads",
        "scenes": [
            ("Wide panoramic view of ancient Olympic rainforest covered in emerald moss", "Slow crane descent through misty ancient spruce canopies, gentle drifting morning fog", "In the heart of the Pacific Northwest, ancient giants rise hundreds of feet into the coastal fog."),
            ("Macro 35mm view of crystal rain droplets on velvet fern fronds", "Fixed locked tripod, subtle delicate droplet tremors, soft wind flutter of green fronds", "Every square inch of this living cathedral is layered with intricate biophilic complexity."),
            ("Medium shot of a crystal-clear mountain stream cascading through dark basalt stones", "Smooth laminar flowing water currents, natural ripples over pebbles, soft light glints", "Glacial streams carve their eternal paths, nourishing an unbroken tapestry of flora and fauna."),
            ("Golden hour sunlight piercing through towering cedar branches", "Gentle volumetric god-rays shifting slowly through mist, tranquil environmental stillness", "Here, time slows down, preserving an ancient balance that has endured across centuries."),
        ]
    },
    DocGenre.MOUNTAINS: {
        "title": "Granite Sanctuaries: Titans of the Swiss Alps",
        "audio_tags": "alpine mountain score, soaring french horns, mountain wind whisper, resonant cellos",
        "scenes": [
            ("Sweeping cinematic aerial glide over snow-dusted jagged granite peaks", "Monumental slow forward flight over sheer cliff faces into deep alpine valley below", "Formed through immense tectonic collisions millions of years ago, the Alps stand as monuments of granite and ice."),
            ("Medium low-angle view of a glacial lake reflecting towering white summits", "Fixed locked tripod, mirror-like glassy water surface with subtle gentle ripples at shoreline", "Pristine glacial lakes collect the pure meltwater, reflecting the timeless majesty of the skies above."),
            ("Macro shot of resilient alpine edelweiss flowers blooming on rugged rock crevices", "Locked tripod perspective, gentle breeze fluttering delicate white velvety petals", "Even in this extreme sub-zero climate, resilient alpine flora thrives against all odds."),
            ("Golden twilight mountain ridge with clouds rolling over snowy passes", "Slow cinematic tracking along the ridge, warm amber sunset glow kissing the snowfields", "As twilight settles over the summits, the mountains enter their quiet, eternal sleep."),
        ]
    },
    DocGenre.ART: {
        "title": "The Master's Touch: Secrets of Renaissance Frescoes",
        "audio_tags": "renaissance chamber score, gentle baroque lute, soft acoustic resonance, warm strings",
        "scenes": [
            ("Wide view of an opulent Italian Renaissance vaulted basilica with frescoed ceilings", "Slow architectural crane descent looking up at frescoed vaults, warm golden candlelight", "During the height of the Italian Renaissance, master artists revolutionized the expression of human spirit."),
            ("Ultra-high detail 35mm macro pan across oil canvas brushstrokes and tempera pigments", "Smooth slow macro tracking along layered oil textures, lapis lazuli and gold leaf glints", "Layer upon layer of ground minerals, egg tempera, and oil captured divine emotion with unprecedented realism."),
            ("Dramatic chiaroscuro side-profile close-up of a sculpted Carrara marble statue", "Slow arc orbit around finely chiselled marble drapery and expressive marble face", "From cold blocks of Carrara marble, sculptors unlocked breathing human form and dynamic movement."),
            ("Atmospheric wide shot of sunlight streaming across museum gallery paintings", "Tranquil slow forward camera float down the gallery hall, warm ambient gallery illumination", "Centuries later, these timeless masterpieces continue to speak across the boundaries of human history."),
        ]
    },
    DocGenre.PLACES: {
        "title": "Earth's Geographic Sanctuaries: Wonders of the World",
        "audio_tags": "sweeping world documentary score, noble horns, gentle cultural strings, expansive acoustic pads",
        "scenes": [
            ("Panoramic wide aerial vista revealing the monumental geographic expanse of the landscape", "Slow cinematic drone forward glide over scenic terrain, soft morning haze", "Across the globe, distinct geographical wonders shape the landscapes and cultures that inhabit them."),
            ("Medium architectural and cultural detail perspective of local historic dwellings and stone paths", "Smooth gentle camera drift along timeless regional buildings and natural pathways", "For centuries, human communities have carved their traditions in harmony with the unique topography of their homeland."),
            ("Striking medium landscape perspective of geological features and pure flowing waters", "Slow pedestal rise revealing majestic natural contours and pristine light glints", "Every contour tells a story of millions of years of continental drift, erosion, and atmospheric transformation."),
            ("Dramatic twilight panoramic pull-back over the entire geographic region", "Majestic slow pull-back revealing the vast valley and distant horizons under pastel sunset", "As dusk settles over this sacred landscape, the eternal balance between earth and sky endures."),
        ]
    },
    DocGenre.BEACHES: {
        "title": "Untamed Shorelines: Coastal Wonders of the World",
        "audio_tags": "coastal documentary score, gentle rolling swells, acoustic harp and warm cello resonance",
        "scenes": [
            ("Panoramic aerial glide over pristine coastal shoreline and turquoise waters", "Slow monumental flight parallel to the breaking shoreline, sunlight dancing on crests", "Where the continent yields to the open sea, dynamic coastal ecosystems showcase nature's raw beauty."),
            ("Medium eye-level shot of crystalline turquoise waves washing over pristine sands", "Slow locked tracking of laminar wave wash across smooth sandbars and coastal shells", "Each tidal rhythm sculpts the coastline, breathing life into a delicate littoral sanctuary."),
            ("Dramatic low-angle view of rugged coastal rock formations and sea stacks", "Slow crane ascent revealing sheer sea stacks carved by eternal ocean swells", "Relentless ocean forces continually sculpt the edge of the world into dramatic geological sculptures."),
            ("Golden sunset vista across the vast shoreline horizon", "Tranquil slow forward camera drift into golden hour horizon reflection across wet sands", "As the sun dips below the ocean horizon, the shoreline enters its quiet, timeless serenity."),
        ]
    },
    DocGenre.DESERT: {
        "title": "Silent Dunes: Mysteries of the Living Sands",
        "audio_tags": "mystic desert wind foley, sparse acoustic oud, resonant warm bass drone, 48kHz master",
        "scenes": [
            ("Sweeping high-altitude aerial view of endless golden crescent dunes at sunrise", "Monumental slow drone glide over sharp wind-carved dune ridges, long morning shadows", "Across the vast desert expanse, winds sculpt an ever-changing sea of golden sand."),
            ("Macro 35mm view of crystalline mineral sand grains rippling in desert breeze", "Fixed locked tripod, subtle delicate wind ripples dancing across sand contours", "Every grain of silica bears witness to thousands of years of erosion and patient transformation."),
            ("Medium shot of an isolated desert oasis with date palms reflecting in clear spring water", "Slow pedestal descent toward tranquil mirror-like pool framed by lush green fronds", "Where hidden aquifers reach the surface, vibrant oases sustain life against the arid elements."),
            ("Dramatic twilight vista of sandstone monoliths glowing deep red under starry night sky", "Tranquil slow forward camera drift looking toward towering sandstone arches under dusk", "As the desert heat dissolves into cool night air, silence settles over the ancient expanse."),
        ]
    },
    DocGenre.ANCIENT_STRUCTURES: {
        "title": "Monuments of Time: Secrets of Ancient Architecture",
        "audio_tags": "grand ancient history score, deep bronze percussion, noble brass, choral resonance",
        "scenes": [
            ("Panoramic wide drone view of megalithic stone temples at golden sunrise", "Slow architectural crane ascent revealing massive carved granite pillars and lintels", "Thousands of years ago, ancient builders raised stone titans that have defied the centuries."),
            ("Medium architectural perspective of intricate stone carvings and ancient glyphs", "Smooth lateral tracking across weathered reliefs and weathered basalt glyphs", "Every inscription preserves the spiritual aspirations and scientific genius of lost civilizations."),
            ("Low-angle dramatic perspective looking up at towering ancient columns against the sky", "Slow low-angle pedestal lift capturing the colossal vertical scale of stone colonnades", "Their engineering mastery transformed raw earth into eternal declarations of human endurance."),
            ("Twilight silhouette of the ancient citadel over looking the historic horizon", "Majestic slow pull-back revealing the fortress walls against the deep indigo twilight", "Standing as sentinels of history, these ancient sanctuaries guard the memory of human civilization."),
        ]
    },
}

GENRE_MODEL_DEFAULTS: Dict[DocGenre, tuple[str, str]] = {
    DocGenre.PLACES: ("landscape_solid", "hunyuan"),
    DocGenre.BEACHES: ("water_fluid", "wan"),
    DocGenre.MOUNTAINS: ("landscape_solid", "hunyuan"),
    DocGenre.NATURE: ("landscape_solid", "kling_v3"),
    DocGenre.OCEAN: ("water_fluid", "wan"),
    DocGenre.DESERT: ("landscape_solid", "hunyuan"),
    DocGenre.WILDLIFE: ("wildlife_animal", "kling_v3"),
    DocGenre.ART: ("art_macro", "hunyuan"),
    DocGenre.ANCIENT_STRUCTURES: ("architecture_solid", "hunyuan"),
}


def generate_documentary_storyboard(
    genre: DocGenre = DocGenre.WILDLIFE,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    language: str = "en",
) -> DocStoryboard:
    """Autonomously synthesize an authoritative documentary storyboard."""
    tmpl = DOC_TEMPLATES.get(genre, DOC_TEMPLATES[DocGenre.WILDLIFE])
    title = tmpl["title"]
    if custom_prompt:
        title = f"{title} ~ {custom_prompt.split(',')[0].title()}"

    domain_tag, default_model = GENRE_MODEL_DEFAULTS.get(genre, ("landscape_solid", "kling_v3"))
    raw_scenes = tmpl["scenes"]
    num_scenes = len(raw_scenes)
    dur_per_scene = round(duration_seconds / num_scenes, 2)

    doc_scenes: List[DocScene] = []
    for idx, (vis_desc, mot_desc, narr) in enumerate(raw_scenes):
        v_prompt = (
            f"Raw blue-chip BBC/NatGeo documentary 35mm film photograph of {genre.value}. {vis_desc}. "
            f"Crisp natural balanced lighting, extreme optical depth, 35mm Master Prime lens at f/4.0, zero CGI sheen, zero plastic artifacts."
        )
        if custom_prompt:
            v_prompt = f"{v_prompt} Featuring {custom_prompt}."

        doc_scenes.append(
            DocScene(
                scene_index=idx + 1,
                duration_seconds=dur_per_scene,
                shot_type="wide" if idx in (0, 3) else "medium",
                motion_domain=domain_tag,
                recommended_model=default_model,
                visual_prompt=v_prompt,
                motion_prompt=f"Cinematic 24fps documentary motion. {mot_desc}. Natural physics, realistic micro-motion.",
                narration_text=narr,
            )
        )

    return DocStoryboard(
        title=title,
        genre=genre,
        total_duration=duration_seconds,
        scenes=doc_scenes,
        language=language,
        audio_tags=tmpl["audio_tags"],
    )


__all__ = [
    "DocGenre",
    "DocScene",
    "DocStoryboard",
    "DOC_TEMPLATES",
    "GENRE_MODEL_DEFAULTS",
    "generate_documentary_storyboard",
]

