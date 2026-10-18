"""Gemini Master Director: Telugu Lo-Fi Live Concert Video Producer.

Pipeline:
1. Gemini 1.5 Pro: Directorial script, Telugu lyrics, timestamps, gestures.
2. Suno v3.5: Authentic Telugu Lo-Fi acoustic master audio generation.
3. Fal Wan 2.1 / Z-Image: Multi-camera angles (Lead Singer, Guitar, Wide).
4. Sync Labs: Smart selective lip-sync strictly for active vocal scenes.
5. Local FFmpeg: Beat-aligned multi-camera assembly & 48kHz stereo master mux.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
import imageio_ffmpeg
from scripts.concert_prompts import (
    DIRECTOR_PROMPT,
    GUITAR_KEYFRAME_PROMPT,
    GUITAR_MOTION_PROMPT,
    SINGER_KEYFRAME_PROMPT,
    SINGER_MOTION_PROMPT,
)
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.providers.llm.gemini_adapter import GeminiLLMAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter

OUTPUT_DIR = Path("storage/productions/telugu_lofi_concert").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def confirm_step(step_name: str, model_name: str, calls: int, cost: str, auto_approve: bool = False):
    print("\n" + "=" * 65)
    print(f"📋 PRE-FLIGHT CONFIRMATION: {step_name}")
    print(f"🤖 Target Model:    {model_name}")
    print(f"🔢 Total API Calls:  {calls} call(s)")
    print(f"💰 Estimated Cost:   {cost}")
    print("=" * 65)
    if not auto_approve and os.getenv("AUTO_APPROVE") != "1":
        ans = input(f"Proceed with {step_name} [{model_name}]? [Y/n]: ").strip().lower()
        if ans in ("n", "no"):
            print("❌ Step cancelled by user.")
            sys.exit(0)


async def step1_gemini_direct(out_file: Path) -> Dict[str, Any]:
    if out_file.is_file() and out_file.stat().st_size > 500:
        print(f"  [CACHE HIT] Reusing Gemini script: {out_file.name}")
        return json.loads(out_file.read_text(encoding="utf-8"))

    print("🤖 Calling Gemini 1.5 Pro to direct song, lyrics, gestures, and storyboard...")
    gemini = GeminiLLMAdapter()
    body = {
        "contents": [{"parts": [{"text": DIRECTOR_PROMPT}]}],
        "generationConfig": {"temperature": 0.4, "response_mime_type": "application/json"},
    }
    resp = await gemini._post_with_retry(body, timeout=120.0)
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    script_data = json.loads(text)
    out_file.write_text(json.dumps(script_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✅ Gemini Directorial Script saved: {out_file.name} ({len(script_data.get('scenes', []))} scenes)")
    return script_data


async def step2_suno_song(script: Dict[str, Any], out_mp3: Path) -> Path:
    if out_mp3.is_file() and out_mp3.stat().st_size > 500000:
        print(f"  [CACHE HIT] Reusing Suno master audio: {out_mp3.name}")
        return out_mp3

    print(f"🎵 Calling Suno v3.5 to synthesize: '{script.get('title')}'...")
    suno = SunoMusicAdapter()
    url = await suno.generate_track(
        genre=script.get("suno_tags", "telugu lofi acoustic"),
        lyrics=script.get("lyrics", ""),
        title=script.get("title", "Telugu Lo-Fi Live"),
        vocal_gender="female",
    )
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        out_mp3.write_bytes(resp.content)
    print(f"  ✅ Suno master audio downloaded: {out_mp3.name} ({out_mp3.stat().st_size / 1024:.1f} KB)")
    return out_mp3


async def step3_generate_angle(keyframe_prompt: str, motion_prompt: str, base_name: str, fal_key: str) -> Path:
    img_path = OUTPUT_DIR / f"{base_name}_keyframe.png"
    vid_path = OUTPUT_DIR / f"{base_name}_5s.mp4"
    if vid_path.is_file() and vid_path.stat().st_size > 500000:
        return vid_path

    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    if not img_path.is_file():
        print(f"  📸 Generating keyframe for {base_name} via Z-Image ($0.01)...")
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(
                "https://queue.fal.run/fal-ai/fast-turbo-diffusion",
                headers=headers,
                json={"prompt": keyframe_prompt, "image_size": "landscape_16_9"},
            )
            data = r.json()
            for _ in range(40):
                await asyncio.sleep(2.0)
                st = (await c.get(data["status_url"], headers=headers)).json()
                if st.get("status") == "COMPLETED":
                    res = (await c.get(data["response_url"], headers=headers)).json()
                    img_path.write_bytes((await c.get(res["images"][0]["url"])).content)
                    break

    img_fal_url = await upload_to_fal(img_path, fal_key)
    print(f"  🎬 Generating 5s living motion for {base_name} via Wan 2.1 ($0.40)...")
    from src.providers.visual.fal_wan21 import FalWan21Adapter
    adapter = FalWan21Adapter()
    await adapter.generate_video(img_fal_url, motion_prompt, vid_path, duration=5.0)
    return vid_path


def slice_clip(in_f: Path, out_f: Path, start: float, dur: float, is_video: bool = False) -> Path:
    if out_f.is_file() and out_f.stat().st_size > 5000:
        return out_f
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if is_video:
        cmd = [ffmpeg, "-y", "-nostats", "-loglevel", "error", "-stream_loop", "-1", "-i", str(in_f), "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-r", "30", "-pix_fmt", "yuv420p", "-an", str(out_f)]
    else:
        cmd = [ffmpeg, "-y", "-nostats", "-loglevel", "error", "-ss", f"{start:.2f}", "-i", str(in_f), "-t", f"{dur:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", str(out_f)]
    subprocess.run(cmd, check=True)
    return out_f


async def call_sync_labs(image_path: Path, audio_path: Path, out_path: Path, fal_key: str) -> Path:
    if out_path.is_file() and out_path.stat().st_size > 50000:
        print(f"  [CACHE HIT] Reusing Sync Labs clip: {out_path.name}")
        return out_path

    print(f"🎤 Calling Sync Labs ({out_path.name}) at $0.1333/sec...")
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    img_url = await upload_to_fal(image_path, fal_key)
    aud_url = await upload_to_fal(audio_path, fal_key)
    payload = {"image_url": img_url, "audio_url": aud_url, "sync_mode": "cut_off"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post("https://queue.fal.run/fal-ai/sync-lipsync/v3/image-to-video", headers=headers, json=payload)
        data = resp.json()
        for attempt in range(80):
            await asyncio.sleep(3.0)
            st = (await client.get(data["status_url"], headers=headers)).json()
            if st.get("status") == "COMPLETED":
                res = (await client.get(data["response_url"], headers=headers)).json()
                v_url = res.get("video", {}).get("url") or res.get("video_url")
                out_path.write_bytes((await client.get(v_url, timeout=60.0)).content)
                print(f"  ✅ Sync Labs vocal clip downloaded: {out_path.name}")
                return out_path
            if attempt % 5 == 0:
                print(f"    ⏳ Sync Labs rendering... ({attempt*3}s)")
    raise TimeoutError("Sync Labs timed out")


def assemble_final_master(cuts: List[Path], master_audio: Path, out_master: Path) -> Path:
    print(f"\n🎬 Assembling final concert video ({len(cuts)} cuts) & 48kHz stereo master...")
    concat_txt = out_master.parent / "final_concat_list.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in cuts), encoding="utf-8")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(master_audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart",
        str(out_master),
    ]
    subprocess.run(cmd, check=True)
    return out_master


async def main():
    parser = argparse.ArgumentParser(description="Gemini-Directed Telugu Lo-Fi Concert Video Producer")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4, 5], help="Run a specific production step")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve steps without interactive prompt")
    args = parser.parse_args()

    fal_key = _fal_api_key()
    auto = args.auto_approve
    t0 = time.time()
    print("=====================================================================")
    print("🎬 GEMINI MASTER DIRECTOR: Fresh Telugu Lo-Fi Concert Video")
    print("=====================================================================\n")

    # Step 1: Gemini Directorial Script & Lyrics
    if args.step in (None, 1):
        confirm_step("Step 1: Directorial Scriptwriting & Lyrics", "Google Gemini 1.5 Pro (Flash)", 1, "~$0.01", auto)
        script = await step1_gemini_direct(OUTPUT_DIR / "director_script.json")
    else:
        script = json.loads((OUTPUT_DIR / "director_script.json").read_text(encoding="utf-8"))

    # Step 2: Suno Audio Synthesis
    if args.step in (None, 2):
        confirm_step("Step 2: Soundtrack Synthesis", "Suno v3.5 Pro (MusicAPI.ai)", 1, "~$0.30", auto)
        master_audio = await step2_suno_song(script, OUTPUT_DIR / "master_song.mp3")
    else:
        master_audio = OUTPUT_DIR / "master_song.mp3"

    # Step 3: Base Multi-Camera Visual Angles (Wan 2.1)
    if args.step in (None, 3):
        confirm_step("Step 3: Multi-Angle Visual Generation", "Fal Z-Image ($0.01x2) + Alibaba Wan 2.1 ($0.40x2)", 4, "~$0.82", auto)
        singer_vid = await step3_generate_angle(SINGER_KEYFRAME_PROMPT, SINGER_MOTION_PROMPT, "angle_lead_singer", fal_key)
        guitar_vid = await step3_generate_angle(GUITAR_KEYFRAME_PROMPT, GUITAR_MOTION_PROMPT, "angle_guitar", fal_key)
    else:
        singer_vid = OUTPUT_DIR / "angle_lead_singer_5s.mp4"
        guitar_vid = OUTPUT_DIR / "angle_guitar_5s.mp4"

    # Step 4: Scene Slicing & Smart Lip-Sync Routing
    cuts: List[Path] = []
    singer_keyframe = OUTPUT_DIR / "angle_lead_singer_keyframe.png"
    vocal_scenes = [sc for sc in script.get("scenes", []) if sc.get("is_vocal")]
    vocal_dur_total = sum(float(sc["duration_s"]) for sc in vocal_scenes)

    if args.step in (None, 4):
        confirm_step(f"Step 4: Smart Vocal Lip-Sync ({len(vocal_scenes)} vocal scenes, {vocal_dur_total:.1f}s)", "Sync Labs (sync-lipsync/v3/image-to-video)", len(vocal_scenes), f"~${vocal_dur_total * 0.1333:.2f}", auto)
        for sc in script.get("scenes", []):
            sc_id = sc["scene_id"]
            start_s, dur_s = float(sc["start_s"]), float(sc["duration_s"])
            is_vocal = bool(sc.get("is_vocal", False))
            audio_clip = slice_clip(master_audio, OUTPUT_DIR / f"audio_sc{sc_id}.mp3", start_s, dur_s, is_video=False)

            if not is_vocal:
                vid_clip = slice_clip(guitar_vid, OUTPUT_DIR / f"video_sc{sc_id}_guitar.mp4", 0.0, dur_s, is_video=True)
                cuts.append(vid_clip)
            else:
                lipsync_clip = await call_sync_labs(singer_keyframe, audio_clip, OUTPUT_DIR / f"video_sc{sc_id}_synclabs.mp4", fal_key)
                cuts.append(lipsync_clip)
    else:
        for sc in script.get("scenes", []):
            sc_id = sc["scene_id"]
            cuts.append(OUTPUT_DIR / (f"video_sc{sc_id}_synclabs.mp4" if sc.get("is_vocal") else f"video_sc{sc_id}_guitar.mp4"))

    # Step 5: Multi-Camera Assembly & Master Export
    if args.step in (None, 5):
        confirm_step("Step 5: Multi-Camera Concat & 48kHz Stereo Master Mux", "Local Single-Pass FFmpeg (CPU)", 0, "$0.00", auto)
        master_video = assemble_final_master(cuts, master_audio, OUTPUT_DIR / "master_fresh_telugu_concert.mp4")
        elapsed = time.time() - t0
        size_mb = master_video.stat().st_size / (1024 * 1024)
        print(f"\n🎉 MASTER VIDEO COMPLETE! ({elapsed:.1f}s, {size_mb:.2f} MB): {master_video}")


if __name__ == "__main__":
    asyncio.run(main())
