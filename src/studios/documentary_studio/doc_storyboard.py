"""Documentary Storyboard & Model Routing Engine.

Directorial generation for 6 blue-chip documentary archetypes:
1. Wildlife (Biological kinematics, animal behaviors)
2. Ocean (Deep-sea, coral reefs, pelagic life)
3. Nature (Canopies, seasonal transitions, rainforests)
4. Mountains (Alpine peaks, glacial valleys, survival)
5. Art (Renaissance frescoes, sculptures, fine canvas macro)
6. Ancient Structures (Megaliths, pyramids, lost temples)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Dict, List, Optional


class DocGenre(str, Enum):
    WILDLIFE = "wildlife"
    OCEAN = "ocean"
    NATURE = "nature"
    MOUNTAINS = "mountains"
    ART = "art"
    ANCIENT_STRUCTURES = "ancient_structures"


@dataclass
class DocScene:
    """A single documentary visual scene with matched narration and model routing."""
    scene_index: int
    duration_seconds: float
    shot_type: str
    motion_domain: str
    recommended_model: str
    visual_prompt: str
    motion_prompt: str
    narration_text: str


@dataclass
class DocStoryboard:
    """Complete documentary production storyboard with metadata and scenes."""
    title: str
    genre: DocGenre
    total_duration: float
    scenes: List[DocScene] = field(default_factory=list)
    language: str = "en"
    audio_tags: str = "cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master"


GENRE_MODEL_DEFAULTS = {
    DocGenre.WILDLIFE: ("wildlife_animal", "kling_v3"),
    DocGenre.OCEAN: ("water_fluid", "wan"),
    DocGenre.NATURE: ("landscape_solid", "kling_v3"),
    DocGenre.MOUNTAINS: ("landscape_solid", "hunyuan"),
    DocGenre.ART: ("art_macro", "hunyuan"),
    DocGenre.ANCIENT_STRUCTURES: ("architecture_solid", "hunyuan"),
}


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
    DocGenre.ANCIENT_STRUCTURES: {
        "title": "Monuments of Eternity: The Megaliths of Ancient Civilizations",
        "audio_tags": "ancient history score, deep bronze gongs, low orchestral drone, atmospheric desert wind",
        "scenes": [
            ("Panoramic golden dawn vista of the Giza Pyramids rising from the desert sands", "Slow monumental low-angle aerial glide forward toward the Great Pyramid, warm dawn dust", "Rising from the golden sands of Egypt, the Great Pyramids have defied time for over four thousand years."),
            ("Macro close-up of precision-cut megalithic stone blocks fitting seamlessly without mortar", "Locked tripod macro view of weathered granite seams, subtle sand grains blowing in wind", "Built with baffling mathematical precision, these titanic stone blocks align perfectly to cosmic cardinal points."),
            ("Medium atmospheric shot through a hypostyle hall of towering stone columns with hieroglyphs", "Smooth slow pedestal rise revealing towering carved columns, soft shafts of sunlight", "Ancient priests and architects encoded their deepest celestial lore into stone that would outlast empires."),
            ("Twilight vista of ancient ruins under the rising Milky Way galaxy", "Fixed locked tripod camera, brilliant starry night sky drifting slowly over ancient stone obelisks", "These stone giants stand as eternal testaments to human ambition, engineering mastery, and cosmic wonder."),
        ]
    }
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


async def generate_documentary_storyboard_gemini(
    genre: DocGenre = DocGenre.WILDLIFE,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    language: str = "en",
    user_id: str = "user_krishna_01",
) -> DocStoryboard:
    """Dynamically generate authoritative BBC/NatGeo documentary script and storyboard via Gemini."""
    theme_seed = custom_prompt or genre.value
    num_scenes = 4
    dur_per_scene = round(duration_seconds / num_scenes, 2)
    domain_tag, default_model = GENRE_MODEL_DEFAULTS.get(genre, ("landscape_solid", "kling_v3"))

    print(f"\n[GEMINI DOCUMENTARY AGENT INVOKED]")
    print(f"   * Genre / Theme:      {genre.value.upper()} ~ \"{theme_seed}\"")
    print(f"   * Duration:           {duration_seconds}s (4 Scenes @ {dur_per_scene}s each)")
    print(f"   * Language:           {language.upper()}")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        from src.core.telemetry import logger
        llm = GeminiLLMAdapter()

        system_prompt = (
            "You are a world-renowned BBC / National Geographic documentary showrunner and authoritative science communicator. "
            "Your task is to write a compelling, educational, and visually majestic 8K UHD 4-scene documentary script and storyboard. "
            "CRITICAL ANTI-FATIGUE DIRECTIVES:\n"
            "- ANTI-FATIGUE CAMERA MOTION: Slow, sweeping, majestic 24fps documentary movements. Strictly prohibit aggressive zooms, rapid pans, jerky handheld shake, or disorienting camera speed.\n"
            "- ANTI-FATIGUE ACOUSTIC SCORE: Warm cinematic orchestral textures, gentle natural environmental foley, zero harsh high-frequency spikes, deterministic sidechain ducking (-18dB) under narration, velvet -14 LUFS mastering.\n"
            "For narration: Measured, poetic, authoritative cadence (~120 wpm) rich in geographic, ecological, and evolutionary lore. "
            "For visual prompts: Arri Alexa 35mm Master Prime specifications, 8K UHD master resolution, exact focal lengths, f-stops (f/2.8, f/4.0), natural balanced lighting, zero CGI sheen. "
            "For motion prompts: Majestic 24fps documentary camera motion, steady forward glides, natural animal behaviors or environmental physics. "
            "Return valid JSON matching the schema."
        )

        user_msg = (
            f"Write a 4-scene 8K UHD anti-fatigue documentary storyboard on: '{theme_seed}'.\n"
            f"Genre: {genre.value}. Duration: {duration_seconds}s ({dur_per_scene}s per scene). Language: {language}.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': Evocative, high-CTR NatGeo documentary title\n"
            f"- 'story_topic': Educational overview and scientific/lore thesis\n"
            f"- 'audio_tags': Sweeping anti-fatigue orchestral score and natural foley tags\n"
            f"- 'scenes': Array of 4 scenes each containing:\n"
            f"    - 'scene_index': int (1..4)\n"
            f"    - 'shot_type': 'wide', 'medium', or 'close_up'\n"
            f"    - 'visual_prompt': 35mm Arri 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': smooth 24fps cinematic camera motion prompt for Kling v3 Pro / Wan 2.1\n"
            f"    - 'narration_text': authoritative voiceover narration lines in {language}\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        logger.info(f"gemini_doc_request_sent: genre='{genre.value}' theme='{theme_seed}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI DOC DIRECTORIAL REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_doc_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI DOC DIRECTORIAL RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 4:
            doc_scenes = []
            for idx, sc in enumerate(data["scenes"][:4]):
                doc_scenes.append(
                    DocScene(
                        scene_index=idx + 1,
                        duration_seconds=dur_per_scene,
                        shot_type=sc.get("shot_type", "wide" if idx in (0, 3) else "medium"),
                        motion_domain=domain_tag,
                        recommended_model=default_model,
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        narration_text=sc.get("narration_text", ""),
                    )
                )

            sb = DocStoryboard(
                title=data.get("title") or theme_seed.title(),
                genre=genre,
                total_duration=duration_seconds,
                scenes=doc_scenes,
                language=language,
                audio_tags=data.get("audio_tags") or "cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master",
            )
            print(f"[GEMINI DOC STORYBOARD SUCCESS] Synthesized '{sb.title}' with {len(sb.scenes)} authoritative documentary scenes.")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed documentary storyboard data: {data}")
    except Exception as ex:
        from src.core.telemetry import logger
        logger.error(f"gemini_doc_storyboard_fatal_error: {ex}")
        print(f"\n[GEMINI FATAL ERROR] Documentary directorial screenplay synthesis failed: {ex}\n")
        raise RuntimeError(f"Gemini documentary directorial screenplay generation failed: {ex}") from ex


__all__ = ["DocGenre", "DocScene", "DocStoryboard", "generate_documentary_storyboard", "generate_documentary_storyboard_gemini"]
