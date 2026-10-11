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
        "title": "Silent Dunes: Mysteries of the Arid Frontiers",
        "audio_tags": "desert documentary score, atmospheric desert wind whisper, low strings, deep resonant drone",
        "scenes": [
            ("Panoramic golden dawn vista of monumental sand dunes stretching to infinity", "Slow aerial flight over sharp razor-edge dune crests, warm morning shadows", "Across the arid expanses of our planet, silence reigns over colossal oceans of shifting sand."),
            ("Macro close-up of intricate wind-rippled sand grains shifting in the breeze", "Locked tripod macro view of fine sand ripples with delicate micro-particles drifting in wind", "Every grain tells a story of eroded mountain ranges and millions of years of desert winds."),
            ("Medium perspective of a desert oasis and resilient acacia trees against stark dunes", "Smooth slow pedestal rise revealing hidden green oasis nestled beneath towering dunes", "Against impossible odds, resilient life carves out ingenious sanctuaries within this extreme environment."),
            ("Dramatic twilight perspective under the emerging canopy of the Milky Way galaxy", "Slow tranquil locked tripod framing of starry night sky glittering over silent dark dunes", "Under the infinite desert night sky, the timeless stillness of the sands connects us to the cosmos."),
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
    theme_seed: Optional[str] = None,
    num_shots: int = 1,
    raw_output_path: Optional[Any] = None,
) -> DocStoryboard:
    """Dynamically generate authoritative BBC/NatGeo documentary script and storyboard via Gemini."""
    effective_theme = theme_seed or custom_prompt or genre.value
    num_scenes = max(1, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else max(2, round(duration_seconds / 12.0)))
    dur_per_scene = round(duration_seconds / num_scenes, 2)
    domain_tag, default_model = GENRE_MODEL_DEFAULTS.get(genre, ("landscape_solid", "kling_v3"))

    print(f"\n[GEMINI DOCUMENTARY AGENT INVOKED]")
    print(f"   * Genre / Theme:      {genre.value.upper()} ~ \"{effective_theme}\"")
    print(f"   * Duration:           {duration_seconds}s ({num_scenes} Scene(s) @ ~{dur_per_scene}s each)")
    print(f"   * Language:           {language.upper()}")

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        from src.core.telemetry import logger
        llm = GeminiLLMAdapter()

        system_prompt = (
            "You are a world-renowned BBC / National Geographic documentary showrunner, master cinematographer, and authoritative science communicator. "
            "Your task is to write a compelling, educational, and visually majestic 8K UHD documentary script and storyboard. "
            "CRITICAL CAMERA & MOTION DIRECTIVES:\n"
            "- 100% TIER-0 LOCAL PERSPECTIVE DRONE & KEN BURNS MOTION ($0.00 COMPUTE):\n"
            "By default for all documentaries, camera motion MUST be handled by our Tier-0 local perspective drone and Ken Burns engine. "
            "Set 'motion_type': 'ken_burns' and 'motion_engine': 'local_drone' for all scenes. "
            "Unlike fixed 5-second generative AI models, each scene's duration is completely flexible matching the requested narration beat.\n"
            "- PERMITTED DRONE MOVEMENTS: 'stay' (calm hold), 'dollyin' (optical push-in), 'dollyout' (pull-back), 'pan-left', 'pan-right', "
            "'tilt-up', 'tilt-down', 'drift-up-right', 'drift-up-left', 'drift-down-right', 'drift-down-left', 'orbit-left', 'orbit-right'.\n"
            "- SEQUENTIAL & PARALLEL STAGES: Structure 'drone_choreography' as a sequence of stages. Within each stage, 'movements' can contain a single action or multiple simultaneous actions running in parallel (e.g. ['dollyin', 'pan-left']).\n"
            "- START FRAMING: 'start_framing' can specify {'pan': 'center'|'left'|'right', 'zoom': 'normal'|'in', 'tilt': 'center'|'up'|'down'}.\n"
            "- MOTION CURVES: 'cosine' (smooth S-curve), 'linear', 'ramp-up' (slow build), 'ramp-down'.\n"
            "- ATMOSPHERIC WEATHER: 'weather' can be 'none', 'rain' (light/medium), or 'snow' (medium/heavy).\n"
            "- ANTI-FATIGUE ACOUSTIC SCORE: Warm cinematic orchestral textures, gentle natural environmental foley, deterministic sidechain ducking (-18dB) under narration, velvet -14 LUFS mastering.\n"
            "- ITINERARY & GENERIC TOUR DIRECTIVES:\n"
            "  * Autonomous Attraction Selection: The user only provides the city and duration (e.g. 'Oslo Tour, 2 Days' or 'London Tour, 3 Days'). "
            "You MUST autonomously curate the top famous attractions from your global knowledge base and allocate them logically across days based on geographic proximity and realistic visiting time (e.g. 2-3 major stops per day). Do NOT expect the user to name attractions.\n"
            "  * Strict 9:00 AM to 6:00 PM Daylight Window: For all tours, schedule visits strictly between 9:00 AM and 6:00 PM local time. Frame all landmark images in crisp natural daylight (5400K-5600K) or warm late-afternoon golden hour (3500K-4500K). Strictly PROHIBIT dark night scenes, dim moonlight, or pitch-black darkness. The last attraction must conclude by 6:00 PM.\n"
            "  * For 'itinerary_map_tour', alternate between illustrated topographic route map transition scenes (showing the travel route between stops) and iconic landmark vistas.\n"
            "  * For 'grand_tour', 'top_attractions_tour', 'local_neighborhood_tour', 'culinary_food_tour', 'heritage_history_tour', or 'architecture_design_tour', curate the defining sights in ordered narrative sequence.\n"
            "For narration: Measured, poetic, authoritative cadence (~120 wpm) rich in geographic, ecological, architectural, and cultural lore.\n"
            "Return valid JSON matching the schema."
        )

        user_msg = (
            f"Write a {num_scenes}-scene 8K UHD anti-fatigue documentary storyboard on: '{effective_theme}'.\n"
            f"Genre: {genre.value}. Duration: {duration_seconds}s (exactly {num_scenes} scene(s), ~{dur_per_scene}s per scene). Language: {language}.\n\n"
            f"Output JSON with fields:\n"
            f"- 'title': Evocative, high-CTR NatGeo documentary title\n"
            f"- 'story_topic': Educational overview and scientific/lore thesis\n"
            f"- 'audio_tags': Sweeping anti-fatigue orchestral score and natural foley tags\n"
            f"- 'scenes': Array of exactly {num_scenes} scenes each containing:\n"
            f"    - 'scene_index': int (1..{num_scenes})\n"
            f"    - 'duration_seconds': float ({dur_per_scene})\n"
            f"    - 'shot_type': 'wide', 'medium', or 'close_up'\n"
            f"    - 'motion_type': 'ken_burns'\n"
            f"    - 'motion_engine': 'local_drone'\n"
            f"    - 'camera_movement': array of stage dicts, each with:\n"
            f"        - 'stage': int\n"
            f"        - 'duration': float (seconds, sum of stage durations MUST equal {dur_per_scene}s)\n"
            f"        - 'movements': array of supported movement strings executed in parallel (e.g. ['dollyin', 'pan-left'] or ['stay'])\n"
            f"    - 'start_framing': {{'pan': 'center'|'left'|'right', 'zoom': 'normal'|'in', 'tilt': 'center'|'up'|'down'}}\n"
            f"    - 'motion_curve': 'cosine' | 'linear' | 'ramp-up' | 'ramp-down'\n"
            f"    - 'weather': 'none' | 'rain' | 'snow'\n"
            f"    - 'visual_prompt': 35mm Arri 8K photoreal prompt for Fal FLUX 1.1 Pro\n"
            f"    - 'motion_prompt': cinematic camera and atmospheric motion prompt\n"
            f"    - 'narration_text': authoritative voiceover narration lines in {language}\n"
        )

        full_prompt = f"{system_prompt}\n\n{user_msg}"
        if raw_output_path:
            try:
                from pathlib import Path
                p_out = Path(raw_output_path)
                prompt_file = p_out.parent / "gemini_input_prompt.txt" if p_out.is_file() or p_out.suffix else p_out / "gemini_input_prompt.txt"
                prompt_file.parent.mkdir(parents=True, exist_ok=True)
                prompt_file.write_text(full_prompt, encoding="utf-8")
                logger.info(f"gemini_input_prompt_saved: {prompt_file}")
            except Exception as e_p:
                logger.warning(f"failed_to_save_gemini_input_prompt: {e_p}")
        logger.info(f"gemini_doc_request_sent: genre='{genre.value}' theme='{theme_seed}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI DOC DIRECTORIAL REQUEST DISPATCHED]")
        print(f"--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_doc_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        print(f"\n[GEMINI DOC DIRECTORIAL RESPONSE RECEIVED]\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 1:
            raw_scenes = data["scenes"][:num_scenes]
            doc_scenes = []
            for idx, sc in enumerate(raw_scenes):
                sc_dur = float(sc.get("duration_seconds", dur_per_scene))
                sc_dur = max(2.0, sc_dur)
                doc_scenes.append(
                    DocScene(
                        scene_index=idx + 1,
                        duration_seconds=sc_dur,
                        shot_type=sc.get("shot_type", "wide" if idx == 0 else "medium"),
                        motion_domain=domain_tag,
                        recommended_model=default_model,
                        visual_prompt=sc.get("visual_prompt", ""),
                        motion_prompt=sc.get("motion_prompt", ""),
                        narration_text=sc.get("narration_text", ""),
                        motion_engine=sc.get("motion_engine", "local_drone"),
                        drone_choreography=sc.get("camera_movement") or sc.get("drone_choreography"),
                        start_framing=sc.get("start_framing"),
                        motion_curve=sc.get("motion_curve", "cosine"),
                        weather=sc.get("weather", "none"),
                    )
                )

            sb = DocStoryboard(
                title=data.get("title") or (theme_seed.title() if theme_seed else "Documentary"),
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
