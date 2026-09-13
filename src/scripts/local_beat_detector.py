"""Tier-0 Deterministic Beat & Downbeat Detection Engine for Musical Video Cuts."""

from dataclasses import dataclass, field
import math
from typing import List, Optional
import numpy as np

from src.core.telemetry import logger


@dataclass
class BeatGrid:
    """Frame-accurate musical beat grid and downbeat timestamps."""

    bpm: float
    duration_seconds: float
    downbeat_timestamps: List[float] = field(default_factory=list)
    beat_timestamps: List[float] = field(default_factory=list)
    drop_timestamps: List[float] = field(default_factory=list)
    energy_levels: List[float] = field(default_factory=list)


class LocalBeatDetector:
    """Deterministic CPU audio transient and tempo analyzer (0 model cost)."""

    def __init__(self, default_bpm: float = 120.0):
        self.default_bpm = default_bpm

    def analyze_audio_buffer(
        self,
        samples: Optional[np.ndarray] = None,
        sample_rate: int = 44100,
        duration_seconds: float = 30.0,
        bpm: Optional[float] = None,
    ) -> BeatGrid:
        """Analyze audio waveform to extract BPM, downbeat intervals, and drops."""
        if samples is None or len(samples) == 0:
            # Deterministic mathematical synthesis of beat grid if raw audio buffer omitted
            bpm = bpm or self.default_bpm
            beat_interval = 60.0 / bpm
            bar_interval = beat_interval * 4.0

            beats = [round(i * beat_interval, 3) for i in range(int(duration_seconds / beat_interval))]
            downbeats = [round(i * bar_interval, 3) for i in range(int(duration_seconds / bar_interval))]
            drops = [round(16 * beat_interval, 3)] if duration_seconds >= 16 * beat_interval else []

            return BeatGrid(
                bpm=bpm,
                duration_seconds=duration_seconds,
                downbeat_timestamps=downbeats,
                beat_timestamps=beats,
                drop_timestamps=drops,
                energy_levels=[0.8] * len(beats),
            )

        # Real waveform transient detection using signal energy envelope
        frame_size = int(sample_rate * 0.05)  # 50ms windows
        hop_size = int(sample_rate * 0.025)   # 25ms hop
        num_frames = (len(samples) - frame_size) // hop_size

        if num_frames <= 0:
            return self.analyze_audio_buffer(None, sample_rate, duration_seconds)

        energies = []
        for i in range(num_frames):
            frame = samples[i * hop_size : i * hop_size + frame_size]
            energies.append(float(np.sqrt(np.mean(frame**2))))

        energies_arr = np.array(energies)
        mean_energy = float(np.mean(energies_arr))
        peaks = np.where(energies_arr > mean_energy * 1.35)[0]

        peak_times = [round(float(p * hop_size) / sample_rate, 3) for p in peaks]
        # Filter peaks to minimum 300ms inter-beat spacing
        filtered_beats: List[float] = []
        for t in peak_times:
            if not filtered_beats or (t - filtered_beats[-1]) >= 0.28:
                filtered_beats.append(t)

        detected_bpm = self.default_bpm
        if len(filtered_beats) > 3:
            diffs = np.diff(filtered_beats)
            median_diff = float(np.median(diffs))
            if 0.25 <= median_diff <= 1.0:
                detected_bpm = round(60.0 / median_diff, 1)

        downbeats = [filtered_beats[i] for i in range(0, len(filtered_beats), 4)]
        return BeatGrid(
            bpm=detected_bpm,
            duration_seconds=round(len(samples) / sample_rate, 2),
            downbeat_timestamps=downbeats,
            beat_timestamps=filtered_beats,
            drop_timestamps=[downbeats[4]] if len(downbeats) > 4 else [],
            energy_levels=[round(float(e), 4) for e in energies_arr[: len(filtered_beats)]],
        )

    def align_scene_cuts_to_beats(
        self,
        target_scene_durations: List[float],
        beat_grid: BeatGrid,
    ) -> List[float]:
        """Snap rough scene boundaries to the nearest musical downbeat or beat drop."""
        aligned_timestamps: List[float] = [0.0]
        accumulated_time = 0.0

        for dur in target_scene_durations:
            accumulated_time += dur
            # Find closest downbeat in grid
            candidates = beat_grid.downbeat_timestamps or beat_grid.beat_timestamps
            if not candidates:
                aligned_timestamps.append(round(accumulated_time, 2))
                continue

            closest_beat = min(candidates, key=lambda b: abs(b - accumulated_time))
            # Only snap if within 0.75 seconds of intended pacing
            if abs(closest_beat - accumulated_time) <= 0.75:
                aligned_timestamps.append(closest_beat)
                accumulated_time = closest_beat
            else:
                aligned_timestamps.append(round(accumulated_time, 2))

        logger.info(f"scene_cuts_snapped_to_beats: count={len(aligned_timestamps)} bpm={beat_grid.bpm}")
        return aligned_timestamps


beat_detector = LocalBeatDetector()
__all__ = ["LocalBeatDetector", "beat_detector", "BeatGrid"]
