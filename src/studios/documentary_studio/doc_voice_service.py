"""Documentary Voice Synthesis Service.

Produces authoritative natural history narration with Western voice defaults,
female voice overrides, multilingual support (Telugu/Hindi/etc.), and fatigue-free balanced cadence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple
import wave

from src.core.telemetry import logger
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter

# Curated Documentary Voice Matrix
VOICE_MAP: Dict[str, Dict[str, Tuple[str, str]]] = {
    # lang -> { "male": (voice_id, lang_code), "female": (voice_id, lang_code) }
    "en": {
        "male": ("en-GB-RyanNeural", "en-GB"),  # Authoritative BBC/David Attenborough cadence
        "female": ("en-GB-SoniaNeural", "en-GB"),  # Stately BBC Earth natural history cadence
    },
    "en-us": {
        "male": ("en-US-AndrewMultilingualNeural", "en-US"),
        "female": ("en-US-AvaMultilingualNeural", "en-US"),
    },
    "te": {
        "male": ("te-IN-MohanNeural", "te-IN"),  # Resonant Telugu documentary narrator
        "female": ("te-IN-ShrutiNeural", "te-IN"),
    },
    "hi": {
        "male": ("hi-IN-MadhurNeural", "hi-IN"),  # Authoritative Hindi documentary narrator
        "female": ("hi-IN-SwaraNeural", "hi-IN"),
    },
    "es": {
        "male": ("es-ES-AlvaroNeural", "es-ES"),
        "female": ("es-ES-ElviraNeural", "es-ES"),
    },
}


class DocumentaryVoiceService:
    """Synthesizes high-clarity documentary narration tracks."""

    def __init__(self):
        self.tts_adapter = AzureSpeechTTSAdapter()

    def get_voice_details(self, language: str = "en", female: bool = False) -> Tuple[str, str]:
        """Select appropriate high-definition documentary narrator voice."""
        lang_key = language.lower().split("-")[0]
        gender_key = "female" if female else "male"
        
        lang_voices = VOICE_MAP.get(lang_key, VOICE_MAP["en"])
        return lang_voices.get(gender_key, lang_voices["male"])

    def get_speech_cadence(self, language: str = "en", female: bool = False) -> Tuple[int, float, str]:
        """Returns calibrated (wpm, words_per_second, provider_and_voice_desc)."""
        voice_id, _ = self.get_voice_details(language=language, female=female)
        lang_key = language.lower().split("-")[0]
        cadence_matrix = {
            "en": (118, 1.96) if not female else (122, 2.03),
            "en-us": (135, 2.25),
            "te": (105, 1.75),
            "hi": (110, 1.83),
            "es": (125, 2.08),
        }
        wpm, wps = cadence_matrix.get(lang_key, (120, 2.0))
        return wpm, round(wps, 2), f"Azure Speech Neural ({voice_id})"

    async def synthesize_scene_narration(
        self,
        text: str,
        output_wav: Path,
        language: str = "en",
        female: bool = False,
    ) -> Path:
        """Synthesize a single scene's narration text to 48kHz WAV audio."""
        out = output_wav.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.is_file() and out.stat().st_size > 1000:
            logger.info(f"narration_cache_hit: Reusing {out.name}")
            return out

        voice_id, lang_code = self.get_voice_details(language=language, female=female)
        logger.info(f"synthesizing_documentary_narration: voice={voice_id} lang={lang_code} chars={len(text)}")

        raw_pcm = await self.tts_adapter.synthesize_speech(
            text=text,
            voice_id=voice_id,
            language_code=lang_code,
        )

        out.write_bytes(raw_pcm)
        return out

    async def synthesize_full_documentary_voiceover(
        self,
        scenes_narration: list[str],
        output_full_wav: Path,
        scene_durations: list[float],
        language: str = "en",
        female: bool = False,
    ) -> Path:
        """Synthesize and assemble timed narration track with breathable scene intervals."""
        out = output_full_wav.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.is_file() and out.stat().st_size > 1000:
            logger.info(f"full_voiceover_cache_hit: Reusing {out.name}")
            return out

        # Generate individual scene stems and concatenate with natural scene spacing
        temp_dir = out.parent / "temp_narration"
        temp_dir.mkdir(parents=True, exist_ok=True)

        stems = []
        for idx, text in enumerate(scenes_narration):
            stem_path = temp_dir / f"scene_{idx+1}_narr.wav"
            await self.synthesize_scene_narration(
                text=text,
                output_wav=stem_path,
                language=language,
                female=female,
            )
            stems.append(stem_path)

        # Build concatenated audio file with silent padding matching scene lengths
        sample_rate = 48000
        channels = 1
        sampwidth = 2
        silence_lead = b"\x00" * int(sample_rate * channels * sampwidth * 0.5)

        full_frames = bytearray()
        actual_scene_durations = []
        for stem, target_dur in zip(stems, scene_durations):
            with wave.open(str(stem), "rb") as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                frames = wf.readframes(wf.getnframes())

            scene_bytes = bytearray(silence_lead)
            scene_bytes.extend(frames)

            bytes_per_sec = sample_rate * channels * sampwidth
            stem_dur = len(scene_bytes) / bytes_per_sec
            # NatGeo 2-Second Rule: Allocate at least 2.2s silence tail for musical breathing space
            eff_dur = max(float(target_dur), stem_dur + 2.2)
            actual_scene_durations.append(round(eff_dur, 2))

            target_bytes = int(eff_dur * bytes_per_sec)
            if len(scene_bytes) < target_bytes:
                scene_bytes.extend(b"\x00" * (target_bytes - len(scene_bytes)))

            full_frames.extend(scene_bytes)

        with wave.open(str(out), "wb") as wf_out:
            wf_out.setnchannels(channels)
            wf_out.setsampwidth(sampwidth)
            wf_out.setframerate(sample_rate)
            wf_out.writeframes(full_frames)

        logger.info(f"documentary_voiceover_assembled: {out.name} ({len(actual_scene_durations)} scenes, total: {sum(actual_scene_durations)}s)")
        return out, actual_scene_durations

    async def synthesize_multilingual_tracks(
        self,
        scenes_narration: list[str],
        base_dir: Path,
        scene_durations: list[float],
        target_languages: tuple[str, ...] = ("es", "hi", "te"),
    ) -> list[dict[str, str]]:
        """Synthesize and package multilingual voice stems for YouTube multi-track audio."""
        tracks = []
        for lang in target_languages:
            voice_id, _ = self.get_voice_details(language=lang)
            lang_wav = base_dir / f"voice_{lang}.wav"
            try:
                out_path, _ = await self.synthesize_full_documentary_voiceover(
                    scenes_narration=scenes_narration,
                    output_full_wav=lang_wav,
                    scene_durations=scene_durations,
                    language=lang,
                )
                tracks.append({"language": lang, "voice_id": voice_id, "file_path": str(out_path)})
            except Exception as ex:
                logger.warning(f"multilingual_synthesis_skipped for {lang}: {ex}")
        return tracks


doc_voice_service = DocumentaryVoiceService()
__all__ = ["DocumentaryVoiceService", "doc_voice_service", "VOICE_MAP"]
