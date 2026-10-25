"""Directorial Directives for Virtual Artist Performance Music Videos (Lara Aredo Style).

Directs Gemini to autonomously derive:
1. Setting-matched scenic backdrops (grass fields, mountains, valleys, deserts, landmarks)
   or live concert stages (lighting trusses, mic, live orchestra/band, cheering audience).
2. 1 to 2 authentic concert cutaway shots of orchestra members playing instruments.
3. Setting-matched elegant, modest outfits (Rule 12) with full 4-zone accessories.
4. Natural singer performance kinematics (subtle rhythm sway, guitar strumming, hair in wind,
   intimate facial expressions, head tilts) instead of dance jumps or static poses.
"""

from __future__ import annotations

from typing import Any, Optional


def build_virtual_artist_directives(
    gender: str = "female",
    artist_mode: str = "scenic",
    instrument: Optional[str] = None,
    has_orchestra: bool = False,
    scenic_archetype: Optional[str] = None,
    landmark: Optional[str] = None,
    culture: str = "Global",
    country: str = "USA",
    theme: str = "intimate acoustic performance",
) -> str:
    """Build authoritative Gemini prompt directive for Virtual Artist productions."""
    eff_gender = (gender or "female").lower()
    eff_mode = (artist_mode or "scenic").lower()
    inst_desc = instrument or "acoustic_guitar"

    # Instrument handling directive
    inst_instruction = (
        f"   - SIGNATURE INSTRUMENT STAGING ({inst_desc.upper()}):\n"
        f"     * The lead performer actively holds and plays a signature {inst_desc.replace('_', ' ')} (or sings into a chrome vintage stage microphone).\n"
        f"     * Left and right hands MUST be anatomically grounded: fingers fretting chords naturally, right hand strumming or fingerpicking resonant strings.\n"
        f"     * Never depict floating instruments, misplaced guitar bodies, or disembodied hands.\n"
    )

    if "concert" in eff_mode:
        setting_text = (
            "1. AUTONOMOUS CONCERT STAGE & ARENA DERIVATION (ELECTRIC STADIUM RIG):\n"
            "   - BRIGHT, VIBRANT & ELECTRIC ATMOSPHERE (MANDATORY):\n"
            "     * Stage MUST be brightly and dynamically lit with high-intensity follow-spots, piercing volumetric beam arrays (electric blue, vivid magenta, cyan, warm gold), moving head spots, and luminous LED backdrop walls.\n"
            "     * Brilliant key follow-spot on the performer ensures razor-sharp facial clarity and luminous skin tones—strictly prohibit dark, underexposed, or muddy concert framing.\n"
            "     * An electric arena atmosphere with cheering audience holding a vibrant sea of glowing neon lightsticks and smartphone torches.\n"
            "   - BACKING ORCHESTRA & ACCOMPANISTS (MANDATORY):\n"
            "     * Flanking the lead singer, depict a live backing ensemble (e.g. cellist, acoustic bassist, rhythm guitarist, keyboardist, or drummer).\n"
            "   - MANDATORY 6 DISTINCT PHYSICAL CAMERAS IN 'scenes' (EXACTLY ONE CHARACTER SHOT):\n"
            "     * Camera 1 (center_vocalist_front): Frontal medium shot of lead singer centerstage at vintage mic (THE ONLY CHARACTER SHOT).\n"
            "     * Camera 2 (active_instrument_macro): Virtuoso close-up macro on solo instrument (guitar fretboard/drum kit/strings).\n"
            "     * Camera 3 (backing_orchestra_ensemble): Live backing orchestra on stage platform (drummer, bassist, keys under trusses).\n"
            "     * Camera 4 (overall_stadium_vista): Grand wide/drone view of the entire stadium arena, roof trusses, and mammoth scale.\n"
            "     * Camera 5 (stadium_audience_crowd): Packed arena floor and cheering crowd waving glowing phone lights and lightsticks.\n"
            "     * Camera 6 (stage_lightshow_pyro): Spectacular concert stage visual spectacle, laser beam arrays, and pyro bursts.\n"
            "   - DIRECTORIAL BROADCAST TIMELINE ('broadcast_timeline'):\n"
            "     * Gemini MUST direct a realistic broadcast cut schedule (3.5s-5.0s per cut) synchronized to song sections.\n"
            "     * WHEN SINGER IS SINGING ('is_singing': true): Cut to Camera 1 for vocal delivery with LatentSync lipsync.\n"
            "     * WHEN ORCHESTRA / INSTRUMENTS PLAYING ('is_singing': false):\n"
            "       - MULTI-ANGLE CUTS: Dynamically cut across Camera 2 (Instrument), Camera 3 (Orchestra), Camera 4 (Overall Stadium), Camera 5 (Audience), or Camera 6 (Lightshow) with smooth camera glides.\n"
            "       - ZERO LIPSYNC: AI motion clips look 100% natural and cinema-grade during orchestra breaks—zero lipsync required.\n"
        )
    else:  # scenic mode
        landmark_clause = f", optionally incorporating the iconic architecture of {landmark.replace('_', ' ').title()}" if landmark else ""
        setting_text = (
            "1. AUTONOMOUS SCENIC BACKDROP DERIVATION (NO HARDCODED TEMPLATES):\n"
            f"   - Gemini must autonomously derive breathtaking natural landscapes matching the lyrical mood: lush undulating wildflower meadows, alpine mountain peaks, pastoral sunlit valleys, sweeping desert dunes at golden hour, or rocky coastal cliffs{landmark_clause}.\n"
            "   - Maintain atmospheric realism: crisp natural daylight (5400K-5600K) or warm sunset rim light, genuine ground flora, and deep cinematic depth of field.\n"
            "   - Avoid monotonous repetitions: rotate camera perspective and focal length across distinct scenic angles of the landscape hub.\n"
            "   - DIRECTORIAL BROADCAST TIMELINE ('broadcast_timeline'): Sequence 3.5s to 5.0s cuts across scenic perspectives, tagging 'is_singing' for vocal segments.\n"
        )

    is_west_va = any(k in str(culture).lower() for k in ("western", "french", "spanish", "american", "british", "nordic", "global"))
    cult_decor = (
        "delicate sequin accents, fine filigree embroidery, or tasteful designer tailoring"
        if is_west_va else "delicate embroidery, fine gold/silver zari threadwork, or tasteful cultural patterns"
    )
    cult_fem_costume = (
        "Female Lead: Floor-length designer concert gown or tailored performance attire in rich jewel tones (sapphire blue, emerald green, ruby crimson) with high modest boat neckline or mandarin collar, fitted long sleeves, continuous covered torso, and subtle elegant accents."
        if is_west_va else "Female Lead: Breathtaking designer Anarkali or traditional gown in rich jewel tones with high modest neckline, continuous covered torso, and fine zari embroidery."
    )

    outfit_text = (
        "2. AUTONOMOUS CONTEXT-MATCHED WARDROBE DERIVATION (GEMINI DYNAMIC DERIVATION - ZERO HARDCODING):\n"
        "   - Gemini MUST autonomously derive the clothing, outfit, and accessories dynamically based on the exact background context and setting (never hardcode fixed colors or generic garments).\n"
        "   - FULLY COVERED & STRICT MODESTY (RULE 12 COMPLIANT ACROSS ALL MODELS):\n"
        "     * Attire MUST ALWAYS be fully covered and broadcast-modest: high closed boat neckline or mandarin collar, full closed torso and midriff coverage with continuous fabric (zero bare midriff, zero exposed stomach, zero bare belly), and explicit tailored sleeves (fitted 3/4 length sleeves or long tailored sleeves).\n"
        "     * Strictly PROHIBIT all revealing cuts, deep cleavage, plunging necklines, bare midriffs, crop tops, lehenga cholis with exposed stomachs, or translucent fabrics across all models.\n"
        "   - ELEGANT, COLORFUL & DECORATIVE:\n"
        f"     * Outfits must be breathtakingly beautiful, vibrant, and colorful in rich saturated jewel tones or radiant vivid pastels (e.g. royal sapphire, ruby crimson, emerald green, warm amber, vivid peach, sunflower yellow, lavender) featuring intricate artistic designs—{cult_decor} that pop against the background.\n"
        f"     * {cult_fem_costume}\n"
        "   - CURATED 4-ZONE ACCESSORIES (CONTEXT-MATCHED):\n"
        f"     * Female Lead: Curated 4-zone accessories coordinated with the derived dress: (1) Hair: delicate pearl/gold barrette pins or fresh flowers; (2) Neck & Ears: sparkling teardrop earrings and fine matching pendant; (3) Hands & Wrists: slim luxury dress watch on left wrist and subtle bangles/rings; (4) Legs & Ankles: delicate silver/gold ankle chain ({'dainty anklet' if is_west_va else 'payal'}).\n"
        "     * Male Lead: Strikingly handsome in context-matched tailored attire (crisp linen/cotton button-down or stylish structured blazer, tailored trousers, leather footwear) with precision chronograph watch strapped securely to his left wrist.\n"
        "   - MANDATORY CONCERT WARDROBE & SETTING CONTINUITY (CONCERT MODE):\n"
        "     * In CONCERT mode, the performance is a single continuous live concert. The artist MUST wear the EXACT SAME STAGE OUTFIT, HAIRSTYLE, AND ACCESSORIES across all shots.\n"
        "     * Gemini establishes this dynamic, fully covered, colorful, elegant stage outfit with explicit sleeve length and high neckline in Scene 1 and character profile, and repeats it 100% IDENTICALLY VERBATIM across all subsequent scenes.\n"
        "     * Strictly PROHIBIT outfit changes, different sleeves, midriff exposure, head veils/chunnis/dupattas over the head, bridal transformations, or switching to interior rooms. Every scene remains on the live stage with overhead lighting trusses and microphone.\n"
        "   - PHOTOREALISTIC HUMAN SKIN TEXTURE (STRICT PROHIBITION OF PLASTIC/WAX BUZZWORDS):\n"
        "     * Always specify 'authentic human skin texture with natural fine visible pores, subtle imperfections, and lifelike subsurface scattering'.\n"
        "     * NEVER use AI buzzwords like 'glowing radiant skin', 'porcelain skin', 'flawless airbrushed skin', or 'glowing peach-fair skin' which trigger waxy doll-like rendering.\n"
    )

    kinematics_text = (
        "3. NATURAL SINGER PERFORMANCE KINEMATICS & PITCH-INFLECTED HAND GESTURES (LARA AREDO STYLE - NOT DANCE):\n"
        "   - The virtual artist is an expressive musical performer, NOT a static statue or two-handed mic clutcher.\n"
        "   - PITCH-INFLECTED VOCAL HAND GESTURES (MANDATORY IN SINGING SCENES):\n"
        "     * High-Pitch Notes & Climax Passages: Singer's free hand gracefully lifts upward and outward with open palm and elegant ascending fingers, visually conveying soaring pitch altitude, breath expansion, and vocal lift.\n"
        "     * Low-Pitch & Tender Intimate Phrases: The hand glides gently downward, floating softly or resting tenderly near the chest/heart with relaxed fingers.\n"
        "     * Melodic Phrasing & Rhythmic Cadence: Subtle wrist turns, expressive finger curls, and rhythmic hand accents matching lyrical ornamentations (gamakas/melisma).\n"
        "     * Strictly PROHIBIT rigid two-handed clutching of the microphone, frozen hands, or stiff mannequin poses.\n"
        "   - Natural Performance Kinematics: Gentle rhythmic swaying to tempo, subtle head tilts, hair fluttering softly, and expressive singing eyes.\n"
        "   - Strictly PROHIBIT vigorous dance steps, acrobatic jumps, or stiff static passport-photo mannequin poses.\n"
    )

    return (
        "VIRTUAL ARTIST DIRECTORIAL SPECIFICATION (LARA AREDO STYLE):\n"
        f"{setting_text}"
        f"{outfit_text}"
        f"{inst_instruction}"
        f"{kinematics_text}"
        "4. CAMERA MOTION & FRAMING:\n"
        "   - Fluid cinematic camera movements: gentle crane push-in ('dollyin+tilt-up'), slow arc orbit ('orbit-left'), or tranquil tracking glide ('pan-right').\n"
        "   - Maintain 20% broadcast headroom above performer's head for rule-of-thirds composition.\n\n"
    )


def get_offline_virtual_artist_scenes(
    country: str,
    culture: str,
    character_desc: str,
    gender: str = "female",
    artist_mode: str = "scenic",
    instrument: str = "acoustic_guitar",
    num_scenes: int = 4,
) -> list[dict[str, Any]]:
    """Return deterministic, high-CTR virtual artist scenes for offline mock mode ($0.00 spend, Rule 8)."""
    eff_gender = (gender or "female").lower()
    is_concert = "concert" in (artist_mode or "").lower()
    inst = instrument or "acoustic_guitar"

    if is_concert:
        catalog = [
            {
                "camera_id": "center_vocalist_front",
                "shot_type": "medium_shot",
                "pose": f"Live concert performance centerstage, singing into vintage stand mic with warm overhead stage spotlights",
                "prompt_ext": f"Performing live under warm overhead spotlights and atmospheric stage haze, singing with heartfelt expression into vintage stand mic, backing orchestra in soft optical bokeh.",
                "motion": f"Expressive vocal delivery: free hand gracefully lifting on high soaring notes, subtle rhythm sway at vintage stand mic",
            },
            {
                "camera_id": "active_instrument_macro",
                "shot_type": "close_up",
                "pose": f"Solo instrument cutaway: Macro focus on {inst.replace('_', ' ')} being played with virtuoso skill",
                "prompt_ext": f"Authentic concert broadcast cutaway. Focused close-up of {inst.replace('_', ' ')} on stage. Musician hands gliding with precision, warm stage lights glinting on instrument body.",
                "motion": f"Virtuoso hand performance on {inst.replace('_', ' ')}, fingers moving rhythmically in sync with the musical solo",
            },
            {
                "camera_id": "backing_orchestra_ensemble",
                "shot_type": "medium_wide",
                "pose": "Live backing band and orchestra performing dynamically on stage platform under overhead trusses",
                "prompt_ext": "Live concert backing orchestra on stage: drummer striking rhythmically, bassist grooving, rhythm players under dramatic blue and magenta spotlights.",
                "motion": "Backing band in energetic concert motion: drummer hitting cymbals, bassist swaying to the driving rhythm groove",
            },
            {
                "camera_id": "overall_stadium_vista",
                "shot_type": "wide_cinematic",
                "pose": "Grand high-altitude stadium arena vista capturing the immense architecture, glowing field, and roof trusses",
                "prompt_ext": "Monumental stadium arena vista from elevated perspective, massive illuminated arena bowl, glowing stage at center, sweeping follow-spots cutting through night sky.",
                "motion": "Slow sweeping panoramic glide high above the stadium arena revealing mammoth concert scale",
            },
            {
                "camera_id": "stadium_audience_crowd",
                "shot_type": "wide_cinematic",
                "pose": "Dense sea of thousands of cheering fans in arena floor waving synchronized phone torches and glowing neon lightsticks",
                "prompt_ext": "Packed stadium audience canopy from elevated angle, ecstatic fans cheering, jumping, and waving glowing amber and cyan lightsticks towards the brightly lit stage.",
                "motion": "Sweeping slow drone glide forward over the cheering sea of fans towards the illuminated concert stage",
            },
            {
                "camera_id": "stage_lightshow_pyro",
                "shot_type": "wide_cinematic",
                "pose": "Spectacular concert stage lighting show with volumetric laser grids, moving head beams, and dramatic pyrotechnic flare bursts",
                "prompt_ext": "Electrified concert stage visual spectacle: crisscrossing volumetric cyan and magenta laser arrays, high-intensity moving spotlights, and explosive golden stage pyro bursts.",
                "motion": "Dynamic camera push towards stage as volumetric lasers sweep overhead and golden pyrotechnic fountains flare dramatically",
            },
        ]
    else:  # scenic mode
        catalog = [
            {
                "camera_id": "center_vocalist_front",
                "shot_type": "medium_shot",
                "pose": f"Acoustic performance in lush wildflower meadow, strumming {inst.replace('_', ' ')}",
                "prompt_ext": f"Seated comfortably on a rustic wooden bench in a sunlit wildflower meadow, strumming an acoustic {inst.replace('_', ' ')} with gentle smile, breeze fluttering dress, distant alpine peaks in soft focus.",
                "motion": f"Natural singer performance: gentle rhythm sway, fingers plucking {inst.replace('_', ' ')}, hair waving in breeze",
            },
            {
                "camera_id": "stage_profile_45",
                "shot_type": "three_quarter",
                "pose": f"Walking leisurely along scenic trail with {inst.replace('_', ' ')} strapped, looking at vistas",
                "prompt_ext": f"Strolling slowly along a scenic gravel path overlooking a sunlit valley, acoustic {inst.replace('_', ' ')} slung over shoulder, relaxed genuine smile, elegant modest attire fluttering softly.",
                "motion": "Leisurely walking cadence with subtle steadycam tracking, smiling towards the landscape",
            },
            {
                "camera_id": "vocal_close_up",
                "shot_type": "close_up",
                "pose": "Emotive close-up singing portrait, natural sunlight and wind in hair",
                "prompt_ext": "Intimate close-up portrait of the lead singer, genuine warm smile, natural skin texture, hair strands drifting in the mountain breeze, expressive eyes reflecting golden sunlight.",
                "motion": "Subtle breathing, eyes engaging camera, natural mouth articulation singing the melody",
            },
            {
                "camera_id": "high_crane_arena_vista",
                "shot_type": "wide_cinematic",
                "pose": "Atmospheric wide scenic landscape vista with lead artist performing in nature",
                "prompt_ext": f"Sweeping panoramic 4K vista of lush rolling hills and mountain valley, lead singer performing acoustic melody with {inst.replace('_', ' ')}, natural daylight 5500K illumination.",
                "motion": "Tranquil camera glide forward across meadow flowers towards the performing artist",
            },
        ]

    scenes = []
    motions = ["dollyin+tilt-up", "pan-right", "dollyin", "orbit-left", "pedestal-up", "crane-down"]
    for i in range(max(1, num_scenes)):
        item = catalog[i % len(catalog)]
        m = motions[i % len(motions)]
        scenes.append({
            "scene_index": i + 1,
            "camera_id": item["camera_id"],
            "camera_shot_type": item["shot_type"],
            "character_pose": item["pose"],
            "camera_motion": m,
            "local_drone": {"movement": m, "start_pan": "center", "start_zoom": "normal", "start_tilt": "center", "rationale": "Singer performance kinematics"},
            "location_hub": f"Stage Perspective {i + 1} ({country})" if is_concert else f"Scenic Hub {i + 1} ({country})",
            "render_mode": "motion" if "close" in item["shot_type"] or "medium" in item["shot_type"] else "still",
            "motion_prompts": {
                "wan": f"Virtual artist natural performance: {item['motion']}, pitch-inflected hand gestures, natural hands, strictly two legs",
                "kling": f"Cinematic music video performance: {item['motion']}, expressive vocal hands, natural hair dynamics, photorealistic eyes and mouth",
            },
            "visual_prompt": f"4K photorealistic cinematic virtual artist music video in {country}. {character_desc}. {item['prompt_ext']}",
        })
    return scenes


def get_offline_virtual_artist_broadcast_timeline(
    duration_seconds: float = 60.0,
    instrument: str = "acoustic_guitar",
) -> list[dict[str, Any]]:
    """Return deterministic multi-camera broadcast switching cuts (3.5s - 5.0s cuts, Rule 8 $0.00 spend)."""
    inst = instrument or "acoustic_guitar"
    cuts_pattern = [
        {"camera_id": "overall_stadium_vista", "is_singing": False, "inst": inst, "drone": "crane-down"},
        {"camera_id": "stadium_audience_crowd", "is_singing": False, "inst": "none", "drone": "slow_push"},
        {"camera_id": "center_vocalist_front", "is_singing": True, "inst": "vocals", "drone": "steady"},
        {"camera_id": "backing_orchestra_ensemble", "is_singing": False, "inst": inst, "drone": "orbit-left"},
        {"camera_id": "center_vocalist_front", "is_singing": True, "inst": "vocals", "drone": "slow_push"},
        {"camera_id": "active_instrument_macro", "is_singing": False, "inst": inst, "drone": "pan-right"},
        {"camera_id": "center_vocalist_front", "is_singing": True, "inst": "vocals", "drone": "dollyin+tilt-up"},
        {"camera_id": "stage_lightshow_pyro", "is_singing": False, "inst": "none", "drone": "steady"},
        {"camera_id": "stadium_audience_crowd", "is_singing": False, "inst": "none", "drone": "pan-left"},
        {"camera_id": "overall_stadium_vista", "is_singing": False, "inst": inst, "drone": "crane-down"},
    ]
    # Distribute duration evenly so each cut is strictly between 3.5s and 5.0s
    target_cut_dur = 4.2
    n_cuts = max(1, int(round(duration_seconds / target_cut_dur)))
    cut_dur = round(duration_seconds / n_cuts, 2)
    cuts = []
    t_curr = 0.0
    for i in range(n_cuts):
        pat = cuts_pattern[i % len(cuts_pattern)]
        end_t = round(duration_seconds, 2) if i == n_cuts - 1 else round(t_curr + cut_dur, 2)
        dur = round(end_t - t_curr, 2)
        cuts.append({
            "cut_index": i + 1,
            "start_time": round(t_curr, 2),
            "end_time": end_t,
            "duration_seconds": dur,
            "camera_id": pat["camera_id"],
            "is_singing": pat["is_singing"],
            "active_instrument": pat["inst"],
            "lyrics_line": "Catchy melodic Telugu phrase" if pat["is_singing"] else "",
            "local_drone_motion": pat["drone"],
            "transition": "cut" if (i + 1) % 2 == 1 else "crossfade",
        })
        t_curr = end_t
    return cuts


__all__ = [
    "build_virtual_artist_directives",
    "get_offline_virtual_artist_scenes",
    "get_offline_virtual_artist_broadcast_timeline",
]

