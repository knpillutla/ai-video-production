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
    "en": {"male": ("en-GB-RyanNeural", "en-GB"), "female": ("en-GB-SoniaNeural", "en-GB")},
    "en-us": {"male": ("en-US-AndrewMultilingualNeural", "en-US"), "female": ("en-US-AvaMultilingualNeural", "en-US")},
    "te": {"male": ("te-IN-MohanNeural", "te-IN"), "female": ("te-IN-ShrutiNeural", "te-IN")},
    "hi": {"male": ("hi-IN-MadhurNeural", "hi-IN"), "female": ("hi-IN-SwaraNeural", "hi-IN")},
    "es": {"male": ("es-ES-AlvaroNeural", "es-ES"), "female": ("es-ES-ElviraNeural", "es-ES")},
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


async def produce_documentary_narration_stage(
    ep_dir: Path,
    voice_id: str = "en-GB-RyanNeural",
    tts_model: str = "azure_speech",
    speech_rate: str = "-16%",
    force_rerun: bool = False,
    execution_mode: str = "test",
) -> Dict[str, Any]:
    """Synthesizes high-fidelity voiceover narration for all chapters of a documentary episode."""
    import json
    import time
    from src.core.storage import storage_service
    from src.studios.documentary_studio.doc_chapter_cadence_service import synthesize_chapter_aligned_narration

    story_file = ep_dir / "raw_gemini_story.json"
    sp_file = ep_dir / "raw_gemini_screenplay.json"

    scenes: list[dict[str, Any]] = []
    story_data: dict[str, Any] = {}
    if story_file.is_file():
        try:
            story_data = json.loads(story_file.read_text("utf-8"))
            for ch in story_data.get("chapters", []):
                scenes.append({
                    "chapter_index": ch.get("chapter_index", 1),
                    "chapter_title": ch.get("chapter_title", ""),
                    "narration_text": ch.get("narration") or ch.get("narration_text", ""),
                    "duration_seconds": max(12.0, round(len((ch.get("narration") or ch.get("narration_text", "")).split()) / 2.0 + 3.0, 1)),
                })
        except Exception as ex:
            logger.warning(f"failed_to_read_raw_story_for_narration: {ex}")

    if not scenes and sp_file.is_file():
        try:
            sp_data = json.loads(sp_file.read_text("utf-8"))
            scenes = sp_data.get("scenes", [])
        except Exception as ex:
            logger.warning(f"failed_to_read_screenplay_for_narration: {ex}")

    if not scenes:
        raise RuntimeError(f"No story chapters or screenplay found in {ep_dir} to synthesize narration.")

    res = await synthesize_chapter_aligned_narration(
        scenes=scenes,
        ep_dir=ep_dir,
        voice_id=voice_id,
        speech_rate=speech_rate,
        lead_in_sec=0.8,
        min_tail_pause_sec=2.5,
        force_rerun=force_rerun,
        tts_model=tts_model,
        execution_mode=execution_mode,
    )

    out_master = ep_dir / "spoken_narration.mp3"
    mtime = int(time.time())
    try:
        rel = out_master.resolve().relative_to(storage_service.root_dir.resolve())
        url = f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
    except Exception:
        url = f"/storage/{out_master.name}?t={mtime}"

    narr_stem = {
        "name": "Neural Broadcast Narration",
        "filename": "spoken_narration.mp3",
        "type": "azure_speech",
        "role": "narration",
        "stem_type": "narration",
        "voice_name": voice_id,
        "duration": f"{res.get('total_duration', 60.0):.1f}s",
        "url": url,
        "status": "completed",
        "color": "indigo",
    }

    pipe_file = ep_dir / "pipeline_state.json"
    pipe_state: dict[str, Any] = {}
    if pipe_file.is_file():
        try:
            pipe_state = json.loads(pipe_file.read_text("utf-8"))
        except Exception:
            pass

    stems = pipe_state.get("audio_stems", [])
    stems = [s for s in stems if s.get("filename") != "spoken_narration.mp3" and s.get("role") != "narration"]
    stems.insert(0, narr_stem)
    pipe_state["audio_stems"] = stems
    pipe_state["current_stage"] = max(pipe_state.get("current_stage", 1), 2)
    stages_comp = pipe_state.setdefault("stages_completed", {})
    stages_comp["story"] = True
    stages_comp["narration"] = True
    stages_comp["audio"] = True
    pipe_state["stage_status"] = "ready"
    try:
        pipe_file.write_text(json.dumps(pipe_state, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"pipeline_state_updated_with_narration: {pipe_file}")
    except Exception as ex:
        logger.warning(f"failed_to_write_pipeline_state_narration: {ex}")

    return {
        "success": True,
        "stage": 2,
        "current_stage": 2,
        "narration_path": str(out_master),
        "audio_stems": stems,
        "total_duration": res.get("total_duration", 60.0),
        "story": story_data or None,
    }


__all__ = [
    "DocumentaryVoiceService",
    "doc_voice_service",
    "produce_documentary_narration_stage",
    "VOICE_MAP",
]
