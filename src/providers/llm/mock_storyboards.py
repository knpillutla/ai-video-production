"""Topic-accurate deterministic offline mock storyboard resolver."""

from typing import Any


def resolve_mock_storyboard(prompt: str) -> dict[str, Any]:
    """Return topic-accurate storyboard plan adhering to ScenePlan contracts."""
    p_lower = prompt.lower()

    if any(k in p_lower for k in ("lauterbrunnen", "rainy village", "swiss rain", "rain walk")):
        return {
            "title": "Lauterbrunnen Rainy Village Walking Tour",
            "hook_thesis": "Immerse in the tranquil rain-slicked chalets and cascading waterfalls of the Swiss Alps.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Lauterbrunnen aesthetic, traditional Swiss timber chalets with red geraniums along rain-slicked asphalt reflecting green cliffs, cascading Staubbach waterfall in mist, 4K walking tour POV",
                    "dialogue": "Rain falls gently over Lauterbrunnen as cascading waterfalls plunge from mist-shrouded limestone cliffs into the valley.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "First-person perspective walking under umbrella past dark timber alpine barns, raindrops splashing in emerald meadows, distant cowbells, 4K steady glide",
                    "dialogue": "Every rain-slicked cobblestone and wooden balcony reflects the quiet majesty of Switzerland's most dramatic mountain village.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Winding mountain lane leading toward the historic Lauterbrunnen church steeple framed by towering alpine rock faces and hanging rain clouds, 4K peaceful still",
                    "dialogue": "Listen to the soothing rhythm of mountain rain mingling with the eternal roar of glacial cascades.",
                },
            ],
        }

    if any(k in p_lower for k in ("swiss", "grindelwald", "eiger", "jungfrau", "alpine")):
        return {
            "title": "Grindelwald 8K Alpine Wonderland",
            "hook_thesis": "Behold the awe-inspiring peaks, turquoise glacial rivers, and iconic red trains of Grindelwald.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Grindelwald alpine wonderland, towering snow-capped Eiger and Jungfrau peaks under crisp azure sky, arched stone viaduct crossing turquoise river, red Swiss alpine train, 8K travel film",
                    "dialogue": "High above the valley floor, the iconic red mountain train glides gracefully over historic stone arches against the Eiger's north face.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Rolling emerald green pastures with grazing cows and dark-timber Swiss chalets, turquoise glacial meltwater river rushing over white stones, 8K cinematic sweep",
                    "dialogue": "Turquoise glacial meltwaters carve their path through lush green meadows in pure alpine serenity.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Breathtaking panoramic vista of Grindelwald valley as golden afternoon sunlight illuminates glacier ice caps, 8K broadcast still",
                    "dialogue": "Grindelwald stands as a timeless monument to nature's grandest architecture.",
                },
            ],
        }

    if any(k in p_lower for k in ("innsbruck", "tegernsee", "scenic drive", "road trip")):
        return {
            "title": "Alpine Rainy Scenic Road Trip",
            "hook_thesis": "A contemplative road trip from Innsbruck to Tegernsee along wet mountain highways.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Wet winding alpine highway glistening with car taillights, windshield rain droplets, misty pine forests and dark Tyrolean chalets, 4K road trip POV",
                    "dialogue": "Wipers glide rhythmically across the windshield as we wind through mist-draped Austrian mountain passes.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "Scenic lakeside view of historic white church with red steeple standing quietly on peninsula, calm grey lake waters reflecting clouds, 4K travel film",
                    "dialogue": "Beside the glassy waters of Tegernsee, the red church steeple stands vigilant in the afternoon drizzle.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Smooth forward vehicle tracking shot along tree-lined lake road as dusk settles over misty Bavarian alpine peaks, 4K cinematic still",
                    "dialogue": "A journey defined not by speed, but by the tranquil melody of falling rain on open roads.",
                },
            ],
        }

    if any(k in p_lower for k in ("greek", "aegean", "sea cave", "cycladic", "milos", "santorini")):
        return {
            "title": "Greek Cycladic Coastal & Aegean Sea Caves",
            "hook_thesis": "Drift through turquoise sea caves and whitewashed Cycladic coves.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Milos aesthetic, crystal-clear turquoise sea water with rippling sun caustics, white limestone sea cave entrance with curved arches, lone wooden boat, 4K coastal relaxation",
                    "dialogue": "Sunlight penetrates crystal-clear Aegean waters, casting dancing caustics across ancient limestone sea arches.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "Interior of luminous sea cave looking out toward turquoise bay, azure water reflections on natural stone ceiling, gentle wave ripples, 4K tranquil view",
                    "dialogue": "Inside this natural stone sanctuary, the gentle ocean surf echoes in eternal peaceful stillness.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Whitewashed Cycladic stone cottages with Aegean blue doors nestled against limestone cliffs over calm bay at noon, 4K broadcast still",
                    "dialogue": "White cliffs and cobalt horizons blend together in quintessential Mediterranean peace.",
                },
            ],
        }

    if any(k in p_lower for k in ("lake como", "como", "amalfi", "bellagio", "italian coastal")):
        return {
            "title": "Italian Coastal & Lake Como Morning",
            "hook_thesis": "Savor tranquil morning coffee along the pastel terraces of Lake Como.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "Waterfront dining terrace set with white linen tablecloth, espresso cup, pink roses, seated traveler looking at sparkling blue lake, 4K Mediterranean aesthetic",
                    "dialogue": "Morning breaks across Lake Como with diamond sunlight shimmering across deep sapphire waters.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Historic Bellagio pastel peach and terracotta villas rising against cypress hills, passenger ferry gliding across calm water, 4K travel film",
                    "dialogue": "Centuries of romantic Italian architecture rise gracefully from water's edge into verdant hills.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Sun shimmering bokeh on lake surface framing distant snow-dusted Alpine foothills under golden morning light, 4K cinematic still",
                    "dialogue": "A moment of pure Mediterranean dolce far niente that lingers in memory forever.",
                },
            ],
        }

    if any(k in p_lower for k in ("ibiza", "lounge", "rooftop", "sunset")):
        return {
            "title": "Ibiza Luxury Sunset Rooftop Lounge",
            "hook_thesis": "Experience the ultimate Balearic sunset lounge relaxation.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Luxury Balearic seaside rooftop terrace, infinity pool reflecting golden setting sun, glass hurricane lanterns with flickering candles, silhouetted palms, 4K architectural digest",
                    "dialogue": "The Mediterranean sun melts into the horizon, setting the infinity pool ablaze in golden amber.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "White daybed loungers with chic guests enjoying twilight ambient chillout beats and ocean breeze, warm candle glows, 4K lounge vibes",
                    "dialogue": "Warm candle lanterns flicker as twilight settles over the Balearic coastline in effortless elegance.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Deep violet dusk sky over calm sea ripples, illuminated architectural rooftop terrace with warm ambient lighting, 4K broadcast still",
                    "dialogue": "As dusk turns to night, the rhythm of Ibiza breathes peace and sublime sophistication.",
                },
            ],
        }

    if any(k in p_lower for k in ("forest", "rainforest", "stream", "nature sanctuary")):
        return {
            "title": "Primeval Emerald Forest Sanctuary",
            "hook_thesis": "Wander through ancient mossy roots and crystal babbling streams.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Primeval temperate rainforest, massive ancient moss-covered tree roots, crystal-clear babbling rocky stream, sunbeams piercing emerald canopy, 4K nature ASMR",
                    "dialogue": "Deep in the primeval sanctuary, ancient mossy roots embrace crystal waters in timeless silence.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "Dappled volumetric sunbeams filtering through deep green ferns onto smooth river pebbles and water ripples, 4K tranquil nature",
                    "dialogue": "Volumetric sunbeams carve through emerald mist, breathing life into every fern and moss-draped branch.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Winding walking trail disappearing into lush emerald old-growth forest under soft morning ambient light, 4K cinematic still",
                    "dialogue": "In this untouched emerald sanctuary, nature's gentle heartbeat restores the soul.",
                },
            ],
        }

    if any(k in p_lower for k in ("thailand", "karst", "chiang mai", "krabi")):
        return {
            "title": "Tropical Thailand Karst Wonders",
            "hook_thesis": "Discover blooming mountain flower plantations and towering limestone karsts.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Chiang Mai aesthetic, geometric blooming flower plantation with vibrant rows of magenta and yellow blossoms, teak chalet with thatched roof, palm trees, 4K travel film",
                    "dialogue": "Vibrant rows of tropical blossoms carpet the valley floor beneath towering emerald limestone peaks.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Towering limestone karst peaks shrouded in morning mist with distant Buddhist pagoda on cliff top, tropical sunrise glow, 4K cinematic sweep",
                    "dialogue": "Misty karst towers rise dramatic toward morning skies, sheltering centuries of serene mountain heritage.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Traditional teak chalet framed by lush palms and blooming flower fields as morning sun illuminates the landscape, 4K broadcast still",
                    "dialogue": "Thailand's mystical mountain landscapes inspire wonder and peaceful reflection.",
                },
            ],
        }

    if "hyderabad" in p_lower:
        return {
            "title": "Top Tourist Spots in Hyderabad",
            "hook_thesis": "Experience royal heritage and iconic monuments in Hyderabad.",
            "target_duration_seconds": 30,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 6.0, "shot_type": "wide",
                    "visual_prompt": "Majestic Charminar monument in Hyderabad illuminated during golden hour sunset with Old City bazaars, 4K broadcast still",
                    "dialogue": "Welcome to Hyderabad, the historic City of Pearls! Our journey begins at the legendary Charminar.",
                },
                {
                    "scene_index": 1, "duration_seconds": 6.0, "shot_type": "wide",
                    "visual_prompt": "Golconda Fort stone ramparts and royal hilltop citadel in Hyderabad, 4K broadcast still",
                    "dialogue": "Next, explore the mighty Golconda Fort, where the world-famous Koh-i-Noor diamond once echoed.",
                },
                {
                    "scene_index": 2, "duration_seconds": 6.0, "shot_type": "medium",
                    "visual_prompt": "White granite Buddha statue in Hussain Sagar Lake in Hyderabad, 4K broadcast still",
                    "dialogue": "Cruise along Hussain Sagar Lake to behold the serene monolithic Buddha statue.",
                },
            ],
        }

    if "paris" in p_lower:
        return {
            "title": "Paris Tourist Attractions",
            "hook_thesis": "Discover iconic monuments of Paris.",
            "target_duration_seconds": 15,
            "scenes": [
                {
                    "scene_index": 0, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Golden hour view of the Eiffel Tower rising above Champ de Mars in Paris, 4K broadcast still",
                    "dialogue": "Welcome to Paris, the City of Light! Our journey begins at the majestic Eiffel Tower.",
                },
                {
                    "scene_index": 1, "duration_seconds": 5.0, "shot_type": "medium",
                    "visual_prompt": "Musée du Louvre glass pyramid at twilight, 4K broadcast still",
                    "dialogue": "Next, immerse yourself in world-class art and timeless culture inside the Louvre Museum.",
                },
                {
                    "scene_index": 2, "duration_seconds": 5.0, "shot_type": "wide",
                    "visual_prompt": "Arc de Triomphe framed by the Champs-Élysées at dusk, 4K broadcast still",
                    "dialogue": "Finally, marvel at the triumphant Arc de Triomphe crowning the Champs-Élysées.",
                },
            ],
        }

    return {
        "title": "IT Employee Remote Work Confusions",
        "hook_thesis": "Why working from home turned into a 24-hour standup call",
        "target_duration_seconds": 480,
        "scenes": [
            {
                "scene_index": 0, "duration_seconds": 3.8, "shot_type": "close_up",
                "visual_prompt": "Cinematic close-up of tired software engineer looking at dual 4K monitors in dark room",
                "dialogue": "వర్క్ ఫ్రమ్ హోమ్ అని చెప్పి రోజుకి 18 గంటలు లాగిన్ లోనే ఉంటే... జీతం ఏమో నెలకి 30 వేలు!",
            },
            {
                "scene_index": 1, "duration_seconds": 4.2, "shot_type": "medium",
                "visual_prompt": "Modern apartment desk with cold coffee cup and laptop displaying chat windows",
                "dialogue": "మేనేజర్ కాల్ వచ్చిన ప్రతిసారీ వైఫై కట్ అయిందని అబద్ధం చెప్పే కళ లో మనం డాక్టరేట్ చేసాం.",
            },
            {
                "scene_index": 2, "duration_seconds": 4.0, "shot_type": "wide",
                "visual_prompt": "Sun rising through high-rise window as engineer stares into distance laughing",
                "dialogue": "కానీ ఆఫీస్ కి వెళ్లి ట్రాఫిక్ లో గంటలు నిలబడటం కంటే ఇంట్లోనే బెస్ట్ కదా!",
            },
        ],
    }


__all__ = ["resolve_mock_storyboard"]
