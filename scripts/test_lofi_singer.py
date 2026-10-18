"""Telugu Lo-Fi Music Video Production Script (Strictly Idempotent & Cost-Guarded).

Architecture:
- Rule 3 Universal Artifact Caching: Zero duplicate calls. If song, base video, or scene
  clip exists on disk (>1000 bytes), external models are NEVER called again.
- Auto-splitting: Slices the MP3 into Instrumental (Intro/Interlude: looped living motion, mouth closed)
  and Singing (Verse/Chorus: ByteDance LatentSync beat-matched mouth motion) segments.
- Resumable: If stopped mid-run, it synthesizes ONLY missing scenes on restart ($0.00 for completed ones).
- Cost Guard: Uses Wan 2.1 living base ($0.40) + LatentSync ($0.20/clip) instead of $9.60 image-to-video.
- Hardware: Zero local GPU required (Fal cloud + local CPU FFmpeg).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import imageio_ffmpeg
from src.core.telemetry import logger
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.services.ambient_export_service import get_media_duration

TELUGU_LOFI_LYRICS = """
[Verse 1 - Soft & Whispered]
కదిలే మేఘం అడిగే తీరం...
కలలో నీవే నా ఏకాంతం...
తడిసే ప్రాణం వెతికే రూపం...
వెన్నెల దారిన నీ చిరునవ్వుల రాగం...

[Chorus - Melodic Lo-Fi Hook]
ఒక బృందావనం నా మదిలోన విరిసెనులే...
ప్రతి శ్వాసలో నీ జత కోరెనులే...
చిరుగాలిలా నను తాకగ రావా...
ఈ తీయని కల నిజమవ్వగ రావా...
""".strip()

DEFAULT_IMAGE_PROMPT = (
    "Aesthetic 4K cinematic portrait of a beautiful South Indian woman (balanced fit build, mid-20s, graceful features), "
    "wearing a cozy oversized cream knit sweater, sitting at a wooden window seat listening to headphones. "
    "Raindrops trickling down the glass, warm glowing incandescent desk lamp and tea mug on the sill, "
    "soft evening twilight outside, moody nostalgic amber and teal color grade, 35mm f/1.4 shallow depth of field, photorealistic."
)


async def produce_lofi_song_idempotent(output_dir: Path, custom_audio: Optional[Path] = None, title: str = "Oka Brundavanam Telugu Lo-Fi") -> Path:
    """Step 1: Produce or retrieve the Suno audio track with strict Rule 3 idempotency."""
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", title.lower()).strip("_")
    target_mp3 = output_dir / f"{clean_name}.mp3"

    if custom_audio and custom_audio.is_file():
        logger.info(f"using_custom_audio: {custom_audio}")
        return custom_audio

    # Tier 1 Local Disk Check: If MP3 exists on disk (>10KB), NEVER call Suno again
    if target_mp3.is_file() and target_mp3.stat().st_size > 10000:
        logger.info(f"lofi_audio_cache_hit: [IDEMPOTENT SKIP] Reusing {target_mp3.name} ($0.00 spend)")
        print(f"  [CACHE HIT] Reusing existing song on disk: {target_mp3.name} ($0.00 spend)")
        return target_mp3

    # Also check if any existing suno mp3 sits in the output directory
    existing_mp3s = list(output_dir.glob("*.mp3"))
    if existing_mp3s:
        best = max(existing_mp3s, key=lambda f: f.stat().st_size)
        if best.stat().st_size > 10000:
            print(f"  [CACHE HIT] Found existing project song: {best.name} ($0.00 spend)")
            return best

    print(f"  [SYNTHESIZING] Calling Suno v3.5 Pro for '{title}'...")
    suno = SunoMusicAdapter()
    audio_path = await suno.generate_to_file(
        output_path=target_mp3,
        genre="telugu lo-fi chillhop, nostalgic melody",
        mood="warm rhodes, vinyl crackle, gentle flute",
        duration_seconds=72.0,
        lyrics=TELUGU_LOFI_LYRICS,
        vocal_gender="female",
        title=title,
    )
    return Path(audio_path)


async def produce_living_base_video_idempotent(output_dir: Path, custom_video: Optional[Path] = None) -> Path:
    """Step 2: Generate or retrieve living character base loop via Wan 2.1 with strict disk check."""
    target_vid = output_dir / "character_living_motion_5s.mp4"
    if custom_video and custom_video.is_file():
        return custom_video

    if target_vid.is_file() and target_vid.stat().st_size > 500000:
        logger.info(f"base_video_cache_hit: [IDEMPOTENT SKIP] Reusing {target_vid.name} ($0.00 spend)")
        print(f"  [CACHE HIT] Reusing Wan 2.1 living base video: {target_vid.name} ($0.00 spend)")
        return target_vid

    img_path = output_dir / "character_singer_portrait.jpg"
    if not img_path.is_file():
        raise FileNotFoundError(f"Keyframe image not found at {img_path}")

    print("  [GENERATING] Generating 5s living base video via Alibaba Wan 2.1 ($0.40)...")
    adapter = FalWan21Adapter()
    _, saved_path = await adapter.generate_video(
        image_url=str(img_path),
        motion_prompt="The beautiful young woman listening to music on headphones gently sways head and shoulders to lo-fi beat, blinks softly, natural breathing.",
        output_path=target_vid,
        duration=5,
        force_live=True,
    )
    return saved_path


def split_song_timeline(total_dur: float, vocal_start: float = 18.0) -> List[Tuple[int, str, float, float, bool]]:
    """Compute natural 4-scene breakdown (Intro, Verse, Interlude, Chorus) with singing flags."""
    v_start = min(vocal_start, total_dur * 0.3)
    verse_end = min(total_dur * 0.55, v_start + 20.0)
    interlude_end = min(total_dur * 0.70, verse_end + 10.0)
    return [
        (1, "intro", 0.0, v_start, False),               # Instrumental intro: looped living motion ($0.00)
        (2, "verse_singing", v_start, verse_end, True),   # Vocal verse: LatentSync singing ($0.20)
        (3, "interlude", verse_end, interlude_end, False),# Flute solo: looped living motion ($0.00)
        (4, "chorus_singing", interlude_end, total_dur, True), # Vocal chorus: LatentSync singing ($0.20)
    ]


def slice_scene_audio(full_audio: Path, out_path: Path, start_s: float, end_s: float) -> Path:
    """Slice audio segment for a scene with local disk check."""
    if out_path.is_file() and out_path.stat().st_size > 2000:
        return out_path
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    dur = max(1.0, end_s - start_s)
    cmd = [
        ffmpeg_exe, "-y", "-nostats", "-loglevel", "error",
        "-ss", f"{start_s:.2f}", "-i", str(full_audio),
        "-t", f"{dur:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path


def loop_video_to_duration(input_video: Path, output_video: Path, target_dur: float) -> Path:
    """Seamlessly loop a living video base to target duration using local FFmpeg ($0.00 spend)."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-nostats", "-loglevel", "error",
        "-stream_loop", "-1", "-i", str(input_video),
        "-t", f"{target_dur:.2f}",
        "-c:v", "copy", "-an",
        str(output_video),
    ]
    subprocess.run(cmd, check=True)
    return output_video


async def produce_scene_clip_idempotent(
    base_video: Path,
    scene_audio: Path,
    out_video: Path,
    is_singing: bool,
    dur_sec: float,
) -> Path:
    """Synthesize or reuse a scene clip. Skips immediately if already present on disk."""
    if out_video.is_file() and out_video.stat().st_size > 50000:
        logger.info(f"scene_clip_cache_hit: [IDEMPOTENT SKIP] Reusing {out_video.name} ($0.00 spend)")
        print(f"  [CACHE HIT] Scene clip already exists: {out_video.name} ($0.00 spend)")
        return out_video

    # 1. Prepare duration-matched base video
    raw_looped = out_video.parent / f"raw_loop_{out_video.name}"
    loop_video_to_duration(base_video, raw_looped, dur_sec)

    if not is_singing:
        # Instrumental scene: living Wan motion with zero mouth movement ($0.00 spend)
        print(f"  [INSTRUMENTAL SCENE] Looping living motion for {out_video.name} ({dur_sec:.1f}s) ($0.00)...")
        raw_looped.replace(out_video)
        return out_video

    # Singing scene: apply ByteDance LatentSync ($0.20 flat)
    print(f"  [SINGING LIPSYNC] Applying ByteDance LatentSync for {out_video.name} ({dur_sec:.1f}s) ($0.20)...")
    adapter = FalLatentSyncAdapter()
    res = await adapter.lipsync_video(
        video_url=str(raw_looped),
        audio_path=scene_audio,
        output_path=out_video,
        force_live=True,
    )
    raw_looped.unlink(missing_ok=True)
    return Path(res)


def concatenate_and_master(scene_videos: List[Path], full_audio: Path, final_video: Path) -> Path:
    """Concatenate all scene clips and mux with the original 48kHz master audio track."""
    if final_video.is_file() and final_video.stat().st_size > 100000:
        logger.info(f"final_video_cache_hit: [IDEMPOTENT SKIP] Reusing {final_video.name} ($0.00 spend)")
        print(f"  [CACHE HIT] Final master video already complete: {final_video.name} ($0.00 spend)")
        return final_video

    print(f"  [MASTERING] Concatenating {len(scene_videos)} scenes & muxing with 48kHz master audio...")
    concat_txt = final_video.parent / "scene_concat_list.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in scene_videos), encoding="utf-8")

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-nostats", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(full_audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", str(final_video),
    ]
    subprocess.run(cmd, check=True)
    return final_video


async def run_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("\n🎵 Starting Idempotent Telugu Lo-Fi Music Video Pipeline")
    print(f"📁 Output Directory: {out_dir}")
    print("🛡️ Idempotency Mandate: Active (All completed artifacts skipped at $0.00)\n")

    # 1. Master Audio
    audio_path = await produce_lofi_song_idempotent(out_dir, Path(args.audio) if args.audio else None, args.topic)
    total_dur = args.duration or get_media_duration(audio_path) or 72.0
    print(f"✅ Master Audio Track: {audio_path.name} ({total_dur:.1f}s)")

    # 2. Living Base Video
    base_video = await produce_living_base_video_idempotent(out_dir, Path(args.video) if args.video else None)
    print(f"✅ Living Character Base: {base_video.name}\n")

    # 3. Timeline
    timeline = split_song_timeline(total_dur, vocal_start=args.vocal_start)
    print("🎬 Song Scenes Split (Instrumental vs Singing):")
    for idx, name, start, end, is_sing in timeline:
        tag = "🎤 Singing Lip-Sync (LatentSync $0.20)" if is_sing else "🎧 Instrumental Sway (Local Loop $0.00)"
        print(f"   - Scene {idx} [{name}]: {start:.1f}s - {end:.1f}s ({end-start:.1f}s) • {tag}")
    print()

    # 4. Generate/Reuse Scenes Idempotently
    scene_videos: List[Path] = []
    for idx, name, start, end, is_sing in timeline:
        dur = end - start
        sc_audio = slice_scene_audio(audio_path, out_dir / f"scene_{idx}_{name}.mp3", start, end)
        sc_video = out_dir / f"scene_{idx}_{name}.mp4"
        animated = await produce_scene_clip_idempotent(base_video, sc_audio, sc_video, is_sing, dur)
        scene_videos.append(animated)

    # 5. Concatenate & Master
    final_video = out_dir / "master_4k_lofi_music_video.mp4"
    master_video = concatenate_and_master(scene_videos, audio_path, final_video)

    print(f"\n🎉 100% Complete & Broadcast Ready: {master_video.name}")
    print(f"📁 Output Path: {master_video}")
    print(f"⏱️ Finished in {time.time() - t0:.2f}s\n")

    return {"status": "success", "master_video": str(master_video)}


def main():
    parser = argparse.ArgumentParser(description="Idempotent Telugu Lo-Fi Music Video Generator (Zero Local GPU)")
    parser.add_argument("--topic", default="Oka Brundavanam Telugu Lo-Fi", help="Song topic or theme")
    parser.add_argument("--vocal-start", type=float, default=18.0, help="Seconds when singing starts (default: 18.0)")
    parser.add_argument("--duration", type=float, default=72.0, help="Total duration in seconds")
    parser.add_argument("--audio", default=None, help="Optional pre-existing audio track path")
    parser.add_argument("--video", default=None, help="Optional pre-existing living base video path")
    parser.add_argument("--output-dir", default="storage/tests/lofi_singer_test", help="Output directory")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
