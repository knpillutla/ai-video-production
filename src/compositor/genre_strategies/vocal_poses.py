"""Directorial Engine for Background-Specific Dynamic Poses and High-CTR Staging.

Directs Gemini to synthesize active, context-aware character poses enjoying the
surrounding environment, weather, and props (smelling flowers, wind in hair,
hand on partner's waist/neck, hands intertwined), eliminating static "stand still" passport photos.
"""

from __future__ import annotations

from typing import Any


def build_environmental_pose_directive(
    gender: str = "duet",
    theme: str = "soulful romantic melody",
    culture: str = "Indian",
    num_scenes: int = 3,
    is_mass: bool = False,
) -> str:
    """Build authoritative Gemini prompt directive for dynamic, background-specific poses."""
    eff_gender = (gender or "duet").lower()

    if eff_gender == "duet":
        chemistry_text = (
            "   * AUTONOMOUS DUET INTERACTION & CHEMISTRY DERIVATION (NO HARDCODED TEMPLATES):\n"
            "     - Autonomously invent natural, authentic, context-matching couple interactions derived directly from the specific background elements, props, and terrain of each scene.\n"
            "     - Derive poses that naturally engage with the setting (e.g., walking together along terrain trails with intertwined fingers, leaning side-by-side against authentic architectural rails or stone fences, candid laughing glances, gentle wind-in-hair moments).\n"
            "     - Strictly prohibit stiff, separated mannequin stances where characters stand apart with arms dangling flat at sides staring blankly.\n"
        )
    elif eff_gender == "male":
        chemistry_text = (
            "   * AUTONOMOUS SOLO MALE CHARISMA & STORYTELLING DERIVATION:\n"
            "     - Autonomously invent dynamic, context-matching poses derived from the specific background architecture, terrain, and weather of each scene.\n"
            "     - Engage naturally with the environment (e.g., walking through the trail, leaning thoughtfully against scenic props, candid seated reflections overlooking vistas).\n"
            "     - Never depict a stiff passport photo standing with arms flat at sides staring blankly.\n"
        )
    else:  # Solo female
        chemistry_text = (
            "   * AUTONOMOUS SOLO FEMALE SENSORY IMMERSION & HIGH-CTR MAGNETISM:\n"
            "     - Autonomously invent graceful, context-matching poses derived from the environment, breeze, sunlight, and natural scenery of each scene.\n"
            "     - Engage dynamically with surroundings (e.g., twirling in open meadows with flowing fabric, enjoying the mountain breeze, candid reflective smiles, touching hair ornaments).\n"
            "     - Never depict a stiff passport photo standing straight with hands down.\n"
        )

    mass_inserts_text = (
        "8. AUTONOMOUS CONTEXTUAL CUTAWAYS & DRONE INSERTS (MASS SONGS ONLY):\n"
        "   - In mass songs, do NOT show the lead character in every single image! Gemini must autonomously decide where to interleave 1 to 2 high-impact CONTEXTUAL INSERT / CUTAWAY scenes (e.g. during percussive bridge rolls, fast drum buildups, or scene transitions):\n"
        "     * Archetype A (Percussion Close-up): Macro shot of energetic village drummers' hands beating dappu frame drums with wooden karras in swirling dust ('dummu'). (Camera: 'punch' / 'crash-zoom' or 'dollyin').\n"
        "     * Archetype B (Festival Aerial / Drone Flight): Sweeping panoramic drone flyover across illuminated festival grounds, effigies, lanterns, and cheering crowd under twilight sky. (Camera: 'drift-up-right' / 'pedestal-rise').\n"
        "     * Archetype C (Troupe Whirl Formation): Dynamic wide shot of coordinated male and female troupe dancers spinning in colorful lehengas/dhotis throwing flower petals into the air. (Camera: 'orbit' / 'dollyout').\n"
        "   - For these contextual scenes, set 'character_pose': 'Contextual Cutaway: <description>', and omit the lead hero/heroine so the camera can execute breathtaking drone and cinematography movements on the festival environment and troupe!\n"
    ) if is_mass else ""

    return (
        "AUTONOMOUS CONTEXT-DRIVEN POSE & FRAMING DIRECTIVE (NO HARDCODED POSES):\n"
        "1. DYNAMIC CONTEXTUAL DERIVATION: Gemini must autonomously derive unique, cinema-grade character poses for each scene based strictly on the background terrain, weather, architecture, and narrative mood. Do NOT use generic or static templates.\n"
        "2. STRICT BAN ON OFF-SCREEN REACHING & DISEMBODIED HANDS (CRITICAL):\n"
        "   - In close-ups or intimate interactions, NEVER describe an off-screen partner's hands or arms reaching into the frame (e.g., do NOT write 'Dev reaches into the frame to touch her hair/ear').\n"
        "   - For couple interactions, BOTH characters' faces, heads, and upper bodies MUST be clearly visible together in the frame (two-shot), OR the physical action must be self-directed (e.g., she touches her own hair blossom while smiling warmly at him beside her).\n"
        "   - Strictly prohibit disembodied hands, floating limbs, or severed arms entering from frame edges.\n"
        "3. UNIVERSAL FEMALE COMPOSITION & ACCESSORIES (EVERY SCENE):\n"
        "   - The female lead's attractive composition MUST remain consistent across ALL scenes: graceful medium-slender slim build, defined slender waist, balanced natural feminine curves, and flattering designer gown (strictly NO boxy, loose, or shapeless garments).\n"
        "   - Neckline must be an elegant, modest high boat neckline, mandarin collar, or high round neck with full upper chest coverage (strictly zero cleavage, zero low-cut V-necks).\n"
        "   - AUTONOMOUS CONTEXTUAL ACCESSORIES IN EVERY SCENE: Gemini must autonomously decide the exact setting-matched accessories across all 4 zones (hair, neckline/ears, hands/wrists, legs/ankles) based on the background and context, and explicitly include them in 'characters[0].outfit_description' and each scene's 'visual_prompt' to ensure she looks delightfully cute, charming, and stylish in every frame.\n"
        "4. ACTIVE SENSORY ENGAGEMENT WITH ENVIRONMENT & WEATHER:\n"
        "   - Characters must naturally engage with their surroundings (breeze ruffling hair, sunlight reflections, touching natural textures, walking along trails, resting against scenic timber/stone rails).\n"
        f"{chemistry_text}"
        f"5. DIVERSE MULTI-SCENE PROGRESSION ({num_scenes} SCENES):\n"
        "   - Every scene MUST specify a distinct camera shot type ('camera_shot_type') AND a distinct physical interaction ('character_pose') derived autonomously from that specific scene's environment.\n"
        "   - 'visual_prompt' in each scene MUST describe the exact physical action and environmental engagement in vivid detail.\n"
        "6. MANDATORY BROADCAST SAFE HEADROOM & UPPER FRAME CLEARANCE (RULE OF THIRDS):\n"
        "   - In ALL shots (wide, medium, two-shot, walking, seated), camera framing MUST maintain generous headroom: leave at least 15% to 25% clear open vertical space above the tallest character's head to the top edge of the 16:9 canvas.\n"
        "   - Characters' eye lines must sit along the upper-third line (roughly 30-35% down from the top), showing the expansive open sky, mountains, or architecture above them.\n"
        "   - Strictly prohibit tight headroom, cropped hair, cut off foreheads, or characters' heads touching the top edge of the frame, ensuring faces remain 100% visible on all desktop and mobile players without being cropped.\n"
        "7. MASS SONG & PARTY BACKGROUND TROUPE (MALE & FEMALE DANCERS - MANDATORY):\n"
        "   - For all mass songs, dance videos, and indoor party settings, NEVER depict an empty or deserted room.\n"
        "   - The midground and background MUST feature an energetic, coordinated dance troupe of BOTH male and female backup dancers in matching colorful festive attire.\n"
        "   - Direct background dancers performing synchronized hook steps, clapping on the downbeat, or cheering in soft optical bokeh/depth of field.\n"
        "   - The solo lead remains the radiant centerstage superstar in sharp foreground focus with full 4-zone accessories and modest attire.\n"
        f"{mass_inserts_text}"
        "8. LIVE CONCERT & STAGE PERFORMANCES (ACCOMPANISTS, TROUPE & AUDIENCE - MANDATORY):\n"
        "   - When setting is a concert (classical sabha, singing arena, dance recital, amphitheatre), NEVER depict an empty or deserted stage!\n"
        "   - Classical Concert / Sabha: Seated on raised carpeted dais, authentic accompanists (mridangam/tabla, tanpura, violin), brass lamps, and seated connoisseur audience in soft optical bokeh.\n"
        "   - Live Singing Concert / Arena: Lead singer at center stage with dynamic microphone, illuminated proscenium, stage spot beams, and cheering audience with lightsticks.\n"
        "   - Dance Concert / Recital: Expansive performance proscenium floor, coordinated background troupe flanking leads, theatrical lighting cues, and engaged audience in auditorium.\n"
        "   - Instrumental Virtuoso Performance & Jugalbandi:\n"
        "     * Characters hold and actively play their signature instruments: graceful fingers on flute holes, plucking sitar/veena/guitar strings, or bowing violin/cello with emotional absorption (bhava).\n"
        "     * Macro cinematic camera: close-up on instrument craftsmanship (polished wood grain, vibrating strings) intercut with medium shots of the musician completely immersed in the melody. Zero singing or mouthing lyrics.\n"
        "   - Leads remain in razor-sharp foreground focus; audience, stage rigging, and accompanists provide rich cinematic depth-of-field.\n"
        "9. MANDATORY CONTEXT-DRIVEN FACIAL EXPRESSIONS & EMOTIVE ACTING (ABHINAYA):\n"
        "   - Strictly prohibit blank, deadpan, expressionless, neutral staring, or robotic faces.\n"
        "   - Every scene's 'visual_prompt' MUST explicitly direct vivid, authentic facial expressions matching the lyrical context:\n"
        "     * Romantic / Soulful Melodies: Tender affectionate smile, soft dreamy gaze, gentle warmth, eyes full of emotion and longing.\n"
        "     * Mass Song / Party / Dance: Radiant, infectious, high-voltage joyful grin, energetic confidence, lively teasing sparkle in eyes.\n"
        "     * Melancholic / Love Ballad: Tender wistful gaze, gentle nostalgic emotion, subtle reflective depth.\n"
        "     * Devotional / Spiritual: Serene peaceful countenance, blissfully meditative smile of inner peace.\n"
        "     * Playful / Banter: Mischievous playful smirk, sparkling laughing eyes, charming teasing expression.\n"
        "   - Characters must look genuinely alive, emotionally connected, and expressive in every frame.\n\n"
    )


def get_offline_dynamic_scene_poses(
    country: str,
    culture: str,
    character_desc: str,
    gender: str = "female",
    num_scenes: int = 3,
    setting: str = "Alpine Meadow",
) -> list[dict[str, Any]]:
    """Return deterministic, high-CTR dynamic poses for offline mock pipelines (Rule 8 $0.00 spend)."""
    eff_gender = (gender or "female").lower()

    is_concert = any(k in setting.lower() for k in ("concert", "stage", "sabha", "recital", "theatre", "amphitheatre"))
    is_instrumental = any(k in setting.lower() for k in ("instrumental", "bansuri", "sitar", "veena", "guitar", "piano", "violin"))

    if is_instrumental:
        if eff_gender == "duet":
            pose_catalog = [
                {"shot_type": "medium_shot", "pose": "Virtuoso instrumental jugalbandi dialogue, exchanging intricate melodic phrases", "prompt_ext": "Seated gracefully playing signature acoustic instruments in intense harmonious dialogue, exchanging joyful musical smiles as melodies intertwine."},
                {"shot_type": "wide_cinematic", "pose": "Atmospheric wide panoramic shot of both master musicians on stage or scenic setting", "prompt_ext": "Cinematic wide perspective of the two instrumentalists performing in full flow, beautiful scenic background and warm acoustic lighting."},
                {"shot_type": "close_up", "pose": "Extreme macro close-up of fingers dancing across instrument strings or flute holes", "prompt_ext": "Crisp macro close-up of skilled fingers plucking instrument strings and sliding across frets, wood grain texture and vibrating strings in razor-sharp focus."},
            ]
        else:
            pose_catalog = [
                {"shot_type": "medium_shot", "pose": "Deeply absorbed solo instrumental performance, fingers gliding effortlessly", "prompt_ext": "Seated gracefully with signature instrument in hands, fingers executing intricate melodic ornamentations, face serene and lost in musical bliss."},
                {"shot_type": "wide_cinematic", "pose": "Expansive scenic view of solo virtuoso performing against breathtaking landscape", "prompt_ext": "Wide cinematic vista of the master instrumentalist playing in the serene open setting, gentle breeze and soft natural lighting."},
                {"shot_type": "close_up", "pose": "Macro close-up on instrument craftsmanship and expressive hand movement", "prompt_ext": "Detailed macro close-up of fingers dancing across the instrument, warm wood finish, soulful emotive expression on musician's face."},
            ]
    elif is_concert:
        if eff_gender == "duet":
            pose_catalog = [
                {"shot_type": "medium_shot", "pose": "Harmonious duet performance at center stage, trading melodious vocal lines", "prompt_ext": "Performing together at center stage under warm theatrical spotlights, smiling as they harmonize, live accompanists and engaged audience in soft optical bokeh."},
                {"shot_type": "wide_cinematic", "pose": "Grand stage panoramic two-shot with ambient stage lighting and audience silhouette", "prompt_ext": "Wide proscenium stage perspective with glowing stage backdrops, couple singing together in sharp focus with audience silhouettes in foreground."},
                {"shot_type": "close_up", "pose": "Soulful emotive harmony close-up, feeling the melodic climax", "prompt_ext": "Intense emotive close-up of both vocalists singing the signature hook couplet with radiant heartfelt smiles under warm spotlight beams."},
            ]
        elif eff_gender == "male":
            pose_catalog = [
                {"shot_type": "medium_shot", "pose": "Confident stage performance at microphone stand, gesturing to the rhythm", "prompt_ext": "Singing at center stage into a vintage dynamic microphone, chronograph watch visible on left wrist, stage spot beams and live band in soft bokeh."},
                {"shot_type": "wide_cinematic", "pose": "Expansive live concert stage view, interacting warmly with audience", "prompt_ext": "Wide stage view under sweeping architectural spotlights, lead singer holding the stage with backing musicians and audience silhouettes in soft focus."},
                {"shot_type": "close_up", "pose": "Emotive vocal delivery with eyes closed, lost in the melodic cadence", "prompt_ext": "Expressive close-up singing with heartfelt emotion, hand near chest feeling the resonance, warm stage rim light catching his hair."},
            ]
        else:  # female
            pose_catalog = [
                {"shot_type": "medium_shot", "pose": "Graceful stage performance, emotive singing or dance mudra under spotlights", "prompt_ext": "Performing at center stage in elegant modest designer dress, singing with expressive hand gestures, live accompanists and audience in soft optical bokeh."},
                {"shot_type": "wide_cinematic", "pose": "Grand stage perspective with dramatic lighting, shimmering attire", "prompt_ext": "Expansive proscenium stage view with theatrical warm glow, graceful lead singer centerstage with 4-zone accessories shining under spotlights, audience silhouettes."},
                {"shot_type": "close_up", "pose": "Expressive soulful facial emotion (abhinaya) during melodic hook", "prompt_ext": "Soulful close-up, radiant expressive eyes and serene smile singing the earworm hook, soft stage bokeh in background."},
            ]
    elif eff_gender == "duet":
        pose_catalog = [
            {
                "shot_type": "medium_shot",
                "pose": "Tender romantic stance, standing close on scenic trail with fingers intertwined",
                "prompt_ext": "Standing close together on the scenic trail with fingers tenderly intertwined ('holding hands'), leaning their shoulders gently in with radiant genuine smiles, modest high boat neckline, graceful slender-curvy silhouette.",
            },
            {
                "shot_type": "wide_cinematic",
                "pose": "Walking together with hands tightly intertwined, laughing in the open breeze",
                "prompt_ext": "Walking together along the scenic trail with fingers intertwined ('holding hands'), sharing a genuine happy laugh in the open mountain sunlight, dress fluttering softly.",
            },
            {
                "shot_type": "close_up",
                "pose": "Intimate profile two-shot, leaning against rustic fence rail",
                "prompt_ext": "Intimate two-shot profile leaning side-by-side against a rustic timber railing, BOTH faces and upper bodies clearly visible together, Dev smiling warmly beside Simran, zero disembodied hands.",
            },
            {
                "shot_type": "three_quarter",
                "pose": "Leaning shoulder-to-shoulder on rustic fence gazing at vista",
                "prompt_ext": "Leaning shoulder-to-shoulder against a rustic timber railing, his arm comfortably over her shoulder, gazing together at the panoramic peaks, elegant modest attire.",
            },
        ]
    elif eff_gender == "male":
        pose_catalog = [
            {
                "shot_type": "medium_shot",
                "pose": "Casual confident lean against rustic fence, warm magnetic smile",
                "prompt_ext": "Leaning casually against a rustic timber railing, one hand in pocket, sleeves rolled up displaying chronograph watch on left wrist, confident warm smile.",
            },
            {
                "shot_type": "wide_cinematic",
                "pose": "Walking forward through meadow with wind in hair, looking towards peaks",
                "prompt_ext": "Walking forward through the wildflower meadow, looking thoughtfully towards the snowy peaks with the cool alpine breeze ruffling his dark wavy hair.",
            },
            {
                "shot_type": "close_up",
                "pose": "Emotive singing performance, hand over chest feeling the rhythm",
                "prompt_ext": "Expressive singing close-up, hand placed over his chest feeling the musical cadence, soulful eyes reflecting the golden sunset light.",
            },
        ]
    else:  # female
        pose_catalog = [
            {
                "shot_type": "medium_shot",
                "pose": "Sensory floral immersion, gently smelling a blooming wildflower",
                "prompt_ext": "Gracefully holding a freshly picked wildflower near her nose, gently inhaling its fragrance with eyes closed in serene bliss ('smelling a flower').",
            },
            {
                "shot_type": "wide_cinematic",
                "pose": "Mid-twirl in wildflower meadow, dress swirling outward dynamically",
                "prompt_ext": "Mid-twirl in the vibrant alpine meadow with her dress billowing out gracefully, looking back over her shoulder with an enchanting radiant smile.",
            },
            {
                "shot_type": "three_quarter",
                "pose": "Playfully tucking a blossom behind her ear in mountain breeze",
                "prompt_ext": "Leaning playfully near a rustic fence, fingers tucking a bright yellow wildflower into her wavy hair ('putting flower in hair'), wind caught in her hair.",
            },
            {
                "shot_type": "close_up",
                "pose": "Dreamy reflective gaze towards distant snow-capped peaks",
                "prompt_ext": "Sitting on a sunlit grassy slope, hand resting gently on chin, gazing dreamily towards the distant snow-capped peaks with heartfelt expression.",
            },
        ]

    scenes = []
    motions = ["dollyin", "tilt-up", "pan-right", "orbit-left", "dollyout"]
    for i in range(max(1, num_scenes)):
        idx = i % len(pose_catalog)
        item = pose_catalog[idx]
        m = motions[i % len(motions)]
        scenes.append({
            "scene_index": i + 1,
            "camera_shot_type": item["shot_type"],
            "character_pose": item["pose"],
            "camera_motion": m,
            "local_drone": {"movement": m, "start_pan": "center", "start_zoom": "normal", "start_tilt": "center", "rationale": "Choreographic beat progression"},
            "location_hub": f"Scenic Setting {i+1} ({country})",
            "visual_prompt": f"4K photorealistic cinematic music video scene in {country}, {setting}. {character_desc}. {item['prompt_ext']}",
        })
    return scenes
