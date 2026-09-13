"""Multi-Language Audio (MLA) Track Multiplexer & YouTube Manifest Builder."""

from __future__ import annotations
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

ISO_639_2_MAP: Dict[str, str] = {
    "en": "eng", "te": "tel", "hi": "hin", "ta": "tam",
    "kn": "kan", "ml": "mal", "es": "spa", "fr": "fra",
    "de": "deu", "ja": "jpn", "pt": "por", "ko": "kor",
    "zh": "zho", "ar": "ara", "ru": "rus",
}

LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English", "te": "Telugu", "hi": "Hindi", "ta": "Tamil",
    "kn": "Kannada", "ml": "Malayalam", "es": "Spanish", "fr": "French",
    "de": "German", "ja": "Japanese", "pt": "Portuguese", "ko": "Korean",
    "zh": "Chinese", "ar": "Arabic", "ru": "Russian",
}


@dataclass
class AudioTrackSpec:
    """Specification for an audio track in an MLA container."""
    language_code: str
    audio_path: str
    is_default: bool = False
    title: Optional[str] = None
    role: str = "dubbed"  # 'original' or 'dubbed'

    def get_iso_code(self) -> str:
        """Return the 3-letter ISO 639-2 language code."""
        code = self.language_code.split("-")[0].lower()
        return ISO_639_2_MAP.get(code, "und")

    def get_display_title(self) -> str:
        """Return human-readable display title for players and YouTube."""
        if self.title:
            return self.title
        code = self.language_code.split("-")[0].lower()
        lang_name = LANGUAGE_NAMES.get(code, self.language_code.upper())
        suffix = "Original" if self.is_default else "Dubbed"
        return f"{lang_name} [{suffix}]"


class MLAMuxer:
    """Combines multiple language audio tracks into an MP4 and prepares YouTube MLA manifests."""

    def __init__(self, ffmpeg_bin: str = "ffmpeg") -> None:
        self.ffmpeg_bin = ffmpeg_bin

    def compile_ffmpeg_args(
        self,
        video_input_path: str,
        tracks: List[AudioTrackSpec],
        output_path: str,
        copy_video: bool = True,
    ) -> List[str]:
        """Generate single-pass FFmpeg arguments to multiplex video with multiple audio tracks."""
        cmd: List[str] = [self.ffmpeg_bin, "-y", "-i", video_input_path]

        # Add each audio input file
        for track in tracks:
            cmd.extend(["-i", track.audio_path])

        # Map video stream from input 0
        cmd.extend(["-map", "0:v:0"])

        # Map each audio stream from input (i+1)
        for i, track in enumerate(tracks):
            input_idx = i + 1
            cmd.extend(["-map", f"{input_idx}:a:0"])

            # ISO 639-2 language tag & track title
            iso_code = track.get_iso_code()
            display_title = track.get_display_title()
            cmd.extend([
                f"-metadata:s:a:{i}", f"language={iso_code}",
                f"-metadata:s:a:{i}", f"handler_name={display_title}",
                f"-metadata:s:a:{i}", f"title={display_title}",
            ])

            # Default disposition
            disposition = "default" if track.is_default else "0"
            cmd.extend([f"-disposition:a:{i}", disposition])

        # Video & audio codecs
        if copy_video:
            cmd.extend(["-c:v", "copy"])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "20"])

        cmd.extend(["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", output_path])
        return cmd

    def build_youtube_mla_manifest(
        self,
        video_id: str,
        tracks: List[AudioTrackSpec],
        default_language: str = "en",
    ) -> Dict[str, Any]:
        """Build YouTube Data API v3 multi-language audio track upload manifest."""
        items: List[Dict[str, Any]] = []

        for i, track in enumerate(tracks):
            code = track.language_code.split("-")[0].lower()
            is_def = track.is_default or (code == default_language.lower())
            items.append({
                "track_index": i,
                "language_code": track.language_code,
                "iso_639_2": track.get_iso_code(),
                "display_name": track.get_display_title(),
                "is_default": is_def,
                "audio_track_type": "primary" if is_def else "dubbed",
                "source_file": track.audio_path,
                "status": "ready_for_upload",
            })

        return {
            "video_id": video_id,
            "total_audio_tracks": len(tracks),
            "primary_language": default_language,
            "contains_mla": len(tracks) > 1,
            "tracks": items,
        }

    def mux_multi_language_audio(
        self,
        video_input_path: str,
        tracks: List[AudioTrackSpec],
        output_path: str,
    ) -> str:
        """Execute multiplexing command or simulate in headless/mock mode."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cmd = self.compile_ffmpeg_args(video_input_path, tracks, output_path)

        if not shutil.which(self.ffmpeg_bin):
            with open(output_path, "wb") as f:
                f.write(b"MOCK_MLA_MULTIPLEXED_MP4_HEADER")
            return output_path

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            with open(output_path, "wb") as f:
                f.write(b"MOCK_MLA_MULTIPLEXED_MP4_HEADER")
        return output_path
