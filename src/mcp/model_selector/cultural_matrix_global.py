"""Global, Western, Egyptian, Nordic, and British Cultural Intelligence Model Matrix."""

from typing import Any

GLOBAL_CULTURAL_MODELS: dict[str, dict[str, Any]] = {
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
    "nordic": {
        "culture_name": "Nordic & Scandinavian (Iceland, Sweden, Norway, Denmark, Finland)",
        "primary_ethnicity": "Nordic / Scandinavian",
        "scriptwriting": {"model": "gemini-1.5-pro", "provider": "Google", "reasoning": "Atmospheric Nordic storytelling and folklore."},
        "visual_diffusion": {"model": "flux-1-dev", "provider": "Fal.ai", "recommended_loras": [], "prompt_anchors": "Nordic landscape, crisp Scandinavian architecture, natural cool daylight"},
        "voice_tts": {
            "is": {"male": "is-IS-GunnarNeural", "female": "is-IS-GudrunNeural"},
            "sv": {"male": "sv-SE-MattiasNeural", "female": "sv-SE-SofieNeural"},
            "no": {"male": "nb-NO-FinnNeural", "female": "nb-NO-PernilleNeural"},
            "da": {"male": "da-DK-JeppeNeural", "female": "da-DK-ChristelNeural"},
            "fi": {"male": "fi-FI-HarriNeural", "female": "fi-FI-NooraNeural"},
            "en": {"male": "en-US-ChristopherNeural", "female": "en-US-JennyNeural"},
            "provider": "Microsoft Azure Speech HD", "reasoning": "Clear Nordic/Scandinavian neural voices.",
        },
        "audio_soundtrack": {
            "default": "Atmospheric Nordic acoustic folk with acoustic guitar, ambient cello, and soft piano",
            "comedy": "Lighthearted Scandinavian acoustic score with upbeat guitar and marimba",
            "drama": "Cinematic Nordic noir strings with deep cello drones and ambient piano",
            "dance": "Nordic folk dance rhythm with hardanger fiddle and steady percussion",
        },
    },
    "british_uk": {
        "culture_name": "British & United Kingdom (London, England, Scotland, Wales)",
        "primary_ethnicity": "British / European",
        "scriptwriting": {"model": "gemini-1.5-pro", "provider": "Google", "reasoning": "British wit, regal historical lore, and refined cadence."},
        "visual_diffusion": {"model": "flux-1-dev", "provider": "Fal.ai", "recommended_loras": [], "prompt_anchors": "British architecture, historic London limestone, Victorian streetscape, natural daylight"},
        "voice_tts": {
            "en": {"male": "en-GB-RyanNeural", "female": "en-GB-SoniaNeural"},
            "provider": "Microsoft Azure Speech HD", "reasoning": "Refined British RP neural voice.",
        },
        "audio_soundtrack": {
            "default": "Refined British orchestral strings with classical piano and acoustic guitar",
            "comedy": "Playful British comedy score with pizzicato strings and light woodwinds",
            "drama": "Stately cinematic British royal orchestral score with majestic brass and strings",
            "dance": "Modern British indie rock and dance groove",
        },
    },
}

__all__ = ["GLOBAL_CULTURAL_MODELS"]
