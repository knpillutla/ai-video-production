"""Cultural, Ethnic, Voice, and Audio Intelligence Catalog for MCP Server."""

from typing import Any
from src.mcp.model_selector.art_style_catalog import ART_STYLE_INTELLIGENCE_CATALOG, lookup_art_style
from src.mcp.model_selector.costume_catalog import COSTUME_INTELLIGENCE_CATALOG, lookup_costume_stack
from src.mcp.model_selector.cultural_matrix_global import GLOBAL_CULTURAL_MODELS
from src.mcp.model_selector.dance_catalog import DANCE_MODEL_MATRIX, lookup_dance_stack

CULTURAL_MODEL_MATRIX: dict[str, dict[str, Any]] = {
    "indian_south": {
        "culture_name": "South Indian (Telugu, Tamil, Kannada, Malayalam)",
        "primary_ethnicity": "South Asian / Dravidian",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Selected Gemini 1.5 Pro for nuanced South Indian cultural ethos, regional Telugu/Tamil comedic timing, dialect idioms, and high context retention.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1", "indian-lighting-warm-v1"],
            "prompt_anchors": "South Asian, warm wheatish and dusky skin tones, authentic Indian facial bone structure, natural dark brown eyes, thick black hair",
            "reasoning": "FLUX.1 with LoRA prompt anchoring renders authentic South Asian skin tones and Dravidian facial features, completely avoiding Western whitewashing.",
        },
        "voice_tts": {
            "te": {"male": "te-IN-MohanNeural", "female": "te-IN-ShrutiNeural"},
            "ta": {"male": "ta-IN-ValluvarNeural", "female": "ta-IN-PallaviNeural"},
            "kn": {"male": "kn-IN-GaganNeural", "female": "kn-IN-SapnaNeural"},
            "ml": {"male": "ml-IN-MidhunNeural", "female": "ml-IN-SobhanaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native South Indian neural voices with authentic regional intonation for Telugu/Tamil/Kannada/Malayalam, and crisp Western narrator for English.",
        },
        "audio_soundtrack": {
            "default": "South Indian cinematic fusion with Carnatic acoustic flute, veena, and subtle mridangam rhythm",
            "comedy": "Playful Tollywood comedic acoustic score with mridangam and konnakol accents",
            "drama": "Emotive Telugu melodic strings, acoustic sitar, and bansuri flute",
            "dance": "High-energy Tollywood mass teenmaar rhythm with nadaswaram and dholak",
        },
    },
    "indian_north": {
        "culture_name": "North Indian (Hindi, Punjabi, Gujarati, Bengali)",
        "primary_ethnicity": "South Asian / Indo-Aryan",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Selected Gemini 1.5 Pro for authentic Hindi/Punjabi colloquial dialogue, poetic metaphors, and cultural festivities.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["south-asian-photoreal-v1"],
            "prompt_anchors": "South Asian, olive to wheatish complexion, expressive features, natural black hair",
            "reasoning": "FLUX.1 diffusion captures authentic North Indian ethnic representation with cinematic depth of field.",
        },
        "voice_tts": {
            "hi": {"male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
            "pa": {"male": "pa-IN-GurpreetNeural", "female": "pa-IN-OjasNeural"},
            "gu": {"male": "gu-IN-NiranjanNeural", "female": "gu-IN-DhwaniNeural"},
            "bn": {"male": "bn-IN-BashkarNeural", "female": "bn-IN-TanishaaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Clear Hindi/Punjabi neural prosody for regional languages, and Western narrator for English.",
        },
        "audio_soundtrack": {
            "default": "North Indian classical fusion with sitar, bansuri flute, and tabla rhythm",
            "comedy": "Lively Bollywood comedic score with playful dholak and acoustic guitar",
            "drama": "Soulful Hindustani acoustic raga with sarod, violin, and slow tabla tempo",
            "dance": "Upbeat Bollywood / Bhangra dance rhythm with energetic 128 BPM dhol",
        },
    },
    "australian": {
        "culture_name": "Australian & Oceanian",
        "primary_ethnicity": "Australian / Oceanian",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Selected Gemini 1.5 Pro for relaxed Australian colloquialisms, Aussie humor, and authentic natural pacing.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["oceanian-coastal-sun-v1"],
            "prompt_anchors": "Sun-kissed complexion, relaxed expressive features, natural Australian coastal lighting",
            "reasoning": "FLUX.1 diffusion captures golden-hour coastal warmth and relaxed Australian demeanor.",
        },
        "voice_tts": {
            "en": {"male": "en-AU-WilliamNeural", "female": "en-AU-NatashaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Authentic Australian neural voice with genuine broad Aussie vowels, relaxed inflection, and natural rhythm.",
        },
        "audio_soundtrack": {
            "default": "Australian acoustic indie-folk with warm coastal guitar and subtle ambient percussion",
            "comedy": "Upbeat sun-drenched Aussie acoustic surf-rock with light upbeat rhythm",
            "drama": "Cinematic ambient outback acoustic with subtle didgeridoo resonance and warm strings",
            "dance": "Energetic modern Australian dance-pop beat",
        },
    },
    "east_asian": {
        "culture_name": "East Asian (Japanese, Korean, Chinese)",
        "primary_ethnicity": "East Asian",
        "scriptwriting": {"model": "claude-3-5-sonnet", "provider": "Anthropic", "reasoning": "Nuanced East Asian honorifics and stylistic restraint."},
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["east-asian-photoreal-v2"],
            "prompt_anchors": "East Asian, natural skin texture, authentic facial contours",
            "reasoning": "High-fidelity East Asian photorealism and anime/manhwa styling capabilities.",
        },
        "voice_tts": {
            "ja": {"male": "ja-JP-KeitaNeural", "female": "ja-JP-NanamiNeural"},
            "ko": {"male": "ko-KR-InJoonNeural", "female": "ko-KR-SunHiNeural"},
            "zh": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native East Asian neural voices with authentic phonemes, and Western narrator for English.",
        },
        "audio_soundtrack": {
            "default": "East Asian ambient acoustic score with traditional shamisen, koto, and shakuhachi flute",
            "comedy": "Quirky anime-inspired upbeat soundtrack with marimba and playful bells",
            "drama": "Cinematic East Asian orchestral strings and gentle piano",
            "dance": "Modern Asian pop beat with synthetic percussion",
        },
    },
    "italian": {
        "culture_name": "Italian & Mediterranean",
        "primary_ethnicity": "Italian / Southern European",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Selected Gemini 1.5 Pro for passionate Italian cadence, comedic operatic expressiveness, and local regional idioms.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["mediterranean-sun-warm-v1"],
            "prompt_anchors": "Warm olive to fair Mediterranean complexion, expressive dark eyes, natural styled hair, golden Italian sunlight",
            "reasoning": "FLUX.1 diffusion captures authentic Italian aesthetic, warm terracotta tones, and scenic Mediterranean vistas.",
        },
        "voice_tts": {
            "it": {"male": "it-IT-DiegoNeural", "female": "it-IT-ElsaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Italian neural voices for Italian language, and Western narrator for English.",
        },
        "audio_soundtrack": {
            "default": "Authentic Italian folk score with lively accordion, mandolin, acoustic guitar, and tambourine rhythm",
            "comedy": "Playful Italian comedic score with upbeat mandolin arpeggios and accordion leaps",
            "drama": "Romantic Italian cinematic orchestral strings with emotive violin and classical acoustic guitar",
            "dance": "Fast 6/8 Italian Tarantella and Pizzica rhythm with energetic tambourine and accordion",
        },
    },
}
CULTURAL_MODEL_MATRIX.update(GLOBAL_CULTURAL_MODELS)


def lookup_cultural_stack(culture: str | None = None, language: str = "en") -> dict[str, Any]:
    """Retrieve optimal AI model stack and cultural rationale for a culture and language."""
    key = (culture or "western_global").lower().replace("-", "_")
    lang = (language or "en").lower().strip().replace("-", "_").split("_")[0]
    if any(k in key for k in ("nordic", "iceland", "sweden", "norway", "denmark", "finland")) or lang in ("is", "sv", "no", "nb", "da", "fi"):
        return CULTURAL_MODEL_MATRIX["nordic"]
    if any(k in key for k in ("british", "uk", "london", "england", "scotland", "britain")):
        return CULTURAL_MODEL_MATRIX["british_uk"]
    if "egypt" in key or "arab" in key or lang == "ar":
        return CULTURAL_MODEL_MATRIX["egyptian"]
    if "ital" in key or lang == "it":
        return CULTURAL_MODEL_MATRIX["italian"]
    if "mexic" in key:
        return CULTURAL_MODEL_MATRIX["mexican"]
    if "aust" in key or "oceania" in key:
        return CULTURAL_MODEL_MATRIX["australian"]
    if "south" in key or lang in ("te", "ta", "kn", "ml"):
        return CULTURAL_MODEL_MATRIX["indian_south"]
    if "north" in key or lang in ("hi", "pa", "gu", "bn"):
        return CULTURAL_MODEL_MATRIX["indian_north"]
    if "east_asian" in key or lang in ("ja", "ko", "zh"):
        return CULTURAL_MODEL_MATRIX["east_asian"]
    return CULTURAL_MODEL_MATRIX["western_global"]


def resolve_cultural_voice(culture: str | None = None, language: str = "en", gender: str = "female") -> str:
    """Resolve culturally authentic, gender-matched neural voice ID.

    Directives:
    - English Audio ('en', 'en-US', 'en-GB', 'en-AU'): ALWAYS Western narrator voice.
    - Language-specific Audio ('te', 'hi', 'ta', 'es', 'it', 'ja', etc.): ALWAYS native language narrator voice.
    """
    raw_lang = (language or "en").lower().strip().replace("-", "_")
    base_lang = raw_lang.split("_")[0]
    g_key = "male" if (gender or "female").lower() == "male" else "female"
    cult_safe = (culture or "western_global").lower().replace("-", "_")

    # 1. English Audio: Always use Western narrator voices
    if base_lang == "en":
        if "british" in cult_safe or "uk" in cult_safe or raw_lang in ("en_gb", "en_uk"):
            return "en-GB-RyanNeural" if g_key == "male" else "en-GB-SoniaNeural"
        if "aust" in cult_safe or raw_lang in ("en_au", "en_nz"):
            return "en-AU-WilliamNeural" if g_key == "male" else "en-AU-NatashaNeural"
        return "en-US-ChristopherNeural" if g_key == "male" else "en-US-JennyNeural"

    # 2. Language-Specific Audio: Resolve native language voice
    stack = lookup_cultural_stack(culture=cult_safe, language=language)
    v_map = stack.get("voice_tts", {})

    for cand in (raw_lang, base_lang):
        if cand in v_map:
            val = v_map[cand]
            if isinstance(val, dict):
                return val.get(g_key, val.get("female", "en-US-JennyNeural"))
            if isinstance(val, str):
                return val

    if base_lang == "te": return "te-IN-MohanNeural" if g_key == "male" else "te-IN-ShrutiNeural"
    if base_lang == "hi": return "hi-IN-MadhurNeural" if g_key == "male" else "hi-IN-SwaraNeural"
    if base_lang == "ta": return "ta-IN-ValluvarNeural" if g_key == "male" else "ta-IN-PallaviNeural"
    if base_lang == "kn": return "kn-IN-GaganNeural" if g_key == "male" else "kn-IN-SapnaNeural"
    if base_lang == "ml": return "ml-IN-MidhunNeural" if g_key == "male" else "ml-IN-SobhanaNeural"
    if base_lang == "it": return "it-IT-DiegoNeural" if g_key == "male" else "it-IT-ElsaNeural"
    if base_lang in ("es", "es_es", "es_mx"): return "es-MX-JorgeNeural" if g_key == "male" else "es-MX-DaliaNeural"
    if base_lang == "ja": return "ja-JP-KeitaNeural" if g_key == "male" else "ja-JP-NanamiNeural"
    if base_lang == "ko": return "ko-KR-InJoonNeural" if g_key == "male" else "ko-KR-SunHiNeural"
    if base_lang == "zh": return "zh-CN-YunxiNeural" if g_key == "male" else "zh-CN-XiaoxiaoNeural"
    if base_lang == "ar": return "ar-EG-ShakirNeural" if g_key == "male" else "ar-EG-SalmaNeural"
    if base_lang in ("is", "sv", "no", "nb", "da", "fi"): return "is-IS-GunnarNeural" if g_key == "male" else "is-IS-GudrunNeural"

    return "en-US-ChristopherNeural" if g_key == "male" else "en-US-JennyNeural"


__all__ = [
    "CULTURAL_MODEL_MATRIX",
    "DANCE_MODEL_MATRIX",
    "COSTUME_INTELLIGENCE_CATALOG",
    "lookup_cultural_stack",
    "lookup_dance_stack",
    "lookup_costume_stack",
    "lookup_art_style",
    "resolve_cultural_voice",
]
