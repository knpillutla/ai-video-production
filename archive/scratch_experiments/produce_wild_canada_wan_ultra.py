"""Live Production Test: Wild Canada Nature Documentary (Single 5s Shot - Wan 2.1 + FLUX 1.1 Pro Ultra).

Adheres to:
- Directive 3: Universal Artifact Caching (reuses exact FLUX 1.1 Pro Ultra keyframe for 100% apples-to-apples comparison).
- Directive 8: Single test shot to minimize cost ($0.40 total API cost).
- Directive 14: Cinematic 24.0 fps, 4K CRF 18 Lanczos mastering, 48kHz audio.
- Uses Fal endpoint: fal-ai/wan-i2v.
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

OUTPUT_DIR = Path("storage/live_production/wild_canada_wan_ultra_test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SRC_HUNYUAN_DIR = Path("storage/live_production/wild_canada_hunyuan_test")


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


async def get_or_upload_keyframe() -> tuple[str, Path]:
    """Retrieve existing FLUX 1.1 Pro Ultra keyframe and upload to Fal."""
    local_img = SRC_HUNYUAN_DIR / "shot_1_keyframe_pro_ultra.jpg"
    if not local_img.exists():
        raise FileNotFoundError(f"Keyframe not found at {local_img}")

    # Copy to our output dir for local reference
    target_img = OUTPUT_DIR / "shot_1_keyframe_pro_ultra.jpg"
    if not target_img.exists():
        target_img.write_bytes(local_img.read_bytes())

    fal_url_cache = SRC_HUNYUAN_DIR / "shot_1_keyframe_pro_ultra.jpg.fal_url"
    if fal_url_cache.exists():
        cached_url = fal_url_cache.read_text().strip()
        if cached_url.startswith("http"):
            print(f"[i] Using cached Fal image URL: {cached_url}", flush=True)
            return cached_url, target_img

    from src.providers.fal_storage import upload_to_fal
    print(f"1. Uploading FLUX 1.1 Pro Ultra keyframe to Fal storage ({target_img.stat().st_size} bytes)...", flush=True)
    uploaded_url = await upload_to_fal(target_img, api_key=FAL_KEY)
    fal_url_cache.write_text(uploaded_url)
    return uploaded_url, target_img


async def generate_wan21_clip(image_url: str) -> tuple[str, Path]:
    """Generate 5s motion using Alibaba Wan 2.1 on Fal.ai."""
    endpoint = "https://queue.fal.run/fal-ai/wan-i2v"
    prompt = (
        "Ultra-photorealistic 4K cinematic BBC Planet Earth documentary aerial camera glide slowly descending "
        "and pushing forward over pristine turquoise glacial waters toward towering snow-capped Rocky Mountain peaks, "
        "slow expansive camera motion, 24fps film cadence, zero high-speed rush."
    )
    payload = {"prompt": prompt, "image_url": image_url}
    print("2. Submitting single test motion to Wan 2.1 (fal-ai/wan-i2v)...", flush=True)

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201, 202):
            raise RuntimeError(f"Wan 2.1 submit failed: {sub.status_code} - {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")
        print(f"   [i] Successfully connected to Wan 2.1 endpoint: {endpoint}")

    local_vid = OUTPUT_DIR / "wan_ultra_test_raw_5s.mp4"
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        for i in range(120):
            await asyncio.sleep(3)
            s_resp = await client.get(status_url, headers=HEADERS, params={"logs": "1"})
            res_data = s_resp.json()
            status = res_data.get("status")
            if i % 4 == 0:
                print(f"   Wan 2.1 Status: {status} ({i*3}s elapsed)", flush=True)

            if status == "COMPLETED":
                r_resp = await client.get(response_url, headers=HEADERS)
                final_res = r_resp.json()
                vid_url = _extract_video_url(final_res) or _extract_video_url(res_data)
                if not vid_url:
                    raise RuntimeError(f"Could not extract video url from response: {final_res}")

                v_bytes = (await client.get(vid_url, timeout=90.0)).content
                local_vid.write_bytes(v_bytes)
                print(f"   Wan 2.1 Clip Ready: {local_vid.name} ({len(v_bytes)} bytes)", flush=True)
                return vid_url, local_vid
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Wan 2.1 task failed: {res_data}")
        raise TimeoutError("Wan 2.1 generation timed out (exceeded 6m)")


async def get_audio_stems() -> tuple[Path, Path]:
    """Reuse or generate 5s narration and orchestral audio stems."""
    voice_file = OUTPUT_DIR / "wild_canada_narration_5s.mp3"
    score_file = OUTPUT_DIR / "wild_canada_orchestral_5s.mp3"

    src_voice = SRC_HUNYUAN_DIR / "wild_canada_narration_5s.mp3"
    src_score = SRC_HUNYUAN_DIR / "wild_canada_orchestral_5s.mp3"

    if src_voice.exists():
        voice_file.write_bytes(src_voice.read_bytes())
    else:
        import edge_tts
        communicate = edge_tts.Communicate("In the heart of the Canadian wilderness, ancient glaciers carved towering monuments of granite.", "en-GB-RyanNeural", rate="-6%")
        await communicate.save(str(voice_file))

    if src_score.exists():
        score_file.write_bytes(src_score.read_bytes())
    else:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        synth_cmd = [
            exe, "-y",
            "-f", "lavfi", "-i", "anoisesrc=d=5:c=pink:r=48000:a=0.015",
            "-f", "lavfi", "-i", "sine=f=110:d=5:r=48000",
            "-f", "lavfi", "-i", "sine=f=164.81:d=5:r=48000",
            "-filter_complex",
            "[1:a]volume=0.22,afade=t=in:ss=0:d=1.5,afade=t=out:st=3.5:d=1.5[cello];"
            "[2:a]volume=0.18,afade=t=in:ss=0:d=2.0,afade=t=out:st=3.5:d=1.5[horn];"
            "[0:a][cello][horn]amix=inputs=3:dropout_transition=0,volume=1.2[out]",
            "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
            str(score_file)
        ]
        subprocess.run(synth_cmd, check=True, capture_output=True)

    return voice_file, score_file


def master_4k_single_pass(video_clip: Path, voice_path: Path, score_path: Path) -> Path:
    """Master to 4K UHD 24.0 fps with Lanczos upscale and broadcast audio ducking."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    final_output = OUTPUT_DIR / "wild_canada_wan_ultra_4k_master.mp4"

    filter_complex = (
        "[0:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v4k];"
        "[2:a]volume=0.18[bgm_quiet];"
        "[1:a][bgm_quiet]amix=inputs=2:duration=first:dropout_transition=0,volume=1.3[aout]"
    )

    cmd = [
        exe, "-y",
        "-i", str(video_clip),
        "-i", str(voice_path),
        "-i", str(score_path),
        "-filter_complex", filter_complex,
        "-map", "[v4k]",
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

    print("3. Executing Single-Pass 4K Lanczos Mastering...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mastering failed:\n{res.stderr}")

    print(f"4. 4K Master Complete: {final_output.name} ({final_output.stat().st_size} bytes)")
    return final_output


def extract_comparison_frame(video_path: Path) -> Path:
    """Extract 4K frame at 2.0s for side-by-side comparison."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    out_frame_dir = Path("scratch/analysis/comparison_frames")
    out_frame_dir.mkdir(parents=True, exist_ok=True)
    out_frame = out_frame_dir / "wan_ultra_4k_f2s.jpg"

    cmd = [
        exe, "-y",
        "-ss", "2.0",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_frame)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"5. Extracted Comparison Frame: {out_frame.name} ({out_frame.stat().st_size} bytes)")
    return out_frame


async def main():
    print("================================================================================")
    print("LIVE PRODUCTION TEST: Wan 2.1 + FLUX 1.1 Pro Ultra (Single 5s Shot)")
    print("================================================================================")
    img_url, img_path = await get_or_upload_keyframe()
    vid_url, raw_vid = await generate_wan21_clip(img_url)
    voice, score = await get_audio_stems()
    master = master_4k_single_pass(raw_vid, voice, score)
    frame = extract_comparison_frame(master)
    print("================================================================================")
    print("TEST SUCCEEDED!")
    print(f"- 4K Master: {master}")
    print(f"- Snapshot Frame: {frame}")
    print("================================================================================")


if __name__ == "__main__":
    asyncio.run(main())
