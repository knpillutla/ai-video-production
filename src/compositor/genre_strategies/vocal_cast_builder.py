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
    
    # Vocal tag descriptor - anchored to prevent high-pitch vocoder cracking
    if gender == "male":
        vocal_tag = "male vocals, smooth tenor, warm chest voice, clean melodic control"
    elif gender == "female":
        vocal_tag = "female vocals, sweet melodic clarity"
    else:
        vocal_tag = "duet, male and female vocals, smooth tenor with warm chest resonance"

    if is_kids_song_genre(eff_sub):
        return (
            f"catchy hummable kids song, nursery rhyme, {culture}, playful, cheerful, ukulele, glockenspiel, "
            f"bouncy rhythm, handclaps, bright melodic whistle, memorable sing-along hook, joyful {vocal_tag}, "
            f"{max(96, tempo_bpm)} bpm, clean broadcast master"
        )

    if "instrumental_jugalbandi" in eff_sub or ("instrumental" in eff_sub and "jugalbandi" in eff_sub):
        return f"pure instrumental jugalbandi, virtuoso musical dialogue, acoustic bansuri flute and sitar, intricate melodic trade, mridangam, tabla, acoustic strings, dynamic crescendo, zero vocals, 88 bpm, audiophile broadcast master"

    if "instrumental" in eff_sub:
        return f"pure instrumental solo, {culture}, virtuoso acoustic performance, bansuri flute, resonant sitar strings, warm acoustic cello, zero vocals, pure acoustic clarity, {tempo_bpm} bpm, audiophile broadcast master"

    if any(k in eff_sub for k in ("jugalbandi", "sawaal", "jawaab", "face_off")):
        return (
            f"vocal jugalbandi, classical fusion duet, sawaal jawaab call and response, intricate swara trade, "
            f"alternating virtuoso vocal solos, acoustic bansuri flute, veena, mridangam, tabla, lush acoustic strings, "
            f"expressive {vocal_tag}, dynamic crescendo, 84 bpm, clean broadcast master"
        )

    if any(k in eff_sub for k in ("carnatic", "raga", "narumugaye", "sangam")):
        return (
            f"carnatic classical fusion, nattaikurinji raga, acoustic bansuri flute, veena, mridangam, "
            f"ghatam, lush acoustic strings orchestra, soulful romantic classical duet, expressive {vocal_tag}, "
            f"pure acoustic warmth, 78 bpm, clean broadcast master"
        )

    if any(k in eff_sub for k in ("retro", "golden", "60s", "70s", "80s", "90s", "vintage")):
        if any(k in eff_sub for k in ("60s", "70s")):
            return f"1970s vintage golden melody, live acoustic orchestra, harmonium, acoustic sitar, tabla, expressive romantic duet, {vocal_tag}, warm analog tape saturation, 82 bpm, broadcast master"
        elif "80s" in eff_sub:
            return f"1980s melodic retro, melodic bass guitar, acoustic western flute, nylon guitar counterpoint, lush strings section, nostalgic analog warmth, {vocal_tag}, 85 bpm, clean broadcast master"
        return f"1990s lush ambient classical fusion, acoustic bansuri flute, lush string orchestra, world percussion, expressive romantic duet, soulful {vocal_tag}, 80 bpm, 48khz broadcast master"

    is_west = any(k in str(culture).lower() for k in ("western", "french", "spanish", "american", "british", "nordic", "global"))
    if any(k in eff_sub for k in ("romantic", "romance", "ballad", "love")):
        if is_west:
            return f"catchy hummable romantic pop ballad, memorable earworm hook, acoustic guitar, grand piano, lush strings, warm analog bass, {vocal_tag}, {tempo_bpm} bpm, radio broadcast mix"
        return f"catchy hummable romantic ballad, heartfelt {culture}, acoustic guitar, bansuri flute, soft strings, lush chords, memorable earworm hook, soulful, {vocal_tag}, {tempo_bpm} bpm, radio broadcast mix"

    if any(k in eff_sub for k in ("soul", "devotion", "spiritual")):
        if is_west:
            return f"soulful acoustic melody, grand piano, warm acoustic cello, memorable peaceful hook, serene emotional warmth, {vocal_tag}, {tempo_bpm} bpm, broadcast master"
        return f"soulful hummable acoustic melody, {culture}, meditative bansuri, resonant acoustic cello, heartfelt devotion, memorable peaceful hook, serene emotional warmth, {vocal_tag}, {tempo_bpm} bpm, broadcast master"

    if any(k in eff_sub for k in ("happy", "celebrat", "joy", "cheerful")):
        return f"catchy hummable celebration, {culture}, bright acoustic strumming, joyous rhythm, memorable sing-along hook, cheerful brass flourishes, vibrant {vocal_tag}, {tempo_bpm} bpm, broadcast mix"

    if any(k in eff_sub for k in ("mass", "dappu", "teenmaar")):
        m_tag = "energetic hero male vocals, punchy chest resonance" if gender == "male" else vocal_tag
        return f"catchy hummable mass commercial dance, heavy thumping dappu drums, fast teenmaar rhythm, {culture}, energetic brass trumpets, whistle drops, explosive earworm hook couplets, {m_tag}, 138 bpm, thumping bass downbeats, clean punchy 48khz broadcast master"

    if any(k in eff_sub for k in ("party", "club", "dance", "beat")):
        return f"infectious catchy party dance, {culture}, groovy bassline, infectious drum groove, memorable earworm hook, club rhythm, {vocal_tag}, 124 bpm, high energy broadcast master"

    cult_str = f"{culture} " if (culture and str(culture).lower() != "none") else ""
    clean_sub = eff_sub.replace("music/", "").replace("_", " ")
    return f"catchy hummable {cult_str}{clean_sub}, memorable earworm melody, acoustic instruments, melodic harmonies, {vocal_tag}, {tempo_bpm} bpm, clean 48khz broadcast master"


def _build_female_wardrobe_directive(fem: Any, setting: str, costume_hint: str | None = None, is_va: bool = False) -> str:
    """Generate dynamic, context-driven female wardrobe instructions without hardcoded lehengas."""
    if is_va:
        return (
            "  * VIRTUAL ARTIST DYNAMIC WARDROBE (GEMINI AUTONOMOUS DERIVATION - ZERO HARDCODING):\n"
            "    - Gemini MUST autonomously derive the entire clothing, outfit, and accessories dynamically based on the exact background context and setting.\n"
            "    - ZERO HARDCODING: Do not hardcode fixed colors, fixed palettes, or generic garment templates. Visual ambiance dictates the attire.\n"
            "    - FULLY COVERED & STRICT MODESTY (RULE 12 COMPLIANT ACROSS ALL MODELS): Must be completely covered: high closed boat neckline or mandarin collar, full closed torso and midriff coverage with continuous fabric (zero bare midriff, zero exposed stomach, zero bare belly), and explicit tailored sleeves (fitted 3/4 length sleeves or long tailored sleeves). Strictly zero cleavage, zero plunging necklines, zero crop tops, zero sheer reveals.\n"
            "    - ELEGANT, COLORFUL & DECORATIVE: Outfits must be breathtakingly beautiful, vibrant, and colorful in rich saturated jewel tones or radiant vivid pastels with intricate embroidery, delicate accents, or tasteful designer detailing that pop against the background.\n"
            "    - SCRIPT & PROMPT PERSISTENCE: Record this chosen outfit in 'characters[0].outfit_description' AND include it across EVERY scene.\n"
        )
    hint_line = f"  * USER COSTUME HINT: '{costume_hint}'. Gemini MUST honor this hint and style it in {fem.palette} with elegant tailoring.\n" if costume_hint else ""
    return (
        f"{hint_line}"
        f"  * AUTONOMOUS CONTEXT-DRIVEN WARDROBE DERIVATION (GEMINI DECIDES BASED ON STORY CONTEXT & THEME HINTS):\n"
        f"    - THEME HINTS PRIORITY: If the theme, idea, or setting ('{setting}') contains any specific outfit hints, fabrics, or colors (e.g. saree, gown, anarkali, dress, chiffon, silk), Gemini MUST honor and elaborate on those hints.\n"
        f"    - STORY-MATCHED SELECTION: If no specific outfit is hinted, Gemini MUST autonomously design an authentic, breathtakingly beautiful, vibrant, and colorful outfit suited specifically to the narrative beats, song mood, climate, and setting.\n"
        f"    - ELEGANT & ROMANTIC (NEVER CHEAP, SEXY, OR REVEALING): Outfits can be deeply romantic, dreamy, and poetic matching romantic song themes (graceful drape, soft billowing fabric, jewel/pastel tones). STRICT ELEGANCE CONTRACT: Must look cinema-grade, regal, and high-end—NEVER cheap, NEVER sexy, and NEVER revealing. Modest high neckline, full midriff and torso coverage. Strictly zero cleavage, zero plunging necklines, zero bare midriff, zero sheer reveals.\n"
        f"    - NO GENERIC DEFAULT: NEVER default to a generic lehenga or half-saree. Autonomously choose the most fitting silhouette:\n"
        f"      * Pastoral Nature / Rain / Soulful Melody: Elegant flowing Handloom Chanderi, Organza, or Chiffon Saree with delicate floral border that billows gracefully in the breeze (or flowing nature dress). Strictly NO lehenga/blouse.\n"
        f"      * Soulful Romance / Ballad: Floor-length embroidered Anarkali gown, pastel chiffon saree, or elegant evening gown.\n"
        f"      * Temple / Classical Sabha / Heritage: Regal Kanchipuram or Pochampally silk saree with rich gold zari temple border.\n"
        f"      * Modern / Pop / Urban / Street / Cafe: Chic contemporary Indo-Western fusion, stylish dress, or smart-casual coordinates.\n"
        f"      * Festive Village / Jathara: Celebratory vibrant festive attire with colorful dupatta and mirror-work accents.\n"
        f"    - Colors & Fabric: Rich saturated jewel tones or radiant pastels in {fem.palette} featuring intricate artistic designs (fine gold/silver threadwork, delicate embroidery, floral motifs) that pop against the backdrop.\n"
        f"    - SCRIPT & PROMPT PERSISTENCE (ZERO OUTFIT DISTORTION): Record this chosen outfit in 'characters[0].outfit_description' AND include it in 'visual_prompt' across EVERY scene for zero outfit distortion.\n"
    )


def _build_male_wardrobe_directive(male: Any, setting: str, costume_hint: str | None = None, is_va: bool = False) -> str:
    """Generate dynamic, context-driven male wardrobe instructions."""
    if is_va:
        return (
            "  * VIRTUAL ARTIST DYNAMIC MALE WARDROBE (GEMINI AUTONOMOUS DERIVATION - ZERO HARDCODING):\n"
            "    - Gemini MUST autonomously derive clothing and accessories based on setting: strikingly handsome in context-matched tailored attire (tailored shirt or structured blazer, tailored trousers, leather footwear) with precision chronograph watch strapped securely to left wrist. Modest gentleman styling (zero bare chest, zero nudity).\n"
        )
    hint_line = f"  * USER COSTUME HINT: '{costume_hint}'. Gemini MUST honor this hint and style it in {male.palette}.\n" if costume_hint else ""
    s_low = str(setting or "").lower()
    is_trad = any(k in s_low for k in ("jathara", "temple", "festiv", "dussehra", "diwali", "sankranti", "classical", "carnatic", "puja", "bonalu"))
    trad_hint = (
        f"  * Traditional / Festive Setting: Rich festive silk or fine-cotton kurta in {male.palette} with gold zari brocade embroidery, paired with a traditional cream/gold silk dhoti (panche) with golden zari border or tailored churidar, draped angavastram, and precision chronograph watch strapped securely to left wrist.\n"
        if is_trad else
        f"  * Context-Matching & Attractive Tailored Attire: Strikingly handsome, stylish tailored attire in {male.palette} authentically suited to {setting} (tailored linen/cotton shirt, structured layer or blazer, tailored trousers, polished leather footwear), with precision chronograph watch strapped securely to left wrist.\n"
    )
    return (
        f"{hint_line}"
        f"  * AUTONOMOUS CONTEXT-DRIVEN MALE WARDROBE (GEMINI DECIDES BASED ON STORY CONTEXT & THEME HINTS):\n"
        f"    - If theme/setting mentions specific attire, Gemini honors it. Otherwise, Gemini autonomously selects the most fitting style:\n"
        f"{trad_hint}"
    )


def build_cast_and_visual_directives(
    slot: int, fem: Any, male: Any, culture: str, setting: str,
    gender: str = "duet", is_kids: bool = False, is_jugalbandi: bool = False,
    costume_hint: str | None = None, is_va: bool = False,
) -> Tuple[str, str]:
    """Generate prompt directives and negative prompt constraints for character staging."""
    eff_gender = (gender or "duet").lower()
    _BASE_NEG = "nudity, naked, cleavage, sexualized outfit, revealing clothes, low cut, exposed midriff, bare midriff, bare stomach, bare belly, crop top, provocative attire, translucent fabric, cheap clothes, sexy, tacky clothing, skimpy dress, watch on shirt, chest badge, misplaced jewelry, plastic doll skin, wax figure, distorted anatomy, disembodied hands, floating hands, phantom limbs, extra limbs, duplicate wrists, duplicate watches, head cropped, cut off head, cut off face, head touching top edge, no headroom, blank expression, deadpan face, emotionless, neutral stare"

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

    is_party_or_mass = any(k in str(setting).lower() for k in ("party", "mass", "club", "dance", "jathara", "festiv", "celebrat"))
    s_low = f"{setting or ''} {culture or ''}".lower()
    is_traditional_festive = any(k in s_low for k in (
        "dussera", "dussehra", "diwali", "deepavali", "sankranti", "pongal", "temple",
        "spiritual", "jathara", "bonalu", "navratri", "bathukamma", "pooja", "puja",
        "traditional", "ethnic", "folk", "carnival", "village festival", "ugadi", "onam",
        "carnatic", "raga", "narumugaye", "sangam", "classical",
    ))

    male_outfit_guide = _build_male_wardrobe_directive(male, setting, costume_hint, is_va=is_va)
    fem_outfit_guide = _build_female_wardrobe_directive(fem, setting, costume_hint, is_va=is_va)

    is_west_cult = any(k in str(culture).lower() for k in ("western", "french", "spanish", "american", "british", "nordic", "global"))
    ear_neck_desc = 'Traditional gold temple jhumkas and delicate gold mango necklace / kasu mala' if is_traditional_festive else ('Context-matched sparkling teardrop earrings and delicate pendant' if is_west_cult else 'Context-matched sparkling earrings/jhumkas and delicate pendant chain')

    if eff_gender == "male":
        if is_party_or_mass:
            solo_male_staging = (
                "- SOLO MALE CENTERSTAGE STAR: Sole singing star in sharp focus.\n"
                "- BACKGROUND PARTY / TROUPE CROWD: Background features lively party guests, friends, or troupe dancers "
                "in soft optical blur/bokeh celebrating and dancing to create an authentic energetic party atmosphere.\n"
                "- STRICT PROHIBITION: No prominent female co-lead, no romantic couple intimacy, no dating partner.\n"
            )
            neg_constraints = "female lead, female co-star, romantic couple, hand holding, romantic partner, girlfriend, dating couple, nudity, naked, bare chest, watch on shirt, chest badge, head cropped, cut off head, cut off face, head touching top edge, no headroom, blank expression, deadpan face, emotionless, neutral stare, robotic face, dull expression, glassy eyes"
        else:
            solo_male_staging = (
                "- STRICT NEGATIVE DIRECTIVE: SOLO MALE ONLY. The image MUST depict ONLY this male character alone in the landscape. "
                "STRICTLY FORBIDDEN: NO WOMEN, NO FEMALE CHARACTERS, NO COUPLE, NO DATING PARTNER.\n"
            )
            neg_constraints = "woman, female, girl, women, couple, hand holding, romantic partner, nudity, naked, bare chest, watch on shirt, chest badge, head cropped, cut off head, cut off face, head touching top edge, no headroom, blank expression, deadpan face, emotionless, neutral stare, robotic face, dull expression, glassy eyes"

        cast_dir = (
            f"SOLO MALE LEAD DIRECTIVE (SLOT #{slot} - STRICT MALE ONLY STAGING):\n"
            f"- MALE LEAD: '{male.name}', Age {male.age}, natural fit medium-athletic build, {male.skin} skin, "
            f"{male.face}, {male.hair}.\n"
            f"- CONTEXT-MATCHING ELEGANT & ATTRACTIVE MALE OUTFIT:\n"
            f"{male_outfit_guide}"
            f"  * WRIST-WORN WATCH: Premium chronograph watch strapped securely to his LEFT WRIST (never on chest/shirt).\n"
            f"  * SCRIPT & PROMPT CONTRACT: Record '{male.hair}' in 'characters[0].hair_and_facial_features' AND repeat his exact facial features ({male.face}), hairstyle and facial stubble ({male.hair}) across 'visual_prompt' in EVERY scene for 100% character face consistency.\n"
            f"  * STRICT MODESTY (ZERO NUDITY): Tasteful, fully covered handsome styling. Zero bare chest, zero nudity.\n"
            f"{solo_male_staging}"
        )
    elif eff_gender == "female":
        if is_party_or_mass:
            solo_fem_staging = (
                "- SOLO FEMALE CENTERSTAGE STAR: Sole singing star in sharp focus.\n"
                "- BACKGROUND PARTY / TROUPE CROWD: Background features stylish party guests, friends, or troupe dancers "
                "in soft optical blur/bokeh dancing, clapping, and celebrating to create an authentic energetic party ambiance.\n"
                "- STRICT PROHIBITION: No prominent male co-lead, no romantic couple intimacy, no dating partner.\n"
            )
            neg_constraints = f"male lead, male co-star, romantic couple, hand holding, romantic partner, boyfriend, dating couple, {_BASE_NEG}"
        else:
            solo_fem_staging = (
                "- STRICT NEGATIVE DIRECTIVE: SOLO FEMALE ONLY. The image MUST depict ONLY this female character alone in the landscape. "
                "STRICTLY FORBIDDEN: NO MEN, NO MALE CHARACTERS, NO COUPLE, NO BOYFRIEND.\n"
            )
            neg_constraints = f"man, male, boy, men, couple, hand holding, romantic partner, boyfriend, dating couple, {_BASE_NEG}"

        cast_dir = (
            f"SOLO FEMALE LEAD DIRECTIVE (SLOT #{slot} - STRICT FEMALE ONLY STAGING):\n"
            f"- FEMALE LEAD: '{fem.name}', Age {fem.age}, natural fit medium-slender graceful build, {fem.skin} skin, "
            f"{fem.face}, {fem.hair}.\n"
            f"- CONTEXT-MATCHING ATTRACTIVE DESIGNER DRESS (BEAUTIFUL, COLORFUL, ELEGANT WITH DESIGNS):\n"
            f"{fem_outfit_guide}"
            f"  * STRICT MODESTY (FAMILY-FRIENDLY - ZERO NUDITY / ZERO SEXUALIZATION): Tasteful, fully modest and elegant necklines (boat neck, modest round neck, mandarin, or modest sweetheart with full coverage), completely covered torso and midriff, non-revealing, graceful silhouette. STRICTLY PROHIBIT deep cleavage, plunging necklines, sheer/translucent reveals, bare midriffs, or suggestive cuts.\n"
            f"  * CURATED 4-ZONE ACCESSORIES (GEMINI AUTONOMOUS CONTEXTUAL SELECTION - MANDATORY IN SCRIPT & IMAGE PROMPTS):\n"
            f"    Gemini MUST autonomously decide and describe context-matched accessories across all 4 zones based on the background, weather, and culture of {setting}:\n"
            f"    - HAIR (Zone 1): {'Fresh fragrant white jasmine flowers (mallepoolu) braided into hair or subtle maang tikka' if is_traditional_festive else 'Context-matched blossoms or delicate pearl/gold barrette pins'}.\n"
            f"    - EARS & NECK (Zone 2): {ear_neck_desc} styled on a modest high neckline.\n"
            f"    - HANDS & WRISTS (Zone 3): {'Traditional glass bangles, delicate gold kada, and dainty rings' if is_traditional_festive else 'Graceful slim dress watch, delicate gold/silver bangles or chain bracelets, and dainty rings'}.\n"
            f"    - LEGS & ANKLES (Zone 4): Context-matched dainty ankle chain (anklet / payal) paired with setting-appropriate footwear (sandals, heels, or embellished juttis).\n"
            f"    - SCRIPT & PROMPT CONTRACT: Gemini MUST record these chosen accessories in 'characters[0].outfit_description' AND explicitly include them in 'visual_prompt' across EVERY scene so each image reflects her cute, charming, and stylish appearance.\n"
            f"{solo_fem_staging}"
        )
    else:
        staging_title = "VOCAL JUGALBANDI STAGING (SAWAAL-JAWAAB FACE-OFF)" if is_jugalbandi else f"COORDINATED COUPLE DIRECTIVE (SLOT #{slot} - DUET STAGING)"
        jugalbandi_notes = (
            f"- VOCAL JUGALBANDI FACE-OFF DIRECTIVE:\n"
            f"  * The two vocal masters '{fem.name}' and '{male.name}' engage in a virtuoso musical face-off (Sawaal-Jawaab).\n"
            f"  * Alternating camera framing: When one sings with expressive mudras/gestures, frame them in sharp 50mm focus while the other listens with appreciative nods (waah!). Frame them together for the grand unison climax.\n"
            if is_jugalbandi else ""
        )
        cast_dir = (
            f"{staging_title}:\n"
            f"- FEMALE LEAD: '{fem.name}', Age {fem.age}, natural fit medium-slender graceful slim build with defined waist and natural feminine curves (graceful SLIM build), {fem.skin} skin, {fem.face}, {fem.hair}.\n"
            f"{fem_outfit_guide}"
            f"  * STRICT MODESTY (FAMILY-FRIENDLY & ZERO NUDITY): Elegant modest high boat neckline, mandarin collar, or high round neck with full upper chest coverage. Strictly zero cleavage, zero plunging necklines, zero low V-necks, zero bare midriff.\n"
            f"  * CURATED 4-ZONE ACCESSORIES (GEMINI AUTONOMOUS CONTEXTUAL SELECTION - MANDATORY IN SCRIPT & IMAGE PROMPTS):\n"
            f"    Gemini MUST autonomously decide and describe context-matched accessories across all 4 zones based on the background, weather, and culture of {setting}:\n"
            f"    - HAIR (Zone 1): {'Fresh fragrant jasmine flowers (mallepoolu)' if is_traditional_festive else 'Context-matched blossoms or delicate pearl/gold barrette pins'}.\n"
            f"    - EARS & NECK (Zone 2 - MANDATORY NECK ACCESSORY): {ear_neck_desc} styled gracefully around her neck over the high neckline. Females ALWAYS wear neck accessories; NEVER omit the necklace or pendant chain in any scene prompt.\n"
            f"    - HANDS & WRISTS (Zone 3): {'Traditional glass bangles, delicate gold kada, and dainty rings' if is_traditional_festive else 'Graceful slim dress watch, delicate gold/silver bangles or chain bracelets, and dainty rings'}.\n"
            f"    - LEGS & ANKLES (Zone 4): Context-matched dainty ankle chain (anklet / payal) paired with setting-appropriate footwear (sandals, heels, or boots).\n"
            f"    - SCRIPT & PROMPT CONTRACT: Gemini MUST record these chosen accessories in 'characters[0].outfit_description' AND explicitly include ALL 4 ZONES (including the necklace around her neck) in 'visual_prompt' across EVERY scene so each image reflects her cute, charming, and stylish appearance.\n"
            f"- MALE LEAD: '{male.name}', Age {male.age}, natural fit medium-athletic frame (MEDIUM BUILT), {male.skin} skin, {male.face}, {male.hair}.\n"
            f"{male_outfit_guide}"
            f"- DIRECTORIAL FRAMING & ANTI-HALLUCINATION GUARD:\n"
            f"  * Both leads must be framed together naturally or solo. NEVER describe an off-screen partner's hands reaching into the frame.\n"
            f"  * Authentic romantic chemistry engaging with the background, zero stiff separated stances.\n"
            f"{jugalbandi_notes}"
        )
        neg_constraints = f"off-screen reaching, boxy tunic, baggy loungewear, shapeless clothing, low V-neck, plunging neckline, stiff posture, standing separated, tight headroom, top frame cut off, forehead cropped, hair touching top frame, {_BASE_NEG}"

    return cast_dir, neg_constraints
