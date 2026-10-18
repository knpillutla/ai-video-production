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
            "   * DUET / ROMANTIC CO-LEAD HIGH-CTR INTIMACY & PHYSICAL CHEMISTRY (MANDATORY):\n"
            "     - Never depict the couple as stiff, distant strangers sitting apart staring blankly!\n"
            "     - Scene 1 (Intimate Glance): Standing close, he gently wraps an arm around her waist while she rests a hand lightly on his chest, looking into each other's eyes.\n"
            "     - Scene 2 (Environmental Shared Joy): Walking side-by-side along the scenic path with fingers tightly intertwined ('holding hands'), sharing a genuine laugh.\n"
            "     - Scene 3 (Tender Touch & Nature): He playfully tucks a blooming wildflower into her hair ('putting flower in hair') or she places her hands gently around his neck in a tender close moment.\n"
            "     - Scene 4 (Atmospheric Panorama): Leaning shoulder-to-shoulder against a rustic wooden fence or stone bridge, his arm draped comfortably over her shoulder, gazing together at the horizon.\n"
        )
    elif eff_gender == "male":
        chemistry_text = (
            "   * SOLO MALE LEAD DYNAMIC STORYTELLING & CHARISMA:\n"
            "     - Never depict a stiff passport photo standing with arms flat at sides!\n"
            "     - Pose 1 (Confident Environmental Lean): Casual swagger leaning back against a rustic timber railing or stone wall, one hand in pocket, sleeves rolled up showing chronograph watch on left wrist, gazing warmly.\n"
            "     - Pose 2 (Sensory Mountain Walk): Walking forward through the alpine meadow or scenic trail, looking thoughtfully towards the peaks with the cool breeze ruffling his hair.\n"
            "     - Pose 3 (Candid Reflective Moment): Sitting casually on a wooden dock or boulder, one knee raised, looking out across the glistening water with an evocative, soulful expression.\n"
        )
    else:  # Solo female
        chemistry_text = (
            "   * SOLO FEMALE LEAD DYNAMIC SENSORY IMMERSION & HIGH-CTR MAGNETISM:\n"
            "     - Never depict a stiff passport photo standing straight with hands down!\n"
            "     - Pose 1 (Sensory Floral / Nature Touch): Gracefully leaning down to gently inhale the fragrance of a blooming wildflower ('smelling a flower') with eyes closed in pure serenity, or gently tucking a blossom behind her ear ('putting flower in hair').\n"
            "     - Pose 2 (Dynamic Motion / Dress Swirl): Mid-twirl in the wildflower meadow with dress fabric billowing softly around her, looking playfully over her shoulder with an enchanting, magnetic smile.\n"
            "     - Pose 3 (Atmospheric Breeze Immersion): Standing near a scenic wooden fence or viewpoint, head tilted back slightly enjoying the mountain breeze through her hair, hand lightly grazing collarbone, radiant expression.\n"
            "     - Pose 4 (Reflective Candid): Sitting gracefully on a grassy knoll or mossy stone, one hand resting on chin, gazing dreamily toward the sunset/distant snow-capped peaks.\n"
        )

    return (
        "MANDATORY HIGH-CTR BACKGROUND-SPECIFIC POSE DIRECTIVE (ANTI-STATIC MANDATE):\n"
        "1. STRICT BAN ON STATIC 'STAND STILL' PORTRAITS: Characters must NEVER stand stiffly upright with arms at sides staring blankly into the camera. Every image must depict an active, natural, cinema-grade physical pose.\n"
        "2. ACTIVE SENSORY ENJOYMENT OF ENVIRONMENT & WEATHER:\n"
        "   - The character(s) must physically interact with and enjoy their surroundings:\n"
        "     * Floral / Meadow / Garden: Smelling flowers, picking a petal, brushing fingertips across grass, tucking flower in hair.\n"
        "     * Breeze / Mountain / Vista: Tilting head back to feel the fresh breeze, hair catching sunlight, open arms embracing nature.\n"
        "     * Water / Lake / River: Dipping fingers into crystal water, walking barefoot along shoreline, feeling cool spray.\n"
        "     * Sunlight / Golden Hour: Glancing over shoulder with radiant smile, golden rim lighting, hand shielding eyes.\n"
        f"{chemistry_text}"
        f"3. DIVERSE MULTI-SCENE PROGRESSION ({num_scenes} SCENES):\n"
        "   - Every scene MUST specify a distinct camera shot type ('camera_shot_type') AND a distinct physical interaction ('character_pose').\n"
        "   - 'visual_prompt' in each scene MUST describe the exact physical action and environmental engagement in vivid detail.\n\n"
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
                "pose": "Tender romantic glance, his hand gently on her waist while she touches his chest",
                "prompt_ext": "He gently places an arm around her waist while she rests her hand softly on his chest, sharing an intimate romantic gaze with the scenic background.",
            },
            {
                "shot_type": "wide_cinematic",
                "pose": "Walking together with hands tightly intertwined, laughing in the open breeze",
                "prompt_ext": "Walking together along the scenic trail with fingers intertwined ('holding hands'), sharing a genuine happy laugh in the open mountain sunlight.",
            },
            {
                "shot_type": "close_up",
                "pose": "Forehead-to-forehead tender moment, arms softly around neck",
                "prompt_ext": "Standing close with foreheads nearly touching, her arms gently around his neck, eyes half-closed in deep emotional connection.",
            },
            {
                "shot_type": "three_quarter",
                "pose": "Leaning shoulder-to-shoulder on rustic fence gazing at vista",
                "prompt_ext": "Leaning shoulder-to-shoulder against a rustic timber railing, his arm comfortably over her shoulder, gazing together at the panoramic peaks.",
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
