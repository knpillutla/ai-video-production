"""South Asian regional cultural models: Telugu, Tamil, Malayalam, and Kannada."""

from typing import Any

SOUTH_ASIAN_REGIONAL_MODELS: dict[str, dict[str, Any]] = {
    "indian_telugu": {
        "culture_name": "Telugu (Andhra Pradesh & Telangana)",
        "primary_ethnicity": "South Asian / Telugu",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Gemini 1.5 Pro for nuanced Telugu lyrical cadence, prasa/chandas rhyming, and Tollywood storytelling.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1", "indian-lighting-warm-v1"],
            "prompt_anchors": "South Asian Telugu heritage, warm radiant skin tones, authentic Indian facial structure, dark brown expressive eyes, thick dark hair",
            "reasoning": "FLUX.1 captures authentic Telugu cultural identity with cinematic depth and realistic skin textures.",
        },
        "voice_tts": {
            "te": {"male": "te-IN-MohanNeural", "female": "te-IN-ShrutiNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Telugu neural voices with authentic regional intonation for Telugu.",
        },
        "audio_soundtrack": {
            "default": "Telugu melody with Carnatic acoustic flute, veena, and subtle mridangam rhythm",
            "comedy": "Playful Tollywood comedic score with mridangam and konnakol accents",
            "drama": "Emotive Telugu melodic strings, acoustic sitar, and bansuri flute",
            "dance": "High-energy Tollywood mass teenmaar rhythm with nadaswaram and dholak",
        },
    },
    "indian_tamil": {
        "culture_name": "Tamil (Tamil Nadu & Diaspora)",
        "primary_ethnicity": "South Asian / Tamil",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Gemini 1.5 Pro for Tamil Sangam-rooted metaphors, Kollywood musical flow, and authentic Tamil phrasing.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1", "indian-lighting-warm-v1"],
            "prompt_anchors": "South Asian Tamil heritage, dusky to warm skin tones, expressive classical eyes, authentic South Indian bone structure",
            "reasoning": "FLUX.1 captures authentic Tamil aesthetics and photorealistic skin textures.",
        },
        "voice_tts": {
            "ta": {"male": "ta-IN-ValluvarNeural", "female": "ta-IN-PallaviNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Tamil neural voices with authentic Chennai and Tamil Nadu intonation.",
        },
        "audio_soundtrack": {
            "default": "Kollywood melodic fusion with nadaswaram, acoustic veena, and kanjira cadence",
            "comedy": "Lively Tamil comedic acoustic score with mridangam rhythmic beats",
            "drama": "Soulful Tamil raga-based acoustic violin and bansuri flute",
            "dance": "Energetic Tamil kuthu dance rhythm with high-tempo thavil and percussion",
        },
    },
    "indian_malayalam": {
        "culture_name": "Malayalam (Kerala)",
        "primary_ethnicity": "South Asian / Malayali",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Gemini 1.5 Pro for Malayalam poetic sensibilities, Kerala cultural nuances, and Mollywood naturalism.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1"],
            "prompt_anchors": "South Asian Malayali heritage, radiant warm complexion, expressive eyes, authentic Kerala natural aesthetic",
            "reasoning": "FLUX.1 delivers photorealistic Malayali portraiture with natural lighting.",
        },
        "voice_tts": {
            "ml": {"male": "ml-IN-MidhunNeural", "female": "ml-IN-SobhanaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Malayalam neural voices with natural Malayalam prosody.",
        },
        "audio_soundtrack": {
            "default": "Kerala acoustic melody with bamboo flute, chenda undertones, and gentle acoustic guitar",
            "comedy": "Playful Malayalam comedic score with edakka and woodwind accents",
            "drama": "Evocative Mollywood melodic score with lush orchestral strings and acoustic piano",
            "dance": "Vibrant Kerala festive rhythm with chenda melam and syncopated beats",
        },
    },
    "indian_kannada": {
        "culture_name": "Kannada (Karnataka)",
        "primary_ethnicity": "South Asian / Kannadiga",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Gemini 1.5 Pro for Kannada poetic meter (ragale/shatpadi), Sandalwood melody flow, and regional authenticity.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1"],
            "prompt_anchors": "South Asian Kannadiga heritage, warm wheatish complexion, authentic South Indian features",
            "reasoning": "FLUX.1 captures authentic Karnataka facial bone structure and natural skin tone.",
        },
        "voice_tts": {
            "kn": {"male": "kn-IN-GaganNeural", "female": "kn-IN-SapnaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Kannada neural voices with authentic Bengaluru/Mysuru inflection.",
        },
        "audio_soundtrack": {
            "default": "Karnataka acoustic melody with Mysore violin, bansuri, and subtle tabla rhythm",
            "comedy": "Lively Sandalwood comedic score with acoustic percussion",
            "drama": "Emotional Kannada melodic strings and sitar",
            "dance": "Fast-paced Janapada folk rhythm with energetic percussion",
        },
    },
}
