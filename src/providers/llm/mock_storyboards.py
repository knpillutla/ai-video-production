"""Topic-accurate deterministic offline mock storyboard resolver."""

import re
from typing import Any
from src.providers.llm.mock_storyboard_catalog import lookup_destination_preset


def _parse_custom_script_scenes(prompt: str, is_te: bool) -> dict[str, Any] | None:
    """Extract user-provided screenplay lines directly into verbatim scenes."""
    match = re.search(r"(?:User Screenplay|Screenplay):\s*\n(.*)", prompt, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    raw_script = match.group(1).strip()
    # Filter non-empty dialogue or narrative lines
    lines = [
        re.sub(r"^(?:scene\s*\d+:?|narrator:|speaker\s*\d+:?|-|\*)\s*", "", l, flags=re.IGNORECASE).strip()
        for l in raw_script.splitlines() if l.strip() and not l.strip().startswith("#")
    ]
    if not lines:
        return None

    # Construct scenes preserving user dialogue as-is
    scenes = []
    dur_per_scene = max(4.0, 30.0 / len(lines[:5]))
    shot_types = ["wide", "medium", "close_up", "medium", "wide"]
    for idx, line in enumerate(lines[:5]):
        scenes.append({
            "scene_index": idx,
            "duration_seconds": dur_per_scene,
            "shot_type": shot_types[idx % len(shot_types)],
            "visual_prompt": f"Cinematic broadcast visual capturing: {line[:80]}",
            "dialogue": line,
        })

    return {
        "title": "Custom Screenplay Production",
        "hook_thesis": "Original narrative performance executing user-provided screenplay.",
        "target_duration_seconds": int(dur_per_scene * len(scenes)),
        "scenes": scenes,
    }


def _resolve_nature_storyboard(p_lower: str, is_te: bool) -> dict[str, Any] | None:
    """Synthesize diverse, multi-element nature and wildlife storyboards."""
    is_nature = any(k in p_lower for k in (
        "nature", "amazon", "rainforest", "ocean", "beach", "rain", "wind",
        "waterfall", "lagoon", "coral", "reef", "glacier", "fjords", "forest",
        "sanctuary", "wildlife", "safari", "savannah", "bamboo",
    ))
    if not is_nature:
        return None

    if any(k in p_lower for k in ("ocean", "beach", "bora bora", "seychelles", "coral", "lagoon")):
        title = "Azure Ocean Sanctuary & Pristine Coral Atolls"
        scenes = [
            {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Aerial view of turquoise coral atolls and powder-white sandbars in crystal lagoon, 4K ocean serenity", "dialogue": "శాంతమైన నీలి సముద్రపు అందాలు మరియు తెల్లని ఇసుక తీరాలు." if is_te else "Crystal turquoise waters lap against pristine white sandbars in a timeless ocean paradise."},
            {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Underwater 4K view of vibrant coral reef teeming with sea turtles and neon fish", "dialogue": "సముద్ర గర్భంలో రంగురంగుల పగడపు దిబ్బలు మరియు జలచరాలు." if is_te else "Beneath gentle rolling swells, radiant coral gardens shelter a vibrant marine sanctuary."},
            {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Dramatic granite boulders framing turquoise surf at golden hour sunset, 4K nature film", "dialogue": "సూర్యాస్తమయ కాంతులలో మురిసిపోతున్న సముద్ర తీరం." if is_te else "Sculpted granite boulders stand eternal watch as the golden sun sets across the horizon."},
            {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Gentle ocean waves washing over smooth sea-glass pebbles on quiet beach, 4K relaxation", "dialogue": "అలల సవ్వడితో సేదతీరే ప్రశాంతమైన బీచ్." if is_te else "Listen to the soothing cadence of rolling waves washing over sun-bleached shores."},
            {"scene_index": 4, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Dusk settling over tropical lagoon with glowing bioluminescent ripples, 4K broadcast still", "dialogue": "ప్రకృతి యొక్క అపురూపమైన సౌందర్యానికి ప్రణామం." if is_te else "Twilight deepens across the lagoon, leaving a feeling of boundless wonder and serene harmony."},
        ]
    elif any(k in p_lower for k in ("rain", "waterfall", "cherrapunji", "wind", "patagoni", "monsoon")):
        title = "Cascading Waterfalls & Wind-Swept Rain Sanctuary"
        scenes = [
            {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Majestic multi-tiered waterfall cascading down sheer green cliff face into misty gorge, 4K nature", "dialogue": "పర్వత శిఖరాల నుండి జాలువారే అద్భుతమైన జలపాతం." if is_te else "Thunderous cascades plummet from mist-shrouded emerald ridges into deep mountain gorges."},
            {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Monsoon rain droplets splashing rhythmically on broad tropical leaves and mossy rocks, 4K ASMR", "dialogue": "వర్షపు చినుకుల సవ్వడితో పులకించే పచ్చని ప్రకృతి." if is_te else "Fresh monsoon showers breathe renewal into every glistening fern and ancient river stone."},
            {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Wind-swept alpine ridges with dramatic moving cloud shadows over turquoise glacial lakes, 4K", "dialogue": "గాలుల హోరుతో కదిలే మేఘాల నీడలు." if is_te else "Powerful mountain winds sweep across vast valleys, sculpting glaciers and dancing across crystalline waters."},
            {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Rainbow forming in waterfall spray over lush emerald riverbank, 4K cinematic still", "dialogue": "జలపాతపు తుంపర్లలో విరిసిన అందమైన ఇంద్రధనుస్సు." if is_te else "A brilliant rainbow arcs through the crystalline mist as afternoon light pierces the cloudbreak."},
            {"scene_index": 4, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Serene panoramic view of green river valley flowing toward distant horizon under soft evening skies, 4K", "dialogue": "ప్రకృతి మాత ఒడిలో లభించే అసలైన ప్రశాంతత." if is_te else "The river carves its quiet journey forward, echoing the eternal heartbeat of untouched nature."},
        ]
    else:
        title = "Primeval Amazon Rainforest Canopy & Wildlife Sanctuary"
        scenes = [
            {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Aerial view gliding over infinite emerald Amazon canopy with winding silver river at sunrise, 4K nature", "dialogue": "దట్టమైన అడవులు మరియు ప్రవహించే నదుల అద్భుత దృశ్యం." if is_te else "The ancient emerald canopy stretches endlessly toward the horizon, cradled by winding riverways at dawn."},
            {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Volumetric golden sunbeams piercing deep jungle canopy onto giant ancient kapok roots and ferns, 4K", "dialogue": "సూర్యకిరణాల వెలుగులో మెరిసే పచ్చని అటవీ సంపద." if is_te else "Golden sunbeams pierce the rainforest canopy, awakening centuries-old kapok trees and vibrant orchids."},
            {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Vibrant scarlet macaws taking flight above lush riverbank canopy, 4K wildlife cinematography", "dialogue": "విహరించే రంగురంగుల పక్షులు మరియు వన్యప్రాణులు." if is_te else "Scarlet macaws and toucans glide overhead as the symphony of tropical wilderness fills the air."},
            {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Crystal-clear jungle creek flowing over polished amber pebbles into calm pool, 4K meditation", "dialogue": "నిర్మలమైన సెలయేరు మరియు ప్రకృతి శబ్దాలు." if is_te else "Crystal forest streams meander gently over sunlit pebbles, sustaining countless hidden micro-worlds."},
            {"scene_index": 4, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Golden hour twilight descending over calm Amazon river reflecting pastel sky, 4K broadcast still", "dialogue": "ప్రకృతి అందాలలో మునిగితేలే దివ్యమైన అనుభూతి." if is_te else "As twilight settles over the river, the rainforest rests in timeless peace and majesty."},
        ]

    return {
        "title": title,
        "hook_thesis": "Immerse in breathtaking natural wonders, pristine waters, and untouched landscapes.",
        "target_duration_seconds": 30,
        "scenes": scenes,
    }


def resolve_mock_storyboard(prompt: str) -> dict[str, Any]:
    """Return topic-accurate storyboard plan adhering to ScenePlan contracts.

    Dance prompts must remain dance prompts. Comedy and Bathukamma song defaults are
    only allowed when the user explicitly asks for them.
    """
    p_lower = prompt.lower()
    is_te = any(k in p_lower for k in ("telugu", "te-in", "te_in", "in te", "language: te", "te language", "telangana"))
    dance_keywords = ("dance", "folk dance", "village dance", "dappu", "jathara", "mass dance", "traditional dance", "dance video", "folk festival")
    comedy_keywords = ("comedy", "standup", "satire", "joke", "funny", "wfh", "office")
    is_dance_request = any(k in p_lower for k in dance_keywords)
    is_comedy_request = any(k in p_lower for k in comedy_keywords)

    # 1. Custom user script execution (verbatim dialogue preservation)
    custom_plan = _parse_custom_script_scenes(prompt, is_te)
    if custom_plan:
        return custom_plan

    # 2. Explicit dance intent must stay dance-centered
    if is_dance_request and not is_comedy_request:
        title = "Telangana Village Folk Dance"
        title_localized = "తెలంగాణ గ్రామీణ జానపద నృత్యం" if is_te else title
        return {
            "title": title,
            "title_localized": title_localized,
            "titles_multilingual": {"en": title, "te": title_localized},
            "hook_thesis": "A joyful Telangana village folk dance performance rooted in community rhythm, celebration, and cultural movement.",
            "target_duration_seconds": 30,
            "recommended_fps": 30,
            "vocal_gender": "female",
            "scenes": [
                {"scene_index": 0, "duration_seconds": 8.0, "location_hub": "Village common ground", "shot_type": "wide_shot", "choreography_phase": "intro_groove", "choreography_steps": "Traditional Telangana folk walk, graceful shoulder sways, synchronized group claps, and stepping pattern in a circle.", "visual_prompt": "Ultra-photorealistic 4K cinematic wide shot of a Telangana village dance circle at golden morning light, colorful traditional attire, paddy fields and terracotta homes in the background, authentic natural daylight, realistic skin tones, vibrant festive energy, no artificial yellow wash.", "motion_prompt": "Slow revealing cinematic entrance, villagers gathering in a lively circle, symmetric folk movements, natural foot taps and hand claps with genuine village celebration energy.", "dialogue": ""},
                {"scene_index": 1, "duration_seconds": 8.0, "location_hub": "Village courtyard", "shot_type": "medium_shot", "choreography_phase": "verse_acting", "choreography_steps": "Hip sways, expressive hand gestures, gentle spins, and rhythmic group response movements matching the folk beat.", "visual_prompt": "Ultra-photorealistic 4K cinematic medium shot of Telangana folk dancers in bright silk traditional attires, vibrant jewelry, jasmine flowers, green landscape backdrop, natural open-air daylight, strong festive composition, culturally authentic village setting.", "motion_prompt": "Fluid folk choreography with hand mudras, side steps, and playful turns, realistic human motion never exaggerated or slapstick, festive village mood.", "dialogue": ""},
                {"scene_index": 2, "duration_seconds": 8.0, "location_hub": "Village street", "shot_type": "close_up", "choreography_phase": "beat_drop_hook", "choreography_steps": "Quick foot stomps, turning spins, synchronized waist shifts, and confident energetic finishes with group formation.", "visual_prompt": "Ultra-photorealistic 4K cinematic close-up of a lead dancer with expressive smile, traditional Telangana costume, silver anklets, glass bangles, natural sunlight, festival decorations, authentic cultural detail, balanced composition.", "motion_prompt": "High-energy local folk hook sequence, synchronized footwork, celebratory faces, bright village backdrop, crisp 30fps motion, natural movement and joyful energy.", "dialogue": ""},
            ],
        }

    # 3. Multi-element global nature & wildlife resolution
    nature_plan = _resolve_nature_storyboard(p_lower, is_te)
    if nature_plan:
        return nature_plan

    # 4. Hyderabad cultural & travel guide
    if any(k in p_lower for k in ("hyderabad", "hyd", "charminar", "golconda")):
        return {
            "title": "Top Tourist Spots in Hyderabad",
            "hook_thesis": "Experience royal heritage and iconic monuments in Hyderabad.",
            "target_duration_seconds": 30,
            "scenes": [
                {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Majestic Charminar monument in Hyderabad illuminated during golden hour sunset with Old City bazaars, 4K broadcast still", "dialogue": "చరిత్ర, సంస్కృతికి నిలయమైన హైదరాబాద్ నగరానికి స్వాగతం! మన ప్రయాణం చారిత్రక చార్మినార్ తో ప్రారంభమవుతుంది." if is_te else "Welcome to Hyderabad, the historic City of Pearls! Our journey begins at the legendary Charminar."},
                {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Golconda Fort stone ramparts and royal hilltop citadel in Hyderabad, 4K broadcast still", "dialogue": "అద్భుతమైన గోల్కొండ కోటను దర్శించండి, ఇక్కడ ప్రపంచ ప్రసిద్ధ కోహినూర్ వజ్రం చరిత్ర దాగి ఉంది." if is_te else "Next, explore the mighty Golconda Fort, where the world-famous Koh-i-Noor diamond once echoed."},
                {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Hussain Sagar lake at sunset with illuminated Buddha statue and necklace road glistening, 4K travel film", "dialogue": "హుస్సేన్ సాగర్ సరస్సు వద్ద రమణీయమైన బుద్ధ విగ్రహం మరియు నెక్లెస్ రోడ్డు సాయంత్రపు వెలుగులు చూడండి." if is_te else "Take in the serene beauty of Hussain Sagar lake and the iconic Buddha statue at dusk."},
                {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Salar Jung Museum grand archways and priceless antique treasures under warm ambient gallery lights, 4K", "dialogue": "సాలార్ జంగ్ మ్యూజియంలో ప్రపంచ ప్రసిద్ధ అపురూప కళాఖండాలను మరియు వీల్డ్ రెబెక్కా శిల్పాన్ని చూడండి." if is_te else "Step into the Salar Jung Museum, home to priceless treasures from around the world."},
                {"scene_index": 4, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Chowmahalla Palace grand Darbar Hall with Belgian crystal chandeliers and royal courtyards, 4K", "dialogue": "నిజాం నవాబుల వైభవాన్ని ప్రతిబింబించే చౌమహల్లా ప్యాలెస్ రాయల్ దర్బార్ హాల్ తో యాత్ర ముగుస్తుంది." if is_te else "Conclude your royal tour at Chowmahalla Palace, marveling at the opulence of Nizam royalty."},
            ],
        }

    # 5. Destination & travel catalogs
    dest = lookup_destination_preset(p_lower)
    if dest:
        return dest

    # 6. Fallback comedy storyboard only when explicitly asked
    if is_comedy_request:
        return {
            "title": "IT Employee Remote Work Confusions",
            "hook_thesis": "Why working from home turned into a 24-hour standup call",
            "target_duration_seconds": 30,
            "scenes": [
                {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "close_up", "visual_prompt": "Cinematic close-up of tired software engineer looking at dual 4K monitors in dark room", "dialogue": "వర్క్ ఫ్రమ్ హోమ్ అని చెప్పి రోజుకి 18 గంటలు లాగిన్ లోనే ఉంటే... జీతం ఏమో నెలకి 30 వేలు!" if is_te else "Working from home means logging in for 18 hours a day, all for a modest monthly salary!"},
                {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Modern apartment desk with cold coffee cup and laptop displaying chat windows", "dialogue": "మేనేజర్ కాల్ వచ్చిన ప్రతిసారీ వైఫై కట్ అయిందని అబద్ధం చెప్పే కళ లో మనం డాక్టరేట్ చేసాం." if is_te else "We earned a doctorate in the fine art of claiming the Wi-Fi dropped every time our manager calls."},
                {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Sun rising through high-rise window as engineer stares into distance laughing", "dialogue": "కానీ ఆఫీస్ కి వెళ్లి ట్రాఫిక్ లో గంటలు నిలబడటం కంటే ఇంట్లోనే బెస్ట్ కదా!" if is_te else "Still, working from home beats standing in city traffic for hours every day!"},
                {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Kitchen counter with burnt toast as Slack notification dings repeatedly on phone", "dialogue": "లంచ్ చేద్దామనుకునే లోపే క్లయింట్ ఎమర్జెన్సీ మీటింగ్ పెట్టేస్తారు." if is_te else "Just as you sit down for lunch, an urgent client ping suddenly arrives."},
                {"scene_index": 4, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Evening sunset from balcony holding cup of chai smiling peacefully", "dialogue": "ఏది ఏమైనా సాయంత్రం వేడి వేడి చాయ్ తాగితే అన్ని కష్టాలు మాయం!" if is_te else "No matter what happens, a hot cup of evening chai makes all the stress melt away!"},
            ],
        }

    # 7. Explicit fallback for ambiguous prompts: keep generic but dance-safe and non-comedic.
    return {
        "title": "Village Festival Rhythm",
        "hook_thesis": "A vibrant community performance celebrating regional folk movement, music, and unity.",
        "target_duration_seconds": 30,
        "scenes": [
            {"scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Authentic village festival square with colorful cloth banners, natural daylight, warm community energy, and dancers gathering for a traditional folk performance.", "dialogue": ""},
            {"scene_index": 1, "duration_seconds": 6.0, "shot_type": "medium", "visual_prompt": "Traditional folk dancers in rhythmic motion, candid smiles, realistic movement, local attire, vibrant natural setting.", "dialogue": ""},
            {"scene_index": 2, "duration_seconds": 6.0, "shot_type": "close_up", "visual_prompt": "Close-up of lead dancer stepping in time with the beat, jewelry catching light, warm natural skin tones, culturally authentic village setting.", "dialogue": ""},
            {"scene_index": 3, "duration_seconds": 6.0, "shot_type": "wide", "visual_prompt": "Final group formation with joyful expressions, bright festival colors, natural daylight, community celebration atmosphere.", "dialogue": ""},
        ],
    }


__all__ = ["resolve_mock_storyboard"]
