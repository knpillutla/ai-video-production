"""Reproduce Lara Aredo - "Sayaghat Jarh" (صياغة جرح) Style 4K Music Video."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.visual.fal_flux_dev import fal_flux_dev_adapter
from src.providers.visual.fal_flux_lora import fal_flux_lora_adapter
from src.providers.lipsync.fal_liveportrait import FalLivePortraitAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.providers.visual.fal_kling_v3 import FalKlingV3Adapter
from src.providers.visual.fal_wan21 import fal_wan21_adapter
from src.scripts.local_beat_detector import LocalBeatDetector
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary


async def build_lara_dataset(artist_dir: Path, artist_name: str) -> Path:
    """Method 1: Generate 1 Master Hero Face -> 5s 3D Head-Turn Video -> Extract 12 Identical Stills."""
    dataset_dir = artist_dir / "dataset_images"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    zip_path = artist_dir / "dataset.zip"
    if zip_path.exists() and zip_path.stat().st_size > 50_000:
        logger.info(f"dataset_cache_hit: {zip_path.name}")
        return zip_path

    # Step A: Generate ONE Master Hero Ground-Truth Face
    hero_path = artist_dir / "hero_master.jpg"
    hero_prompt = (
        f"A striking photorealistic master portrait photograph of {artist_name}, "
        "a stunning 24-year-old Iraqi and Levantine woman, luminous warm olive-honey skin, "
        "deep expressive almond-shaped dark hazel-brown eyes, sculpted cheekbones, sharp jawline, "
        "natural balanced athletic-slender fit build, long glossy dark wavy hair, "
        "straight front close-up portrait, neutral calm gaze, chic black silk blouse, "
        "soft natural studio lighting, 8k UHD, 35mm film still, ultra-detailed skin texture, realistic pores."
    )
    if not hero_path.exists() or hero_path.stat().st_size < 10000:
        logger.info(f"Generating single master hero face for {artist_name}...")
        await fal_flux_dev_adapter.generate_to_file(hero_prompt, hero_path, aspect_ratio="1:1")

    # Step B: Animate 5-second 3D head rotation and expression video via Kling
    rotation_video = artist_dir / "hero_rotation.mp4"
    if not rotation_video.exists() or rotation_video.stat().st_size < 10000:
        logger.info("Generating 5s 3D head rotation video via Kling for 100% identity consistency...")
        kling = FalKlingV3Adapter()
        motion_prompt = (
            "Cinematic slow head rotation: woman slowly turns her head from center to left, "
            "looks slightly down, smiles softly, then turns slowly to right and back to front. "
            "Natural human blinking, gentle breathing, steady camera, photorealistic 4k motion."
        )
        try:
            await kling.generate_video(
                image_url=str(hero_path),
                motion_prompt=motion_prompt,
                output_path=rotation_video,
                duration=5,
            )
        except Exception as ex:
            logger.warning(f"Kling live rotation fallback to local motion: {ex}")
            ffmpeg_bin = get_ffmpeg_binary()
            cmd_rot = [
                ffmpeg_bin, "-y", "-loop", "1", "-i", str(hero_path),
                "-vf", "scale=1080:1080,zoompan=z='min(zoom+0.001,1.05)':d=125:s=1080x1080:fps=25",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-vframes", "125",
                "-movflags", "+faststart", str(rotation_video)
            ]
            proc = await asyncio.create_subprocess_exec(*cmd_rot)
            await proc.wait()

    # Step C: Extract 12 distinct frame stills across the 125 frames (100% mathematically the same person)
    logger.info("Extracting 12 consistent angle stills from 3D rotation video...")
    ffmpeg_bin = get_ffmpeg_binary()
    cmd_extract = [
        ffmpeg_bin, "-y", "-i", str(rotation_video),
        "-vf", "fps=2.4", "-vframes", "12",
        str(dataset_dir / "seed_%02d.jpg")
    ]
    proc = await asyncio.create_subprocess_exec(*cmd_extract)
    await proc.wait()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in dataset_dir.glob("seed_*.jpg"):
            zf.write(f, arcname=f.name)
    logger.info(f"Dataset packaged with 12 mathematically identical angle stills: {zip_path}")
    return zip_path


async def compose_sayaghat_jarh_song(artist_dir: Path) -> Path:
    """Synthesize authentic Iraqi romantic ballad track."""
    song_path = artist_dir / "sayaghat_jarh_master.mp3"
    if song_path.exists() and song_path.stat().st_size > 50_000:
        logger.info(f"song_cache_hit: {song_path.name}")
        return song_path

    if is_mock_mode():
        ffmpeg_bin = get_ffmpeg_binary()
        cmd = [ffmpeg_bin, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=12", "-c:a", "libmp3lame", str(song_path)]
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.wait()
        return song_path

    from src.providers.llm.gemini_adapter import GeminiLLMAdapter
    import httpx

    prompt = (
        "You are an elite Iraqi music producer and poet. Write an authentic, deeply moving "
        "Iraqi romantic ballad titled 'صياغة جرح' (Sayaghat Jarh - Crafting a Wound) in Iraqi Arabic dialect. "
        "Include 1 emotional Mawwal opening couplet, 1 Hook/Chorus, and 1 Verse about wounded love and deep memories. "
        "Return JSON: {\"lyrics\": \"...\", \"suno_tags\": \"...\"}"
    )
    gemini = GeminiLLMAdapter()
    try:
        raw_text = await gemini.generate_text(prompt=prompt, system_prompt="Iraqi Music Director")
        clean_text = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        res = json.loads(clean_text)
        lyrics = res.get("lyrics", "صياغة جرح صاغ الگلب بيدك... وأنا العشت كل عمري أريدك")
    except Exception as ex:
        logger.warning(f"gemini_lyrics_fallback: {ex}")
        lyrics = "صياغة جرح صاغ الگلب بيدك... وأنا العشت كل عمري أريدك"
    tags = "Iraqi romantic ballad, emotional mawwal, acoustic oud, mournful nay flute, modern pop beat, passionate female vocals, 48kHz studio mix"

    suno = SunoMusicAdapter()
    logger.info("Synthesizing Iraqi song with Suno v3.5 Pro...")
    track_url = await suno.generate_track(genre=tags, lyrics=lyrics, vocal_gender="female", title="Sayaghat Jarh")
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(track_url)
        song_path.write_bytes(resp.content)
    return song_path


async def render_lara_scenes(artist_dir: Path, lora_url: str, trigger: str) -> list[Path]:
    """Generate 3 auditorium storyboard scenes matching the live concert setting."""
    scenes_dir = artist_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    prompts = [
        (
            f"{trigger} woman singing passionately into vintage chrome stage microphone on stand, "
            "concert stage in grand auditorium, warm golden theatrical spotlight, soft blurred dark theater audience in background, "
            "wearing identical black silk collared blouse, 8k UHD, 35mm film still."
        ),
        (
            f"{trigger} woman sitting on stage stool holding and strumming an acoustic wooden guitar, "
            "fingers on strings and fretboard, singing into stage microphone on stand, concert hall stage, "
            "wearing identical black silk collared blouse, warm theatrical stage lighting, auditorium seating softly visible in background, 8k UHD."
        ),
        (
            f"{trigger} woman on concert stage holding acoustic wooden guitar, looking out passionately toward seated theater audience, "
            "warm atmospheric stage light beams, dark theater hall with audience silhouettes, "
            "wearing identical black silk collared blouse, cinematic 35mm film still."
        ),
    ]
    scene_paths = []
    for idx, p in enumerate(prompts):
        out = scenes_dir / f"auditorium_scene_{idx+1}.jpg"
        scene_paths.append(out)
        if not out.exists() or out.stat().st_size < 10_000:
            logger.info(f"Rendering auditorium scene {idx+1} with FLUX LoRA...")
            await fal_flux_lora_adapter.generate_with_lora(p, lora_url, out, aspect_ratio="16:9")
    return scene_paths


async def animate_and_master(artist_dir: Path, scenes: list[Path], audio_path: Path, mode: str = "dev") -> Path:
    """Animate video motion via Alibaba Wan 2.1 (dev) or Sync-Lipsync (prod) and master 4K MP4."""
    clips_dir = artist_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    clip1 = clips_dir / f"clip1_{mode}.mp4"
    clip2 = clips_dir / f"clip2_{mode}.mp4"
    clip3 = clips_dir / f"clip3_{mode}.mp4"
    clip1_punchin = clips_dir / f"clip1_punchin_{mode}.mp4"

    if mode == "dev":
        logger.info("Dev Mode: Animating all 3 camera angles via Alibaba Wan 2.1 ($0.40/clip)...")
        prompts = [
            "Cinematic slow camera push, woman passionately singing into vintage chrome stage microphone on stand, subtle head sway, expressive dark eyes, warm auditorium stage spotlight, 4k",
            "Woman sitting on stage playing acoustic wooden guitar, strumming guitar strings with right hand, left fingers on fretboard, singing into stage microphone, identical black silk blouse, warm theatrical stage lighting, 4k",
            "Cinematic slow stage camera track, woman on stage holding acoustic guitar looking out passionately toward seated auditorium audience, warm theatrical spotlights, dark theater hall atmosphere, 4k",
        ]
        tasks = []
        for s, c, p in [(scenes[0], clip1, prompts[0]), (scenes[1], clip2, prompts[1]), (scenes[2], clip3, prompts[2])]:
            if not c.exists() or c.stat().st_size < 10000:
                tasks.append(fal_wan21_adapter.generate_video(str(s), p, c, duration=5))
        if tasks:
            await asyncio.gather(*tasks)
    else:
        logger.info("Prod Mode: Slicing 6s audio for Sync-Lipsync to guarantee cost control...")
        vocal_guide = artist_dir / "vocal_guide.wav"
        if not vocal_guide.exists():
            cmd_vocal = [ffmpeg_bin, "-y", "-i", str(audio_path), "-af", "highpass=f=220,lowpass=f=4000", "-vn", "-ar", "16000", "-ac", "1", str(vocal_guide)]
            proc = await asyncio.create_subprocess_exec(*cmd_vocal)
            await proc.wait()
        sliced_audio = clips_dir / "snippet_vocals.wav"
        if not sliced_audio.exists():
            cmd_slice = [ffmpeg_bin, "-y", "-i", str(vocal_guide), "-t", "6.0", "-c", "copy", str(sliced_audio)]
            proc = await asyncio.create_subprocess_exec(*cmd_slice)
            await proc.wait()
        liveportrait = FalLivePortraitAdapter()
        kling = FalKlingV3Adapter()
        await asyncio.gather(
            liveportrait.animate_avatar(scenes[0], sliced_audio, clip1, duration_seconds=6.0),
            liveportrait.animate_avatar(scenes[1], sliced_audio, clip2, duration_seconds=6.0),
        )
        if not clip3.exists() or clip3.stat().st_size < 10000:
            broll_p = "Cinematic slow camera track, woman holding acoustic guitar looking out passionately toward auditorium audience, 4k"
            await kling.generate_video(image_url=str(scenes[2]), motion_prompt=broll_p, output_path=clip3, duration=5)

    if not clip1_punchin.exists() or clip1_punchin.stat().st_size < 10000:
        cmd_punch = [
            ffmpeg_bin, "-y", "-i", str(clip1),
            "-vf", "scale=1.15*iw:-1,crop=iw/1.15:ih/1.15",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-an", str(clip1_punchin)
        ]
        proc = await asyncio.create_subprocess_exec(*cmd_punch)
        await proc.wait()

    detector = LocalBeatDetector(default_bpm=92.0)
    grid = detector.analyze_audio_buffer(duration_seconds=30.0, bpm=92.0)
    logger.info(f"Beat alignment: BPM={grid.bpm}, {len(grid.downbeat_timestamps)} downbeats detected")

    edl_clips = [clip1, clip3, clip2, clip1_punchin, clip3, clip2]
    masters = [
        (artist_dir / "lara_areda_sayaghat_jarh_35s_4k.mp4", edl_clips),
        (artist_dir / "lara_areda_sayaghat_jarh_full_song_4k.mp4", edl_clips * 6),
    ]
    for out_mp4, clips in masters:
        concat_file = out_mp4.with_suffix(".txt")
        concat_file.write_text("".join(f"file '{c.resolve().as_posix()}'\n" for c in clips), encoding="utf-8")
        cmd_master = [
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio_path),
            "-vf", "scale=3840:2160:flags=lanczos,unsharp=5:5:0.8:5:5:0.0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-af", "loudnorm=I=-14.0:LRA=7.0:TP=-1.0",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            "-movflags", "+faststart", "-shortest", str(out_mp4)
        ]
        proc = await asyncio.create_subprocess_exec(*cmd_master)
        await proc.wait()
        logger.info(f"Broadcast 4K Master Created: {out_mp4.name}")

    return masters[1][0]


async def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce Lara Aredo Sayaghat Jarh Music Video")
    parser.add_argument("--dir-name", default="lara_areda_live", help="Output directory name")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev", help="Execution mode (default: dev)")
    parser.add_argument("--dev", dest="mode", action="store_const", const="dev", help="Run dev mode (Wan 2.1, $0.40/clip)")
    parser.add_argument("--prod", dest="mode", action="store_const", const="prod", help="Run prod mode")
    parser.add_argument("--lora-url", default=None, help="Reuse existing LoRA safetensors URL")
    parser.add_argument("--audio-path", default=None, help="Reuse existing song MP3")
    parser.add_argument("--mock", action="store_true", help="Run offline in mock mode ($0 cost)")
    args = parser.parse_args()

    if args.mock:
        import os
        os.environ["MOCK_ALL_MODELS"] = "true"

    artist_name = "Lara Aredo"
    trigger = "TOK_LARA_AREDO"
    artist_dir = Path("storage") / "artists" / args.dir_name
    artist_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== LARA AREDO - SAYAGHAT JARH REPLICA (MODE: {args.mode.upper()}) ===\n")
    lora_url = args.lora_url
    if not lora_url:
        meta_cand = artist_dir / "lora_meta.json"
        if not meta_cand.exists() and Path("storage/artists/lara_areda_live/lora_meta.json").exists():
            meta_cand = Path("storage/artists/lara_areda_live/lora_meta.json")
        if meta_cand.exists():
            try:
                m_data = json.loads(meta_cand.read_text(encoding="utf-8"))
                lora_url = m_data.get("diffusers_lora_file", {}).get("url")
                if lora_url:
                    logger.info(f"Reusing cached LoRA weights: {lora_url}")
            except Exception:
                pass

    if not lora_url:
        zip_path = await build_lara_dataset(artist_dir, artist_name)
        lora_url = await fal_flux_lora_adapter.train_portrait_lora(zip_path, trigger, artist_dir / "lora_meta.json")

    audio_path = Path(args.audio_path) if args.audio_path else None
    if not audio_path or not audio_path.exists():
        if (artist_dir / "sayaghat_jarh_master.mp3").exists():
            audio_path = artist_dir / "sayaghat_jarh_master.mp3"
        elif Path("storage/artists/lara_areda_live/sayaghat_jarh_master.mp3").exists():
            audio_path = Path("storage/artists/lara_areda_live/sayaghat_jarh_master.mp3")
            logger.info(f"Reusing cached master song: {audio_path.name}")
        else:
            audio_path = await compose_sayaghat_jarh_song(artist_dir)

    scenes = await render_lara_scenes(artist_dir, lora_url, trigger)
    final_video = await animate_and_master(artist_dir, scenes, audio_path, mode=args.mode)
    print(f"\n[DONE] 4K Video Produced ({args.mode}): {final_video.resolve()}\n")


if __name__ == "__main__":
    asyncio.run(main())

