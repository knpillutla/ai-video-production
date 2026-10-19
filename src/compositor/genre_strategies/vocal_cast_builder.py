"""Vocal Cast & Prompt Builder for Music Video Productions.

Directs character staging, gender modality (solo female, solo male, duet),
animation styling for kids songs (3D Pixar/storybook CGI - child safety compliance),
and musical Suno tags alignment.
"""

from __future__ import annotations

import re
from typing import Any, Tuple


def is_kids_song_genre(sub_genre: str | None, theme: str | None = None) -> bool:
    """Check if the requested song format is a children's rhyme or kids song."""
    text = f"{sub_genre or ''} {theme or ''}".lower()
    return any(k in text for k in ("kid", "kids", "rhyme", "nursery", "children", "lullaby_kids"))


def build_vocal_suno_tags(
    sub_genre: str | None,
    culture: str,
    gender: str = "duet",
    tempo_bpm: int = 100,
) -> str:
    """Compose musically accurate Suno genre tags aligned to mood and performer gender."""
    eff_sub = (sub_genre or "romantic_melody").lower()
    
    # Vocal tag descriptor
    if gender == "male":
        vocal_tag = "male vocals"
    elif gender == "female":
        vocal_tag = "female vocals"
    else:
        vocal_tag = "duet, male and female vocals"

    if is_kids_song_genre(eff_sub):
        return (
            f"kids song, nursery rhyme, {culture}, playful, cheerful, ukulele, glockenspiel, "
            f"bouncy rhythm, handclaps, bright melodic whistle, family friendly, joyful {vocal_tag}, "
            f"{max(96, tempo_bpm)} bpm, clean broadcast master"
        )

    if any(k in eff_sub for k in ("romantic", "romance", "ballad", "love")):
        return (
            f"romantic ballad, heartfelt {culture}, acoustic guitar, bansuri flute, soft strings, "
            f"lush melodic chords, soulful, {vocal_tag}, {tempo_bpm} bpm, broadcast mix"
        )

    if any(k in eff_sub for k in ("soul", "devotion", "spiritual")):
        return (
            f"soulful acoustic ballad, {culture}, meditative bansuri, resonant acoustic cello, "
            f"heartfelt devotion, serene emotional warmth, {vocal_tag}, {tempo_bpm} bpm, broadcast master"
        )

    if any(k in eff_sub for k in ("happy", "celebrat", "joy", "cheerful")):
        return (
            f"happy uplifting celebration, {culture}, bright acoustic strumming, joyous rhythm, "
            f"cheerful brass flourishes, vibrant {vocal_tag}, {tempo_bpm} bpm, broadcast mix"
        )

    if any(k in eff_sub for k in ("mass", "dappu", "teenmaar")):
        return (
            f"mass commercial dance, heavy thumping dappu drums, fast teenmaar rhythm, {culture}, "
            f"energetic brass trumpets, whistle drops, catchy hook couplets, energetic {vocal_tag}, "
            f"138 bpm, thumping bass downbeats, clean punchy 48khz broadcast master"
        )

    if any(k in eff_sub for k in ("party", "club", "dance", "beat")):
        return (
            f"energetic party dance, {culture}, groovy bassline, infectious drum groove, "
            f"club rhythm, {vocal_tag}, 124 bpm, high energy broadcast master"
        )

    return (
        f"{culture} {eff_sub.replace('_', ' ')}, acoustic instruments, melodic harmonies, "
        f"{vocal_tag}, {tempo_bpm} bpm, clean 48khz broadcast master"
    )


def build_cast_and_visual_directives(
    slot: int,
    fem: Any,
    male: Any,
    culture: str,
    setting: str,
    gender: str = "duet",
    is_kids: bool = False,
) -> Tuple[str, str]:
    """Generate prompt directives and negative prompt constraints for character staging."""
    eff_gender = (gender or "duet").lower()

    if is_kids:
        # Child safety & platform ethics: 3D Pixar / Disney storybook animation style only
        if eff_gender == "male":
            cast_dir = (
                f"KIDS 3D ANIMATION DIRECTIVE (SOLO BOY - STRICT CHILD SAFETY COMPLIANCE):\n"
                f"- AESTHETIC: High-end 3D Pixar / Disney animated storybook CGI render. STRICT PROHIBITION against photorealistic real human children or photos.\n"
                f"- CHARACTER: Adorable animated 3D boy character with big curious expressive eyes, joyful friendly smile, colorful playful clothes matching {culture} heritage, clean stylized 3D CGI cartoon geometry.\n"
                f"- ENVIRONMENT: Whimsical, vibrantly colored storybook world set in {setting}, warm sunny lighting, cheerful cartoon details.\n"
                f"- CONSTRAINT: Solo animated boy character only. No adult themes, zero photorealistic human photography.\n"
            )
            neg_constraints = "photorealistic, real photograph, real human photo, adult, scary, dark, creepy, wax doll, gloomy"
        elif eff_gender == "female":
            cast_dir = (
                f"KIDS 3D ANIMATION DIRECTIVE (SOLO GIRL - STRICT CHILD SAFETY COMPLIANCE):\n"
                f"- AESTHETIC: High-end 3D Pixar / Disney animated storybook CGI render. STRICT PROHIBITION against photorealistic real human children or photos.\n"
                f"- CHARACTER: Adorable animated 3D girl character with big curious sparkly eyes, joyful cheerful smile, colorful cute outfit matching {culture} heritage, clean stylized 3D CGI cartoon geometry.\n"
                f"- ENVIRONMENT: Whimsical, vibrantly colored storybook world set in {setting}, warm sunny lighting, cheerful cartoon details.\n"
                f"- CONSTRAINT: Solo animated girl character only. No adult themes, zero photorealistic human photography.\n"
            )
            neg_constraints = "photorealistic, real photograph, real human photo, adult, scary, dark, creepy, wax doll, gloomy"
        else:
            cast_dir = (
                f"KIDS 3D ANIMATION DIRECTIVE (BOY & GIRL DUO - STRICT CHILD SAFETY COMPLIANCE):\n"
                f"- AESTHETIC: High-end 3D Pixar / Disney animated storybook CGI render. STRICT PROHIBITION against photorealistic real human children or photos.\n"
                f"- CHARACTERS: Charming animated 3D boy and girl best friends duo, big curious eyes, playful happy expressions, bright colorful storybook clothes, clean stylized 3D CGI cartoon geometry.\n"
                f"- ENVIRONMENT: Whimsical, vibrantly colored storybook world set in {setting}, warm sunny lighting, cheerful playful cartoon details.\n"
                f"- CONSTRAINT: Animated child duo only. Zero photorealistic human photography.\n"
            )
            neg_constraints = "photorealistic, real photograph, real human photo, adult, scary, dark, creepy, wax doll, gloomy"
        return cast_dir, neg_constraints

    # Standard Adult Musical Video Staging
    if eff_gender == "male":
        cast_dir = (
            f"SOLO MALE LEAD DIRECTIVE (SLOT #{slot} - STRICT MALE ONLY STAGING):\n"
            f"- MALE LEAD: '{male.name}', Age {male.age}, natural fit medium-athletic build, {male.skin} skin, "
            f"{male.face}, {male.hair}.\n"
            f"- CONTEXT-MATCHING ELEGANT & ATTRACTIVE MALE OUTFIT:\n"
            f"  * Strikingly handsome, stylish, and elegant tailored attire suited to {setting}.\n"
            f"  * Impeccably styled in {male.palette}: tailored linen/fine-cotton shirt, subtle textured layer or stylish jacket, tailored trousers, polished leather footwear.\n"
            f"  * WRIST-WORN WATCH: Premium chronograph watch strapped securely to his LEFT WRIST (never on chest/shirt).\n"
            f"  * STRICT MODESTY (ZERO NUDITY): Tasteful, fully covered handsome styling. Zero bare chest, zero nudity.\n"
            f"- STRICT NEGATIVE DIRECTIVE: SOLO MALE ONLY. The image MUST depict ONLY this male character. "
            f"STRICTLY FORBIDDEN: NO WOMEN, NO FEMALE CHARACTERS, NO COUPLE, NO DATING PARTNER.\n"
        )
        neg_constraints = "woman, female, girl, women, couple, hand holding, romantic partner, nudity, naked, bare chest, watch on shirt, chest badge"
    elif eff_gender == "female":
        cast_dir = (
            f"SOLO FEMALE LEAD DIRECTIVE (SLOT #{slot} - STRICT FEMALE ONLY STAGING):\n"
            f"- FEMALE LEAD: '{fem.name}', Age {fem.age}, natural fit medium-slender graceful build, {fem.skin} skin, "
            f"{fem.face}, {fem.hair}.\n"
            f"- CONTEXT-MATCHING ATTRACTIVE DESIGNER DRESS (BEAUTIFUL, COLORFUL, ELEGANT WITH DESIGNS):\n"
            f"  * Context-Matching & Highly Attractive: Breathtakingly beautiful, colorful, and elegant dress authentically suited to {setting}.\n"
            f"  * Palette & Designer Patterns: Rich saturated tones or luminous radiant pastels in {fem.palette} featuring intricate artistic designs—delicate floral embroidery, fine gold/silver threadwork borders, tasteful patterns, layered ruffles, or lacework that pop against the scenery.\n"
            f"  * Dynamic photogenic fabrics (flowing chiffon, georgette, or silk) that billow gracefully in the breeze and during turns/twirls.\n"
            f"  * STRICT MODESTY (FAMILY-FRIENDLY - ZERO NUDITY / ZERO SEXUALIZATION): Tasteful, fully modest and elegant necklines (boat neck, modest round neck, mandarin, or modest sweetheart with full coverage), completely covered torso and midriff, non-revealing, graceful silhouette. STRICTLY PROHIBIT deep cleavage, plunging necklines, sheer/translucent reveals, bare midriffs, or suggestive cuts.\n"
            f"  * CURATED 4-ZONE ACCESSORIES (GEMINI AUTONOMOUS CONTEXTUAL SELECTION - MANDATORY IN SCRIPT & IMAGE PROMPTS):\n"
            f"    Gemini MUST autonomously decide and describe context-matched accessories across all 4 zones based on the background, weather, and culture of {setting}:\n"
            f"    - HAIR (Zone 1): Context-matched blossoms (e.g. wild alpine flowers, jasmine, or roses) or delicate pearl/gold barrette pins chosen by Gemini to look cute and romantic.\n"
            f"    - EARS & NECK (Zone 2): Context-matched sparkling earrings/jhumkas and delicate pendant chain styled on a modest high neckline.\n"
            f"    - HANDS & WRISTS (Zone 3): Context-matched graceful slim dress watch, delicate gold/silver bangles or chain bracelets, and dainty rings.\n"
            f"    - LEGS & ANKLES (Zone 4): Context-matched dainty ankle chain (anklet / payal) paired with setting-appropriate footwear (sandals, heels, or embellished juttis).\n"
            f"    - SCRIPT & PROMPT CONTRACT: Gemini MUST record these chosen accessories in 'characters[0].outfit_description' AND explicitly include them in 'visual_prompt' across EVERY scene so each image reflects her cute, charming, and stylish appearance.\n"
            f"- STRICT NEGATIVE DIRECTIVE: SOLO FEMALE ONLY. The image MUST depict ONLY this female character. "
            f"STRICTLY FORBIDDEN: NO MEN, NO MALE CHARACTERS, NO COUPLE, NO BOYFRIEND.\n"
        )
        neg_constraints = "man, male, boy, men, couple, hand holding, romantic partner, nudity, naked, cleavage, sexualized outfit, revealing clothes, low cut, exposed midriff, provocative attire, translucent fabric, misplaced accessories, heavy thick waist, watch on shirt"
    else:
        cast_dir = (
            f"COORDINATED COUPLE DIRECTIVE (SLOT #{slot} - DUET STAGING):\n"
            f"- FEMALE LEAD: '{fem.name}', Age {fem.age}, natural fit medium-slender graceful slim build with defined waist and natural feminine curves (graceful SLIM build), {fem.skin} skin, {fem.face}, {fem.hair}.\n"
            f"  * Context-Matching & Attractive Designer Dress: Breathtakingly beautiful, colorful, elegant designer gown in {fem.palette} with delicate floral embroidery or fine threadwork designs, tailored to flatter her graceful slim waist and silhouette (strictly NO boxy, loose, or shapeless tunics).\n"
            f"  * STRICT MODESTY (FAMILY-FRIENDLY & ZERO NUDITY): Elegant modest high boat neckline, mandarin collar, or high round neck with full upper chest coverage. Strictly zero cleavage, zero plunging necklines, zero low V-necks, zero bare midriff.\n"
            f"  * CURATED 4-ZONE ACCESSORIES (GEMINI AUTONOMOUS CONTEXTUAL SELECTION - MANDATORY IN SCRIPT & IMAGE PROMPTS):\n"
            f"    Gemini MUST autonomously decide and describe context-matched accessories across all 4 zones based on the background, weather, and culture of {setting}:\n"
            f"    - HAIR (Zone 1): Context-matched blossoms or delicate pearl/gold barrette pins chosen by Gemini to look cute and romantic.\n"
            f"    - EARS & NECK (Zone 2 - MANDATORY NECK ACCESSORY): Context-matched sparkling earrings/jhumkas AND delicate necklace or pendant chain styled gracefully around her neck over the high neckline. Females ALWAYS wear neck accessories; NEVER omit the necklace or pendant chain in any scene prompt.\n"
            f"    - HANDS & WRISTS (Zone 3): Context-matched graceful slim dress watch, delicate gold/silver bangles or chain bracelets, and dainty rings.\n"
            f"    - LEGS & ANKLES (Zone 4): Context-matched dainty ankle chain (anklet / payal) paired with setting-appropriate footwear (sandals, heels, or boots).\n"
            f"    - SCRIPT & PROMPT CONTRACT: Gemini MUST record these chosen accessories in 'characters[0].outfit_description' AND explicitly include ALL 4 ZONES (including the necklace around her neck) in 'visual_prompt' across EVERY scene so each image reflects her cute, charming, and stylish appearance.\n"
            f"- MALE LEAD: '{male.name}', Age {male.age}, natural fit medium-athletic frame (MEDIUM BUILT), {male.skin} skin, {male.face}, {male.hair}.\n"
            f"  * Context-Matching & Attractive: Strikingly handsome, elegant tailored attire in {male.palette} suited to {setting}, tailored trousers, precision chronograph watch strapped securely to left wrist.\n"
            f"- DIRECTORIAL FRAMING & ANTI-HALLUCINATION GUARD:\n"
            f"  * Both leads must be framed together naturally or solo. NEVER describe an off-screen partner's hands reaching into the frame.\n"
            f"  * Authentic romantic chemistry engaging with the background, zero stiff separated stances.\n"
        )
        neg_constraints = (
            "nudity, naked, cleavage, sexualized outfit, revealing clothes, low cut, exposed midriff, "
            "provocative attire, translucent fabric, watch on shirt, chest badge, misplaced jewelry, "
            "plastic doll skin, wax figure, distorted anatomy, zero outfit distortion, disembodied hands, floating hands, "
            "phantom limbs, severed arms, severed hands, extra limbs, off-screen reaching, boxy tunic, "
            "baggy loungewear, shapeless clothing, low V-neck, plunging neckline, stiff posture, standing separated, "
            "head cropped, cut off head, cut off face, head touching top edge, no headroom, tight headroom, top frame cut off, forehead cropped, hair touching top frame"
        )

    return cast_dir, neg_constraints



