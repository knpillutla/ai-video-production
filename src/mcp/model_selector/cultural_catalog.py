"""Cultural, Ethnic, Voice, and Audio Intelligence Catalog for MCP Server."""

from typing import Any
from src.mcp.model_selector.costume_catalog import COSTUME_INTELLIGENCE_CATALOG, lookup_costume_stack
from src.mcp.model_selector.dance_catalog import DANCE_MODEL_MATRIX, lookup_dance_stack
from src.mcp.model_selector.art_style_catalog import ART_STYLE_INTELLIGENCE_CATALOG, lookup_art_style

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
            "en": {"male": "en-IN-PrabhatNeural", "female": "en-IN-NeerjaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native South Indian neural voices with authentic regional intonation, gender expression, and Indian English cadence.",
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
            "en": {"male": "en-IN-PrabhatNeural", "female": "en-IN-NeerjaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Clear Hindi/Punjabi neural prosody, regional dialect cadence, and Indian English accent.",
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
            "reasoning": "Native East Asian neural voices with authentic phonemes and gender-matched expressiveness.",
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
            "en": {"male": "it-IT-DiegoNeural", "female": "it-IT-ElsaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Italian neural voices with authentic melodic cadence, rolled r's, and expressive theatrical prosody.",
        },
        "audio_soundtrack": {
            "default": "Authentic Italian folk score with lively accordion, mandolin, acoustic guitar, and tambourine rhythm",
            "comedy": "Playful Italian comedic score with upbeat mandolin arpeggios and accordion leaps",
            "drama": "Romantic Italian cinematic orchestral strings with emotive violin and classical acoustic guitar",
            "dance": "Fast 6/8 Italian Tarantella and Pizzica rhythm with energetic tambourine and accordion",
        },
    },
    "mexican": {
        "culture_name": "Mexican & Latin American",
        "primary_ethnicity": "Mexican / Mestizo",
        "scriptwriting": {
            "model": "gemini-1.5-pro",
            "provider": "Google",
            "reasoning": "Selected Gemini 1.5 Pro for authentic Mexican colloquialisms, warm family warmth, and comedic timing.",
        },
        "visual_diffusion": {
            "model": "flux-1-dev",
            "provider": "Fal.ai",
            "recommended_loras": ["mexican-folklore-festive-v1"],
            "prompt_anchors": "Warm golden brown to wheatish complexion, expressive dark almond eyes, radiant warm smile, festive Mexican light",
            "reasoning": "FLUX.1 diffusion captures authentic Mexican heritage, vibrant festive colors, and colonial architectural backgrounds.",
        },
        "voice_tts": {
            "es": {"male": "es-MX-JorgeNeural", "female": "es-MX-DaliaNeural"},
            "en": {"male": "es-MX-JorgeNeural", "female": "es-MX-DaliaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Native Mexican Spanish neural voices with warm, clear, melodic prosody.",
        },
        "audio_soundtrack": {
            "default": "Traditional Mexican Mariachi with acoustic vihuela, guitarrón, trumpets, and violins",
            "comedy": "Lively Mexican Son Jarocho and festive guitar strumming with playful horn flourishes",
            "drama": "Soulful Mexican acoustic guitar ballad with emotive strings and Spanish classical flair",
            "dance": "High-energy Mexican Ballet Folklórico zapateado with rhythmic heel stomps and brass mariachi fanfare",
        },
    },
    "western_global": {
        "culture_name": "Western & Global General",
        "primary_ethnicity": "Global Diverse",
        "scriptwriting": {"model": "gemini-1.5-pro", "provider": "Google", "reasoning": "Universal structured 3-act narrative and dialogue delivery."},
        "visual_diffusion": {"model": "flux-1-dev", "provider": "Fal.ai", "recommended_loras": [], "prompt_anchors": "Cinematic photorealistic 4K broadcast still"},
        "voice_tts": {
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "en_gb": {"male": "en-GB-RyanNeural", "female": "en-GB-SoniaNeural"},
            "en_au": {"male": "en-AU-WilliamNeural", "female": "en-AU-NatashaNeural"},
            "es": {"male": "es-ES-AlvaroNeural", "female": "es-ES-ElviraNeural"},
            "fr": {"male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
            "de": {"male": "de-DE-ConradNeural", "female": "de-DE-KatjaNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Crisp broadcast documentary and narrative neural voices with gender-matched persona.",
        },
        "audio_soundtrack": {
            "default": "Cinematic orchestral score with contemporary acoustic instrumentation",
            "comedy": "Upbeat comedic acoustic score with pizzicato strings and light rhythm",
            "drama": "Cinematic dramatic orchestral strings with subtle emotional piano",
            "dance": "Modern high-energy pop and electronic dance groove",
        },
    },
    "egyptian": {
        "culture_name": "Ancient Egyptian & Middle Eastern",
        "primary_ethnicity": "Egyptian / Middle Eastern",
        "scriptwriting": {"model": "gemini-1.5-pro", "provider": "Google", "reasoning": "Historical Egyptian narrative and mythology."},
        "visual_diffusion": {"model": "flux-1-dev", "provider": "TogetherAI", "recommended_loras": ["ancient-egypt-hieroglyphs-v1"], "prompt_anchors": "Mediterranean olive skin, dramatic kohl smokey eyeliner, gold diadem, sandstone temple lighting"},
        "voice_tts": {
            "ar": {"male": "ar-EG-ShakirNeural", "female": "ar-EG-SalmaNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD",
            "reasoning": "Authentic Egyptian Arabic regional neural voices with historical dignified cadence.",
        },
        "audio_soundtrack": {
            "default": "Exotic ancient Egyptian and Middle Eastern raga with ney flute, oud, darbuka, and ethereal vocalizations",
            "comedy": "Lively Arabic folk rhythm with joyful darbuka and riq percussion",
            "drama": "Haunting desert ambient strings with deep ney flute meditation and slow frame drum",
            "dance": "Hypnotic Middle Eastern bellydance rhythm with energetic darbuka and qanun melody",
        },
    },
}


def lookup_cultural_stack(culture: str | None = None, language: str = "en") -> dict[str, Any]:
    """Retrieve optimal AI model stack and cultural rationale for a culture and language."""
    key = (culture or "western_global").lower().replace("-", "_")
    lang = (language or "en").lower().strip().replace("-", "_").split("_")[0]
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
    """Resolve culturally authentic, gender-matched neural voice ID."""
    cult_safe = culture or "western_global"
    stack = lookup_cultural_stack(culture=cult_safe, language=language)
    v_map = stack.get("voice_tts", {})
    raw_lang = (language or "en").lower().strip().replace("-", "_")
    base_lang = raw_lang.split("_")[0]
    g_key = "male" if (gender or "female").lower() == "male" else "female"

    for cand in (raw_lang, base_lang):
        if cand in v_map:
            val = v_map[cand]
            if isinstance(val, dict):
                return val.get(g_key, val.get("female", "en-US-JennyNeural"))
            if isinstance(val, str):
                return val

    # Fallbacks based on culture and gender
    if "egypt" in cult_safe or "arab" in cult_safe:
        return "ar-EG-ShakirNeural" if g_key == "male" else "ar-EG-SalmaNeural"
    if "ital" in cult_safe:
        return "it-IT-DiegoNeural" if g_key == "male" else "it-IT-ElsaNeural"
    if "mexic" in cult_safe:
        return "es-MX-JorgeNeural" if g_key == "male" else "es-MX-DaliaNeural"
    if "south" in cult_safe:
        return "te-IN-MohanNeural" if g_key == "male" else "te-IN-ShrutiNeural"
    if "aust" in cult_safe:
        return "en-AU-WilliamNeural" if g_key == "male" else "en-AU-NatashaNeural"
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
