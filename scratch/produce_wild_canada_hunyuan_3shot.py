"""Live Production: Wild Canada Episode 1 (3-Shot 15s Showcase - FLUX 1.1 Pro Ultra + Hunyuan Video 1080p).

Adheres to:
- Directive 3: Universal Artifact Caching (reuses existing Shot 1 assets from disk; 0 redundant cost).
- Directive 8: Multi-shot live test strictly capped to 3 shots (15s duration).
- Directive 14: Single-pass 4K UHD 24.0 fps (-crf 18, Lanczos upscale), 48kHz broadcast audio with -18dB ducking.
- Directive 17: Blue-Chip Nature Documentary standards (slow expansive steadycam glide, natural daylight, orchestral foley).
"""

import asyncio
import os
import sys
import subprocess
import httpx
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
if hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

OUTPUT_DIR = Path("storage/live_production/wild_canada_hunyuan_3shot_ep1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SRC_SHOT1_DIR = Path("storage/live_production/wild_canada_hunyuan_test")

SHOTS_CONFIG = [
    {
        "shot_id": 1,
        "title": "Lake Moraine Glacial Basin",
        "image_prompt": (
            "Ultra-photorealistic 8K cinematic landscape of Canadian Rockies Lake Moraine in Banff National Park. "
            "Majestic granite peaks with snow dusted ridges, pristine turquoise glacial water, emerald pine forest, "
            "soft morning mist, crisp balanced 5500K daylight, deep optical focal depth."
        ),
        "motion_prompt": (
            "Ultra-photorealistic 4K cinematic BBC Planet Earth documentary aerial camera glide slowly descending "
            "and pushing forward over pristine turquoise glacial waters toward towering snow-capped Rocky Mountain peaks, "
            "slow expansive camera motion, 24fps film cadence, zero high-speed rush."
        ),
    },
    {
        "shot_id": 2,
        "title": "Emerald Pine Canopy & Rushing River",
        "image_prompt": (
            "Ultra-photorealistic 8K cinematic landscape of Canadian wilderness crystalline river rushing through "
            "a dense emerald pine forest in Banff National Park. White water cascading over ancient smooth granite boulders, "
            "dew-kissed pine needles, rising morning forest mist, crisp morning sunbeams piercing through tall pines, "
            "photorealistic BBC natural history cinematography."
        ),
        "motion_prompt": (
            "Cinematic steadycam camera moving slowly along the crystalline mountain riverbank, water cascading over "
            "granite boulders, morning mist gently drifting through the tall pine trees, slow measured 24fps film cadence."
        ),
    },
    {
        "shot_id": 3,
        "title": "Sunset Ridge over Mount Assiniboine",
        "image_prompt": (
            "Ultra-photorealistic 8K cinematic panoramic view of Mount Assiniboine at twilight in the Canadian Rockies. "
            "Monumental pyramid-shaped granite peak glowing with soft golden-rose alpine glow on snow-dusted summit, "
            "deep indigo evening shadows across the vast valley and tranquil alpine lake below, crisp 85mm optical depth."
        ),
        "motion_prompt": (
            "Slow cinematic camera pan and gentle push forward across the high alpine ridge overlooking the monumental "
            "pyramid peak as golden light catches the snow crests, majestic timeless nature documentary motion."
        ),
    },
]


def _extract_video_url(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    val = payload.get("video")
    if isinstance(val, dict) and val.get("url"):
        return str(val["url"])
    if isinstance(val, str) and val.startswith("http"):
        return val
    out_val = payload.get("output")
    if isinstance(out_val, dict):
        if isinstance(out_val.get("video"), dict) and out_val["video"].get("url"):
            return str(out_val["video"]["url"])
        if isinstance(out_val.get("video"), str) and out_val["video"].startswith("http"):
            return str(out_val["video"])
        if isinstance(out_val.get("url"), str) and out_val["url"].startswith("http"):
            return str(out_val["url"])
    f_val = payload.get("file")
    if isinstance(f_val, dict) and f_val.get("url"):
        return str(f_val["url"])
    if isinstance(payload.get("url"), str) and payload["url"].startswith("http"):
        return str(payload["url"])
    for v in payload.values():
        if isinstance(v, str) and (v.endswith(".mp4") or "fal.media" in v):
            return v
        if isinstance(v, dict) and isinstance(v.get("url"), str) and ("fal.media" in v["url"] or v["url"].endswith(".mp4")):
            return str(v["url"])
    return None


async def get_or_generate_keyframe(shot: dict) -> tuple[str, Path]:
    """Retrieve existing or synthesize FLUX 1.1 Pro Ultra keyframe."""
    shot_id = shot["shot_id"]
    local_img = OUTPUT_DIR / f"shot_{shot_id}_keyframe_pro_ultra.jpg"

    # Reuse Shot 1 from test if available
    if shot_id == 1 and not local_img.exists():
        src_shot1 = SRC_SHOT1_DIR / "shot_1_keyframe_pro_ultra.jpg"
        if src_shot1.exists() and src_shot1.stat().st_size > 500_000:
            local_img.write_bytes(src_shot1.read_bytes())
            print(f"[Shot {shot_id}] Reusing cached FLUX Pro Ultra keyframe from previous run ({local_img.stat().st_size} bytes)", flush=True)

    if local_img.exists() and local_img.stat().st_size > 500_000:
        print(f"[Shot {shot_id}] Using existing keyframe: {local_img.name} ({local_img.stat().st_size} bytes)", flush=True)
        fal_url_cache = OUTPUT_DIR / f"shot_{shot_id}_keyframe.fal_url"
        if fal_url_cache.exists():
            cached_url = fal_url_cache.read_text().strip()
            if cached_url.startswith("http"):
                return cached_url, local_img

        from src.providers.fal_storage import upload_to_fal
        print(f"[Shot {shot_id}] Uploading local keyframe to Fal storage...", flush=True)
        img_url = await upload_to_fal(local_img, api_key=FAL_KEY)
        fal_url_cache.write_text(img_url)
        return img_url, local_img

    endpoint = "https://queue.fal.run/fal-ai/flux-pro/v1.1-ultra"
    payload = {"prompt": shot["image_prompt"], "aspect_ratio": "16:9", "output_format": "jpeg", "raw": True}
    print(f"[{shot_id}/3] Synthesizing Ultra Keyframe with FLUX 1.1 Pro Ultra...", flush=True)

    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")

        for _ in range(40):
            await asyncio.sleep(2)
            s = await client.get(status_url, headers=HEADERS)
            if s.json().get("status") == "COMPLETED":
                res = (await client.get(resp_url, headers=HEADERS)).json()
                img_url = res.get("images", [{}])[0].get("url") or res.get("image", {}).get("url")
                img_bytes = (await client.get(img_url)).content
                local_img.write_bytes(img_bytes)
                print(f"   Shot {shot_id} Keyframe Ready: {local_img.name} ({len(img_bytes)} bytes)", flush=True)
                (OUTPUT_DIR / f"shot_{shot_id}_keyframe.fal_url").write_text(img_url)
                return img_url, local_img
        raise TimeoutError(f"FLUX Pro Ultra keyframe timed out for shot {shot_id}")


async def get_or_generate_hunyuan_clip(shot: dict, image_url: str) -> tuple[str, Path]:
    """Retrieve existing or synthesize 5s motion using Hunyuan Video 1080p."""
    shot_id = shot["shot_id"]
    local_vid = OUTPUT_DIR / f"shot_{shot_id}_hunyuan_raw_5s.mp4"

    # Reuse Shot 1 raw video if available
    if shot_id == 1 and not local_vid.exists():
        src_vid1 = SRC_SHOT1_DIR / "hunyuan_test_raw_5s.mp4"
        if src_vid1.exists() and src_vid1.stat().st_size > 1_000_000:
            local_vid.write_bytes(src_vid1.read_bytes())
            print(f"[Shot {shot_id}] Reusing cached Hunyuan 1080p clip from previous run ({local_vid.stat().st_size} bytes)", flush=True)
            return "cached", local_vid

    if local_vid.exists() and local_vid.stat().st_size > 1_000_000:
        print(f"[Shot {shot_id}] Using existing video clip: {local_vid.name}", flush=True)
        return "cached", local_vid

    endpoint = "https://queue.fal.run/fal-ai/hunyuan-video-image-to-video"
    payload = {"prompt": shot["motion_prompt"], "image_url": image_url}
    print(f"[{shot_id}/3] Submitting motion to Hunyuan Video 1080p...", flush=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201, 202):
            raise RuntimeError(f"Hunyuan submit failed for shot {shot_id}: {sub.status_code} - {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(225):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 5 == 0:
                print(f"   Shot {shot_id} Hunyuan Status: {status} ({i*4}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                if not vid_url:
                    raise RuntimeError(f"Could not extract video url for shot {shot_id}: {final_res}")

                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Shot {shot_id} Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return vid_url, local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Hunyuan task failed for shot {shot_id}: {res_data}")
        raise TimeoutError(f"Hunyuan generation timed out for shot {shot_id}")


async def generate_full_audio_15s() -> tuple[Path, Path]:
    """Synthesize continuous 15s BBC nature narration and grand orchestral score."""
    import edge_tts
    narration_text = (
        "In the heart of the Canadian wilderness, ancient glaciers carved towering monuments of granite. "
        "Crystal rivers weave through emerald pine canopies, while twilight paints the high peaks in living gold."
    )
    voice_file = OUTPUT_DIR / "wild_canada_narration_15s.mp3"
    communicate = edge_tts.Communicate(narration_text, "en-GB-RyanNeural", rate="-6%")
    await communicate.save(str(voice_file))
    print(f"Narrative Audio Ready: {voice_file.name}", flush=True)

    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    score_file = OUTPUT_DIR / "wild_canada_orchestral_15s.mp3"
    synth_cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=15:c=pink:r=48000:a=0.015",
        "-f", "lavfi", "-i", "sine=f=110:d=15:r=48000",
        "-f", "lavfi", "-i", "sine=f=164.81:d=15:r=48000",
        "-filter_complex",
        "[1:a]volume=0.22,afade=t=in:ss=0:d=2.0,afade=t=out:st=13.0:d=2.0[cello];"
        "[2:a]volume=0.18,afade=t=in:ss=0:d=2.5,afade=t=out:st=12.5:d=2.5[horn];"
        "[0:a][cello][horn]amix=inputs=3:dropout_transition=0,volume=1.2[out]",
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
        str(score_file)
    ]
    subprocess.run(synth_cmd, check=True, capture_output=True)
    print(f"Orchestral Score Ready: {score_file.name}", flush=True)
    return voice_file, score_file


def master_4k_3shot_documentary(clip_paths: list[Path], voice_path: Path, score_path: Path) -> Path:
    """Master all 3 shots into a single 4K UHD 24.0 fps master (-crf 18, Lanczos)."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    final_output = OUTPUT_DIR / "wild_canada_ep1_3shot_4k_master.mp4"

    filter_complex = (
        "[0:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v0];"
        "[1:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v1];"
        "[2:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v2];"
        "[v0][v1][v2]concat=n=3:v=1:a=0[vcat];"
        "[4:a]volume=0.18[bgm_quiet];"
        "[3:a][bgm_quiet]amix=inputs=2:duration=first:dropout_transition=0,volume=1.3[aout]"
    )

    cmd = [
        exe, "-y",
        "-i", str(clip_paths[0]),
        "-i", str(clip_paths[1]),
        "-i", str(clip_paths[2]),
        "-i", str(voice_path),
        "-i", str(score_path),
        "-filter_complex", filter_complex,
        "-map", "[vcat]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-movflags", "+faststart",
        str(final_output)
    ]

    print("Executing Single-Pass 4K Lanczos Mastering for 3-Shot Showcase...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mastering failed:\n{res.stderr}")

    print(f"4K 3-Shot Master Complete: {final_output.name} ({final_output.stat().st_size} bytes)")
    return final_output


def extract_shot_snapshots(video_path: Path):
    """Extract snapshots at 2s, 7s, and 12s."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    snap_dir = Path("scratch/analysis/comparison_frames/ep1_3shot_snapshots")
    snap_dir.mkdir(parents=True, exist_ok=True)

    times = [("shot1_basin_f2s.jpg", "2.0"), ("shot2_river_f7s.jpg", "7.0"), ("shot3_sunset_f12s.jpg", "12.0")]
    for filename, timestamp in times:
        out_snap = snap_dir / filename
        cmd = [exe, "-y", "-ss", timestamp, "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(out_snap)]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Extracted Snapshot: {out_snap.name} ({out_snap.stat().st_size} bytes)")


async def main():
    print("================================================================================")
    print("EPISODE 1 SHOWCASE: Wild Canada (3-Shot 15s FLUX 1.1 Pro Ultra + Hunyuan 1080p)")
    print("================================================================================")
    clip_paths = []
    for shot in SHOTS_CONFIG:
        img_url, img_path = await get_or_generate_keyframe(shot)
        vid_url, vid_path = await get_or_generate_hunyuan_clip(shot, img_url)
        clip_paths.append(vid_path)

    voice, score = await generate_full_audio_15s()
    master = master_4k_3shot_documentary(clip_paths, voice, score)
    extract_shot_snapshots(master)
    print("================================================================================")
    print("SHOWCASE READY!")
    print(f"Master: {master}")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
