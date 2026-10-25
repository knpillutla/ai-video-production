"""Vocal Music Video Prompt Engineering and Photorealism Service.

Enforces:
1. True human skin micro-texture (eradicates plastic, waxy, doll-like skin).
2. Concert mode outfit and staging continuity (exact same stage attire and setting across all scenes).
3. Cultural wardrobe and 4-zone accessories compliance (Rule 12).
"""

from __future__ import annotations

import re
from typing import Any


def sanitize_skin_prompt(prompt: str) -> str:
    """Strip plastic/waxy trigger words and inject realistic human skin descriptors."""
    cleaned = prompt
    # Replace over-smoothed / porcelain / glowing buzzwords that cause waxy AI skin
    cleaned = re.sub(
        r"(?i)\b(porcelain-ivory|porcelain-wheatish|porcelain|glowing\s+radiant|glowing\s+peach-fair|flawless\s+airbrushed|airbrushed|flawless)\s+skin\b",
        "authentic human skin texture with natural fine pores and subtle micro-details",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)\bglowing\s+skin\b",
        "natural human skin texture with fine pores",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)\bpeach-fair\s+skin\b",
        "natural fair-wheatish human skin",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)\bglowing\s+(?:complexion|countenance)\b",
        "natural human complexion",
        cleaned,
    )
    # Remove negative terms accidentally placed in positive prompts (diffusion models can attend to them)
    cleaned = re.sub(r"(?i)\b(?:zero|no)\s+(?:plastic|wax|sheen|doll)[^,\.;]*", "", cleaned)
    return cleaned.strip(", ")


def get_canonical_concert_outfit(storyboard_data: dict[str, Any]) -> str:
    """Derive an explicit, structurally locked, modest stage outfit for concert mode."""
    chars = storyboard_data.get("characters") or []
    outfit_raw = ""
    if chars and chars[0].get("outfit_description"):
        outfit_raw = chars[0]["outfit_description"]
    elif storyboard_data.get("scenes"):
        s1 = storyboard_data["scenes"][0].get("visual_prompt", "")
        m = re.search(r"(?i)\bwearing\s+([^,\.;]+(?:gown|dress|attire|suit|outfit|sari|lehenga)[^,\.;]*)", s1)
        if m:
            outfit_raw = m.group(1).strip()

    if not outfit_raw:
        theme = storyboard_data.get("theme") or storyboard_data.get("genre") or "performance"
        outfit_raw = f"royal sapphire blue silk designer anarkali gown with modest high boat neckline and delicate gold zari embroidery matching the {theme} ambiance"

    outfit_clean = re.sub(r"(?i)\b(exact identical|strictly identical|signature|the identical)\b", "", outfit_raw).strip(", ")
    outfit_clean = re.split(r"(?i)\bcurated\s+4-zone\b", outfit_clean)[0].strip(", ")

    # Explicitly lock sleeves, neckline, and midriff to prevent diffusion model from randomizing bell sleeves or v-necks
    sleeve_clause = ", fitted narrow long sleeves reaching wrists with delicate gold zari embroidery cuffs (strictly no bell sleeves, no cape sleeves, no loose sleeves)"
    neckline_clause = ", closed modest high boat neckline with fine gold piping (strictly no v-neck, no slit neckline, no scoop neck)"
    torso_clause = ", continuous fully covered solid blue midriff with vertical gold zari floral filigree embroidery down the center bodice"

    return (
        f"strictly identical stage outfit: continuous one-piece {outfit_clean}{sleeve_clause}{neckline_clause}{torso_clause}, "
        f"without head scarf, veil, or chunni, "
        f"full closed torso coverage, zero bare midriff, zero exposed stomach, zero crop top, zero saree drape, "
        f"slim gold watch on left wrist, sparkling teardrop earrings, exactly identical dress across all concert shots"
    )


def get_vocal_negative_prompt(is_concert: bool = False, is_female: bool = True) -> str:
    """Generate comprehensive negative prompt for music video visual synthesis."""
    neg = [
        "disfigured, deformed, ugly, distorted, bad anatomy, extra limbs, extra hands, missing limbs, floating limbs",
        "plastic skin, waxy skin, doll skin, artificial gloss, airbrushed, oversaturated yellow",
        "cleavage, sexualized outfit, revealing clothes, low cut, scoop neck, wide neckline, deep neckline, exposed midriff, bare midriff, bare stomach, bare belly, crop top, bare chest, nudity, naked",
    ]
    if is_concert:
        neg.append(
            "singer in audience, singer in crowd, singer in bleachers, singer sitting in seats, audience in foreground, people beside singer, people in front of singer, "
            "carrying microphone stand, dragging microphone stand, floating mic stand, "
            "outfit change, different dress, costume change, wardrobe change, costume variation, "
            "bare midriff, exposed stomach, bare belly, crop top, lehenga choli, saree drape, pallu, "
            "different sleeves, sleeveless, cap sleeves, bell sleeves, loose sleeves, flared sleeves, kimono sleeves, cape sleeves, "
            "different neckline, plunging neckline, scoop neckline, wide neckline, low cut collar, slit neckline, v-neck, casual clothes, "
            "flat studio wall, blank grey background, concrete wall, dull studio backdrop, plain room"
        )
    if is_female:
        neg.append("man, male, boy, men, boyfriend, couple, beard, mustache, stubble")
    return ", ".join(neg)


def build_character_anchors(storyboard_data: dict[str, Any], base_prompt: str) -> str:
    """Build persistent character visual anchor prefix to lock face and outfit across scenes."""
    chars = storyboard_data.get("characters") or []
    char_anchors = []
    for c in chars:
        parts = [f"{c['age']}-year-old" for _ in [1] if c.get("age")] + [
            c[k] for k in ("gender", "body_composition", "hair_and_facial_features") if c.get(k)
        ]
        if c.get("outfit_description"):
            parts.append(f"wearing {c['outfit_description']}")
        char_anchors.append(f"{c.get('name', 'Lead')} ({', '.join(parts)})")

    facial_hair_hint = ""
    if base_prompt:
        m_fh = re.search(
            r"(\b(?:curtain fade|stubble|beard|mustache|haircut|hairstyle|wavy hair|braid|bun|curls)\b[^\.,;]*)",
            base_prompt,
            re.IGNORECASE,
        )
        if m_fh and not any("stubble" in a.lower() or "hair" in a.lower() for a in char_anchors):
            facial_hair_hint = f" Facial and hair styling: {m_fh.group(1)}."

    anchor = f"Lead character identity: {'; '.join(char_anchors)}.{facial_hair_hint} Same exact character face, hair, and outfit in every scene. " if char_anchors else ""
    return sanitize_skin_prompt(anchor)


def build_vocal_scene_prompt(
    raw_prompt: str,
    storyboard_data: dict[str, Any],
    anchor_prefix: str,
    trigger_words: str,
    is_cutaway: bool,
    is_concert: bool,
    is_male: bool,
    is_female: bool,
    is_duet: bool,
) -> str:
    """Construct a photorealistic, cinema-grade prompt for a music video scene."""
    # 1. Sanitize raw prompt to remove negative sections and plastic buzzwords
    effective = f"{trigger_words}, {raw_prompt}".strip(", ") if trigger_words else raw_prompt
    effective = re.split(r"(?i)\bnegative\s*(?:constraints|prompt)?\s*:", effective)[0].strip(", ")
    effective = sanitize_skin_prompt(effective)

    if is_cutaway:
        return effective

    # In concert mode: scrub conflicting wardrobe and crowd-placement descriptions from scene's raw_prompt
    canonical_stage_outfit = ""
    if is_concert:
        canonical_stage_outfit = get_canonical_concert_outfit(storyboard_data)
        effective = re.sub(
            r"(?i)\b(?:wearing|dressed in|outfit:?)\s+[^,\.;]*\b(?:gown|dress|attire|suit|outfit|saree|sari|lehenga|choli|skirt|blouse|top|frock|kurti|anarkali)\b[^,\.;]*[,\.;]?",
            "",
            effective,
        )
        effective = re.sub(r"(?i)\b(?:in|among|amidst|surrounded by)\s+(?:the\s+)?(?:audience|crowd|bleachers|seats)\b", "on the elevated main stage", effective)
        effective = re.sub(r"(?i)\b(?:curve of cheering )?arena bleachers\b", "distant arena bleachers blurred in deep background", effective)
        effective = re.sub(r"(?i)\b(?:holding|carrying)\s+(?:the\s+)?(?:stand|chrome stand)\b", "singing at the vertical stand microphone", effective)

    # 2. Gender and framing safety tokens
    if is_duet:
        safety_tokens = (
            "generous upper headroom, characters framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, modest high boat neckline for female lead, zero cleavage, "
            "fully covered torso and midriff, continuous modest coverage, zero bare midriff, zero crop top, "
            "fully visible leads in frame, zero disembodied hands, zero floating limbs, handsome male lead with watch on left wrist, "
            "beautiful female lead in elegant modest designer attire, tasteful modest family-friendly attire, zero nudity, zero bare chest"
        )
    elif is_male:
        safety_tokens = (
            "generous upper headroom, character framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, fully visible lead in frame, zero disembodied hands, zero floating limbs, "
            "natural fit lean-athletic masculine build, defined sharp jawline, neat light facial stubble, stylish haircut, "
            "tailored collared shirt, strictly one chronograph watch on left wrist only, completely bare right wrist with zero watch, "
            "zero duplicate watches, zero watch on right arm, tasteful modest family-friendly attire, zero bare chest, zero nudity"
        )
    else:
        safety_tokens = (
            "generous upper headroom, character framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, modest high boat neckline, zero cleavage, "
            "fully covered torso and midriff, continuous modest coverage, zero bare midriff, zero exposed stomach, zero crop top, "
            "fully visible lead in frame, zero disembodied hands, zero floating limbs, graceful slender-curvy silhouette, "
            "delicate hair flowers or pins, delicate necklace and sparkling pendant around neck, matching earrings, "
            "slim wrist watch, delicate bangles, dainty ankle chain anklet, cute charming elegant styling, zero nudity"
        )

    # 3. Contextual expression derivation
    ctx = f"{storyboard_data.get('genre', '')} {storyboard_data.get('song_type', '')} {storyboard_data.get('mood', '')} {raw_prompt}".lower()
    if any(k in ctx for k in ("mass", "dappu", "teenmaar", "dance", "troupe", "party", "club", "energetic", "celebrat", "jathara")):
        expression_token = "radiant energetic joyful smile, infectious beaming expression, lively confident sparkle in eyes, happy animated laugh"
        troupe_token = ", vibrant synchronized background troupe of backup dancers in coordinated festive party attire grooving in soft cinematic bokeh"
    elif any(k in ctx for k in ("sad", "heartbreak", "melanchol", "sorrow", "tear", "alone", "cry")):
        expression_token = "tender wistful gaze, gentle soulful reflective emotion, poignant heartfelt expression, emotional eyes"
        troupe_token = ""
    else:
        expression_token = "warm affectionate tender smile, soft dreamy romantic gaze, heartfelt soulful facial expression, vibrant lively eyes"
        troupe_token = ""

    # 4. Photorealistic Human Skin micro-texture tokens (Universal across all character shots)
    photorealism_tokens = (
        "raw 35mm film photograph, shot on Arri Alexa 35, 50mm Master Prime lens, f/2.0 aperture, "
        "natural authentic human skin texture with visible fine pores and subtle micro-details, natural matte complexion, "
        "lifelike subsurface scattering, authentic human eye moisture and corneal reflections, soft cinematic stage illumination, "
        "unretouched studio portrait photography, 8k broadcast quality"
    )

    if is_concert:
        stage_staging = (
            "standing centerstage on the elevated main performance stage behind floor stage monitors, "
            "singing into a vintage chrome stage microphone mounted on a vertical chrome stand resting on the stage floor, "
            f"{canonical_stage_outfit}, "
            "hair styled open in blowout waves with delicate pins. "
            "Audience is strictly in the distant background below the stage waving cyan and amber lightsticks in deep creamy bokeh, "
            "overhead lighting trusses with volumetric spotlight beams cutting through theatrical haze"
        )
        full_prompt = f"{anchor_prefix}{trigger_words + ', ' if trigger_words else ''}{stage_staging}. Camera framing: {effective}, {expression_token}, {safety_tokens}, {photorealism_tokens}"
    else:
        full_prompt = f"{anchor_prefix}{effective}, {expression_token}, {safety_tokens}{troupe_token}, {photorealism_tokens}"

    return re.sub(r"\s+", " ", full_prompt).strip(", ")


__all__ = [
    "sanitize_skin_prompt",
    "get_canonical_concert_outfit",
    "get_vocal_negative_prompt",
    "build_character_anchors",
    "build_vocal_scene_prompt",
]
