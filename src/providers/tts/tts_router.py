"""Dynamic TTS Provider Router matching user model configuration."""

from typing import Optional
from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import TTSProviderProtocol
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
from src.providers.tts.gemini_audio import GeminiAudioTTSAdapter
from src.providers.tts.kokoro_tts import KokoroTTSAdapter


def get_tts_adapter(model_name: Optional[str] = None) -> TTSProviderProtocol:
    """Resolve and instantiate configured TTS Provider Adapter.
    
    Supported models:
      - 'gemini', 'gemini_audio', 'gemini_2_audio', 'gemini_flash_tts' -> GeminiAudioTTSAdapter
      - 'kokoro', 'kokoro_local', 'local' -> KokoroTTSAdapter
      - 'azure', 'azure_speech', 'edge_tts' -> AzureSpeechTTSAdapter
    """
    eff_model = (model_name or getattr(settings.voice, "default_tts_model", "azure_speech") or "azure_speech").lower().strip()

    if "gemini" in eff_model or "google" in eff_model:
        logger.info(f"tts_router_selected: GeminiAudioTTSAdapter (model='{eff_model}')")
        return GeminiAudioTTSAdapter(default_voice=getattr(settings.voice, "gemini_tts_voice", "Charon"))

    if "kokoro" in eff_model or "local" in eff_model:
        logger.info(f"tts_router_selected: KokoroTTSAdapter (model='{eff_model}')")
        return KokoroTTSAdapter(default_voice=getattr(settings.voice, "kokoro_voice", "bm_george"))

    logger.info(f"tts_router_selected: AzureSpeechTTSAdapter (model='{eff_model}')")
    return AzureSpeechTTSAdapter()


__all__ = ["get_tts_adapter"]
