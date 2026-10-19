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
        "8. MANDATORY CONTEXT-DRIVEN FACIAL EXPRESSIONS & EMOTIVE ACTING (ABHINAYA):\n"
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

    if eff_gender == "duet":
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
    for i in range(max(1, num_scenes)):
        idx = i % len(pose_catalog)
        item = pose_catalog[idx]
        scenes.append({
            "scene_index": i + 1,
            "camera_shot_type": item["shot_type"],
            "character_pose": item["pose"],
            "location_hub": f"Scenic Setting {i+1} ({country})",
            "visual_prompt": f"4K photorealistic cinematic music video scene in {country}, {setting}. {character_desc}. {item['prompt_ext']}",
        })
    return scenes
