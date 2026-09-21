"""Dance Model Matrix and Dance Motion LoRA Catalog."""

from typing import Any

DANCE_MODEL_MATRIX: dict[str, dict[str, Any]] = {
    "indian_classical": {
        "dance_name": "Indian Classical (Bharatanatyam, Kuchipudi, Kathak, Odissi)",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_lora": {
            "path": "loras/indian_classical_attire_v1.safetensors",
            "scale": 0.85,
            "trigger": "classical indian dance costume, pleated silk fan, temple border",
        },
        "jewelry_lora": {
            "path": "loras/temple_jewelry_gold_v1.safetensors",
            "scale": 0.80,
            "trigger": "traditional gold temple jewelry, waist belt vaddanam, maang tikka",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "Carnatic / Classical rhythmic beat with mridangam, nattuvangam, and violin",
        "prompt_decorations": (
            "graceful classical Indian dance posture (Araimandi), mudra hand gestures with red Alta dye, "
            "brass ghungroo ankle bells, elaborate pleated Kanchipuram silk costume, jasmine flower veni in hair braid"
        ),
        "reasoning": "Fal.ai MimicMotion provides sub-millimeter finger mudra tracking and footwork audio-sync; FLUX Dev renders intricate temple jewelry and pleated silk with zero artifacting.",
    },
    "indian_folk_mass": {
        "dance_name": "Indian Commercial Mass & Folk (Tollywood Mass, Bollywood, Bhangra, Garba)",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_lora": {
            "path": "loras/indian_festive_mass_v1.safetensors",
            "scale": 0.85,
            "trigger": "colorful festive dhoti-lungi with zari border, mirror-work festive vest",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "130+ BPM high-bass Indian commercial mass dhol and teenmaar beat drops",
        "prompt_decorations": (
            "high-energy synchronized Indian mass dance hook step, flying festive colors, dynamic crowd dancers, "
            "vibrant silk lungi swirl or flared kurta, cinematic festival atmosphere, stadium lighting"
        ),
        "reasoning": "Selected MimicMotion for fast audio-driven hook step pose transfer; paired with Suno 130+ BPM high-energy rhythm track.",
    },
    "contemporary": {
        "dance_name": "Contemporary / Hip-Hop / Pop",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "western_modern",
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "120 BPM upbeat commercial pop/electronic rhythm",
        "prompt_decorations": "modern street dance choreography, fluid contemporary motion, urban studio lighting",
        "reasoning": "Smooth pose transfer matched to rhythmic musical cadence.",
    },
    "italian_tarantella": {
        "dance_name": "Italian Tarantella & Pizzica Folk Dance",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "italian_tarantella_folk",
        "costume_lora": {
            "path": "loras/italian_tarantella_costume_v1.safetensors",
            "scale": 0.85,
            "trigger": "traditional italian folk dress, laced bodice, embroidered apron, tambourine",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "Fast 6/8 Italian Tarantella folk rhythm with tambourine, accordion, mandolin, and acoustic guitar",
        "prompt_decorations": "lively Italian Tarantella spinning steps, waving ribboned tambourine, flared pleated folk skirt, rustic Southern Italian cobblestone piazza",
        "reasoning": "MimicMotion captures rapid 6/8 tambourine-skipping footwork synchronized to Southern Italian folk accordions.",
    },
    "mexican_folklorico": {
        "dance_name": "Mexican Ballet Folklórico & Jarabe Tapatío",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "mexican_jalisco_charro",
        "costume_lora": {
            "path": "loras/mexican_folklore_jalisco_v1.safetensors",
            "scale": 0.85,
            "trigger": "jalisco ribbon dress, embroidered charro suit, wide sombrero",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "Upbeat Mexican Mariachi Folklórico rhythm with energetic trumpets, violins, vihuela, and rhythmic zapateado heel-stomps",
        "prompt_decorations": "grand circular double-skirt waves (faldeo) displaying rainbow satin ribbons, rhythmic zapateado footwork, festive Mexican colonial plaza",
        "reasoning": "Selected MimicMotion for rhythmic zapateado foot-stomping and wide rainbow skirt twirling dynamics.",
    },
    "american_country_line": {
        "dance_name": "American Country Line Dance & Western Swing",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "american_western_country",
        "costume_lora": {
            "path": "loras/american_western_country_v1.safetensors",
            "scale": 0.85,
            "trigger": "cowboy boots, denim jeans, western snap shirt, stetson cowboy hat",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "Upbeat American Country-Western rhythm with twangy acoustic guitar, hoedown fiddle, and rhythmic heel-and-toe stomps",
        "prompt_decorations": "synchronized country line dance steps, grapevine turns and heel scuffs, wooden rustic dance hall, warm western saloon lighting",
        "reasoning": "Selected MimicMotion for synchronized boot-scuffing line dance choreography and country fiddle hoedown rhythm.",
    },
    "chinese_classical_ribbon": {
        "dance_name": "Chinese Classical Water Sleeves & Silk Ribbon Dance",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "chinese_hanfu_water_sleeves",
        "costume_lora": {
            "path": "loras/chinese_classical_hanfu_dance_v1.safetensors",
            "scale": 0.85,
            "trigger": "flowing water sleeves shuixiu, celestial hanfu silk robes, long silk ribbons",
        },
        "music_engine": "suno-v3.5-vocal-pro",
        "music_style": "Traditional Chinese Sizhu silk and bamboo melody with Guzheng zither, Erhu fiddle, Dizi flute, and rhythmic bronze gongs",
        "prompt_decorations": "ethereal Chinese classical dance posture, flowing long white water sleeves (shuixiu) undulating like ocean waves, floating silk ribbons, imperial palace garden",
        "reasoning": "FLUX Dev and MimicMotion render flowing silk water sleeves (shuixiu) and celestial ribbon trajectories with zero geometric clipping.",
    },
    "telugu_monsoon_rain_dance": {
        "dance_name": "Telugu Village Monsoon Rain Folk Dance (Janapada Geyam)",
        "motion_model": "fal-mimic-motion",
        "motion_provider": "Fal.ai",
        "visual_model": "flux-1-dev",
        "costume_style": "telugu_rain_folk_saree",
        "costume_lora": {
            "path": "loras/telugu_rain_folk_v1.safetensors",
            "scale": 0.85,
            "trigger": "wet cotton saree tucked at waist, dark green blouse, rain droplets on skin",
        },
        "music_engine": "suno-v4-vocal-pro",
        "music_style": "128 BPM rustic Telugu village monsoon folk song with heavy dholak, dappu, matka beats, village chorus clapping, and thunder foley",
        "prompt_decorations": "energetic barefoot village rain dance, water splashing from wet grass and muddy puddles, synchronized chorus line swaying, lush green paddy fields with white egrets, monsoon rainfall dynamics",
        "reasoning": "FLUX Dev with MimicMotion replicates authentic Telugu rain folk steps, multi-dancer footwork in puddles, and fluid wet-cloth cling physics.",
    },
}


def lookup_dance_stack(dance_type: str) -> dict[str, Any] | None:
    """Retrieve dance motion models, LoRAs, and prompt decorations for a dance style."""
    d_key = dance_type.lower().replace("-", "_")
    if "rain" in d_key or "monsoon" in d_key or "vanammo" in d_key:
        return DANCE_MODEL_MATRIX["telugu_monsoon_rain_dance"]
    if "ital" in d_key or "tarantella" in d_key or "pizzica" in d_key:
        return DANCE_MODEL_MATRIX["italian_tarantella"]
    if "mexic" in d_key or "folklore" in d_key or "jarabe" in d_key or "zapateado" in d_key:
        return DANCE_MODEL_MATRIX["mexican_folklorico"]
    if "americ" in d_key or "country" in d_key or "line_dance" in d_key or "western_swing" in d_key:
        return DANCE_MODEL_MATRIX["american_country_line"]
    if "chin" in d_key or "ribbon" in d_key or "water_sleeve" in d_key or "hanfu_dance" in d_key:
        return DANCE_MODEL_MATRIX["chinese_classical_ribbon"]
    if "classic" in d_key or "bharat" in d_key or "kuchipudi" in d_key or "kathak" in d_key:
        return DANCE_MODEL_MATRIX["indian_classical"]
    if "mass" in d_key or "folk" in d_key or "tollywood" in d_key or "bollywood" in d_key or "bhangra" in d_key or "garba" in d_key:
        return DANCE_MODEL_MATRIX["indian_folk_mass"]
    if "contemporary" in d_key or "hip_hop" in d_key or "pop" in d_key:
        return DANCE_MODEL_MATRIX["contemporary"]
    return None


__all__ = ["DANCE_MODEL_MATRIX", "lookup_dance_stack"]
