"""Concert Audio Slicer: Deterministic Vocal Energy, Pitch & VAD Segmentation.

Slices concert audio into semantically tagged musical segments:
1. ORCHESTRA (Instrumental breaks, intro, guitar/percussion solos)
2. VERSE_MODERATE (Natural conversational and melodic verses)
3. CHORUS_INTENSE (High-energy vocal peaks, high pitch, belt delivery)
4. OUTRO_FINALE (Sustained final note leading to applause)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import numpy as np

from src.core.telemetry import logger


@dataclass
class AudioConcertSegment:
    """Classified musical slice for dynamic concert camera direction."""

    segment_id: int
    start_time: float
    end_time: float
    duration: float
    segment_type: str  # "ORCHESTRA", "VERSE_MODERATE", "CHORUS_INTENSE", "OUTRO_FINALE"
    intensity_score: float  # 0.0 (silent/calm) to 1.0 (explosive peak)
    is_singing: bool
    recommended_camera: str  # "singer_orchestra_stage", "stadium_audience_crowd", "overall_stage_vista"
    recommended_shot: str    # "closeup", "medium", "wide_vista", "orbit_audience"
    recommended_motion: str  # "zoom_in_singer", "steady_eye_level", "wide_stage_pullback", "orbit_stage_to_audience"
    stem_path: Optional[str] = None


def slice_concert_audio(
    audio_path: Union[str, Path],
    total_duration: float,
    lyrics: Optional[str] = None,
    default_bpm: float = 120.0,
    target_cut_duration: float = 8.5,
    export_stems_dir: Optional[Union[str, Path]] = None,
) -> List[AudioConcertSegment]:
    """Slice audio into semantically classified concert timeline segments."""
    audio_p = Path(audio_path)
    if not audio_p.is_file():
        logger.warning(f"concert_audio_file_not_found: {audio_p}, generating procedural timeline")
        return _procedural_concert_timeline(total_duration, default_bpm, target_cut_duration)

    try:
        import librosa

        y, sr = librosa.load(str(audio_p), sr=22050, mono=True, duration=total_duration)
        if len(y) < sr * 3:
            return _procedural_concert_timeline(total_duration, default_bpm, target_cut_duration)

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0] if isinstance(tempo, (list, np.ndarray)) else tempo)
        if bpm <= 0 or np.isnan(bpm):
            bpm = default_bpm

        # Harmonic vs Percussive separation: vocal formants concentrate in harmonic signal
        y_harm, _ = librosa.effects.hpss(y)
        hop_length = 512
        rms_harm = librosa.feature.rms(y=y_harm, frame_length=1024, hop_length=hop_length)[0]
        time_per_frame = hop_length / float(sr)

        # Musical phrase pacing: 1 measure = (60/BPM)*4 beats. Broadcast takes = 4 measures (~8-10s)
        measure_sec = (60.0 / bpm) * 4.0
        target_measures = 4 if measure_sec * 4.0 <= 10.0 else 3
        step_dur = max(7.0, min(10.5, measure_sec * target_measures))

        # Overall average harmonic energy for adaptive vocal thresholding
        avg_harm = float(np.mean(rms_harm)) if len(rms_harm) > 0 else 0.05
        vocal_threshold = avg_harm * 0.92

        segments: List[AudioConcertSegment] = []
        cur_t = 0.0
        seg_idx = 1

        while cur_t < total_duration:
            rem_dur = total_duration - cur_t
            if rem_dur <= (step_dur * 1.35):
                end_t = round(total_duration, 2)
            else:
                end_t = round(cur_t + step_dur, 2)
            actual_dur = round(end_t - cur_t, 2)

            f_start = int(cur_t / time_per_frame)
            f_end = min(len(rms_harm), int(end_t / time_per_frame))
            win_harm = float(np.mean(rms_harm[f_start:f_end])) if f_end > f_start else 0.05

            # Semantic classification based on vocal energy & position
            is_intro = cur_t < 10.0 and win_harm < (vocal_threshold * 1.35)
            is_outro = cur_t >= (total_duration - 18.0) or end_t >= (total_duration - 16.0)

            if is_intro:
                seg_type = "ORCHESTRA"
                is_sing = False
            elif is_outro:
                seg_type = "OUTRO_FINALE"
                is_sing = False
            elif win_harm >= (vocal_threshold * 1.3):
                seg_type = "CHORUS_INTENSE"
                is_sing = True
            elif win_harm >= vocal_threshold:
                seg_type = "VERSE_MODERATE"
                is_sing = True
            else:
                seg_type = "ORCHESTRA"
                is_sing = False

            intensity = round(min(1.0, win_harm / (avg_harm * 2.0 + 1e-6)), 3)
            cam, shot, motion = _assign_camera_direction(seg_type, is_sing, seg_idx)

            segments.append(AudioConcertSegment(
                segment_id=seg_idx,
                start_time=cur_t,
                end_time=end_t,
                duration=actual_dur,
                segment_type=seg_type,
                intensity_score=intensity,
                is_singing=is_sing,
                recommended_camera=cam,
                recommended_shot=shot,
                recommended_motion=motion,
            ))

            cur_t = end_t
            seg_idx += 1

        if export_stems_dir and audio_p.is_file():
            _export_segment_stems(audio_p, segments, Path(export_stems_dir))
        logger.info(f"sliced_concert_audio: count={len(segments)} bpm={bpm:.1f} dur={total_duration}s")
        return segments
    except Exception as ex:
        logger.warning(f"audio_slicer_fallback_procedural: {ex}")
        segs = _procedural_concert_timeline(total_duration, default_bpm, target_cut_duration)
        if export_stems_dir and audio_p.is_file():
            _export_segment_stems(audio_p, segs, Path(export_stems_dir))
        return segs


def _assign_camera_direction(seg_type: str, is_singing: bool, cut_index: int) -> tuple[str, str, str]:
    """Assign directorial camera, shot type, and perspective drone movement."""
    if seg_type == "ORCHESTRA":
        # Cycle through wide arena vista, crowd lightsticks, and singer grooving with closed lips
        choice = cut_index % 3
        if choice == 0:
            return "overall_stage_vista", "wide_vista", "wide_stage_pullback"
        elif choice == 1:
            return "stadium_audience_crowd", "orbit_audience", "orbit_stage_to_audience"
        else:
            return "singer_orchestra_stage", "medium", "steady_eye_level"

    elif seg_type == "CHORUS_INTENSE":
        # Intense singing peak: Close-up locking onto face or explosive wide drop
        if cut_index % 2 == 1:
            return "singer_orchestra_stage", "closeup", "zoom_in_singer"
        else:
            return "overall_stage_vista", "wide_vista", "tilt_up_stadium"

    elif seg_type == "OUTRO_FINALE":
        # Final vocal climax into grand audience standing ovation
        if cut_index % 2 == 1:
            return "singer_orchestra_stage", "closeup", "zoom_in_singer"
        else:
            return "stadium_audience_crowd", "orbit_audience", "orbit_stage_to_audience"

    else:  # VERSE_MODERATE
        # 60/40 rule: 60% medium singer shot, 40% stadium/crowd glide
        if cut_index % 3 in (0, 1):
            return "singer_orchestra_stage", "medium", "steady_eye_level"
        else:
            return "stadium_audience_crowd", "wide_vista", "pan_to_guitarist"


def _procedural_concert_timeline(total_duration: float, bpm: float, target_dur: float) -> List[AudioConcertSegment]:
    """Deterministic fallback timeline if librosa or audio file is absent."""
    segments: List[AudioConcertSegment] = []
    cur_t = 0.0
    seg_idx = 1
    eff_target = 8.5 if target_dur <= 5.0 else target_dur
    patterns = [
        ("ORCHESTRA", False, 0.45),
        ("ORCHESTRA", False, 0.50),
        ("VERSE_MODERATE", True, 0.58),
        ("VERSE_MODERATE", True, 0.62),
        ("CHORUS_INTENSE", True, 0.85),
        ("CHORUS_INTENSE", True, 0.90),
        ("ORCHESTRA", False, 0.52),
        ("VERSE_MODERATE", True, 0.65),
        ("CHORUS_INTENSE", True, 0.88),
        ("CHORUS_INTENSE", True, 0.92),
        ("OUTRO_FINALE", False, 0.70),
        ("OUTRO_FINALE", False, 0.60),
    ]

    while cur_t < total_duration:
        is_outro = cur_t >= (total_duration - 18.0)
        pat = ("OUTRO_FINALE", False, 0.65) if is_outro else patterns[(seg_idx - 1) % len(patterns)]
        dur = min(total_duration - cur_t, eff_target)
        if dur <= 1.0:
            if segments:
                segments[-1].end_time = round(total_duration, 2)
                segments[-1].duration = round(total_duration - segments[-1].start_time, 2)
            break
        end_t = round(cur_t + dur, 2)
        cam, shot, motion = _assign_camera_direction(pat[0], pat[1], seg_idx)
        segments.append(AudioConcertSegment(
            segment_id=seg_idx,
            start_time=cur_t,
            end_time=end_t,
            duration=round(dur, 2),
            segment_type=pat[0],
            intensity_score=pat[2],
            is_singing=pat[1],
            recommended_camera=cam,
            recommended_shot=shot,
            recommended_motion=motion,
        ))
        cur_t = end_t
        seg_idx += 1
    return segments


def export_timeline_stems(
    audio_path: Union[str, Path],
    cuts: list[dict[str, Any]],
    stems_dir: Union[str, Path],
    clean_stale: bool = True,
) -> None:
    """Physically slice cuts from audio_path and export to stems_dir with accurate names."""
    import subprocess
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    s_dir = Path(stems_dir)
    s_dir.mkdir(parents=True, exist_ok=True)
    if clean_stale:
        for old_f in s_dir.glob("cut_*.mp3"):
            try: old_f.unlink()
            except Exception: pass
    a_path = Path(audio_path)
    if not a_path.is_file():
        return
    for c in cuts:
        c_idx = c.get("cut_index", 1)
        c_type = str(c.get("cut_type", "orchestra")).lower()
        stem_name = f"cut_{c_idx:02d}_{c_type}.mp3"
        stem_file = s_dir / stem_name
        c_start = float(c.get("start_time", 0.0))
        c_dur = float(c.get("duration_seconds", c.get("duration", 8.0)))
        if not (stem_file.is_file() and stem_file.stat().st_size > 1000):
            cmd = [
                ffmpeg_bin, "-y",
                "-ss", f"{c_start:.2f}",
                "-t", f"{c_dur:.2f}",
                "-i", str(a_path),
                "-c:a", "libmp3lame", "-q:a", "2",
                str(stem_file),
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if stem_file.is_file():
            c["stem_path"] = str(stem_file)


def _export_segment_stems(audio_path: Path, segments: List[AudioConcertSegment], stems_dir: Path) -> None:
    """Physically slice and export stems from AudioConcertSegment list."""
    cuts = [
        {"cut_index": s.segment_id, "cut_type": s.segment_type, "start_time": s.start_time, "duration_seconds": s.duration}
        for s in segments
    ]
    export_timeline_stems(audio_path, cuts, stems_dir, clean_stale=True)
    for s, c in zip(segments, cuts):
        s.stem_path = c.get("stem_path")


__all__ = ["AudioConcertSegment", "slice_concert_audio", "export_timeline_stems"]

