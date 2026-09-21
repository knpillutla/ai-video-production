"""Production pipeline for 30-second Telugu Sankranthi Mass Jathara video.
Adheres strictly to Directives 12, 13, 14, 15, 16, and 17.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path and ensure UTF-8 console output
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import httpx
from PIL import Image
import numpy as np

from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary

FAL_KEY = "82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258"
HEADERS = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json",
}

OUT_DIR = Path("storage/live_production/sankranthi_mass_jathara_30s")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = get_ffmpeg_binary()


CHARACTER_ANCHOR_PREFIX = (
    "Protagonist Raju, 25-year-old mid-20s strikingly handsome South Asian Telugu man with lean-athletic fit build, "
    "warm wheatish complexion, well-defined sharp jawline, short neatly styled black hair, clean trimmed light stubble, "
    "confident charismatic smile, wearing festive saffron-orange embroidered silk kurta and traditional cream silk panche dhoti with gold zari border, "
)


async def generate_flux_keyframe(prompt: str, filename: str, seed: int = 42819) -> tuple[str, Path]:
    """Generate 4K photoreal keyframe via Fal Flux Dev with character consistency anchor and seed locking."""
    out_path = OUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 50000:
        print(f"Keyframe already exists: {out_path}")
        return "", out_path

    print(f"\n--- Generating Keyframe: {filename} (Seed: {seed}) ---")
    endpoint = "https://queue.fal.run/fal-ai/flux/dev"
    payload = {
        "prompt": f"{CHARACTER_ANCHOR_PREFIX} {prompt}",
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "seed": seed,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201):
            raise RuntimeError(f"Flux submission failed: {sub.status_code} {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")
        print(f"Submitted task: {sub_data.get('request_id')}")

        for _ in range(40):
            await asyncio.sleep(2.5)
            s = await client.get(status_url, headers=HEADERS)
            status = s.json().get("status")
            if status == "COMPLETED":
                res = await client.get(resp_url, headers=HEADERS)
                data = res.json()
                img_url = data["images"][0]["url"]
                print(f"Generated Image URL: {img_url}")

                img_resp = await client.get(img_url)
                out_path.write_bytes(img_resp.content)
                print(f"Saved keyframe: {out_path} ({out_path.stat().st_size // 1024} KB)")
                return img_url, out_path
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Flux generation failed: {status}")

    raise TimeoutError(f"Flux keyframe timed out for {filename}")


async def generate_kling_motion(image_url: str, prompt: str, filename: str, duration: str = "10") -> Path:
    """Generate video motion from keyframe via Kling v1.5 Pro."""
    out_path = OUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 1000000:
        print(f"Motion video already exists: {out_path}")
        return out_path

    print(f"\n--- Submitting Kling Motion Task ({duration}s): {filename} ---")
    endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/pro/image-to-video"
    payload = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": duration,
        "aspect_ratio": "16:9",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201):
            raise RuntimeError(f"Kling submission failed: {sub.status_code} {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")
        print(f"Queued Kling task: {sub_data.get('request_id')}")

        for i in range(80):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            status = s_resp.json().get("status")
            if i % 3 == 0:
                print(f"Kling progress: {status} ({i*4}s elapsed)")
            if status == "COMPLETED":
                r = await client.get(resp_url, headers=HEADERS)
                video_url = r.json().get("video", {}).get("url")
                print(f"Kling Video Ready: {video_url}")
                vid_resp = await client.get(video_url)
                out_path.write_bytes(vid_resp.content)
                print(f"Saved Kling video: {out_path} ({out_path.stat().st_size // 1024} KB)")
                return out_path
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Kling failed with status {status}")

    raise TimeoutError(f"Kling motion generation timed out for {filename}")


def prepare_30s_audio_bed(dest_audio: Path) -> Path:
    """Prepare a continuous 30.0s 48kHz stereo Suno Sankranthi track."""
    if dest_audio.exists() and dest_audio.stat().st_size > 100000:
        return dest_audio

    source_suno = Path("storage/live_production/job_2_surrumantadiro/surrumantadiro_song.mp3")
    cmd = [
        FFMPEG, "-y",
        "-ss", "00:00:00",
        "-i", str(source_suno),
        "-t", "30.0",
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=7,afade=t=out:st=28.5:d=1.5",
        "-ar", "48000",
        "-ac", "2",
        "-c:a", "aac",
        "-b:a", "320k",
        str(dest_audio),
    ]
    subprocess.run(cmd, check=True)
    print(f"Created 30s 48kHz stereo audio master: {dest_audio}")
    return dest_audio


async def main():
    print("==================================================================")
    print("🎬 STARTING 30-SECOND TELUGU SANKRANTHI MASS JATHARA PRODUCTION")
    print("==================================================================")

    # 1. Prepare 30s Audio Master
    audio_path = OUT_DIR / "sankranthi_30s_audio_master.m4a"
    prepare_30s_audio_bed(audio_path)

    # 2. Scene Prompts (Directive 12, 13, 15, 16)
    prompts = [
        {
            "id": "scene_1_intro_wide",
            "flux_prompt": (
                "Ultra-photorealistic 4K cinematic wide shot, handsome 32-year-old South Indian Telugu male lead with well-built lean-athletic muscular physique, "
                "groomed beard and charismatic joyful smile, wearing vibrant saffron-orange silk kurta with gold embroidery and traditional cream silk panche dhoti "
                "with crimson zari border hitched up at the knee. Surrounded by 6 energetic young South Indian male dancers in matching festive dhotis playing traditional "
                "dappu drums and clapping with festive celebration in an authentic Andhra village jathara courtyard during Sankranthi festival. "
                "Colorful kites soaring in the clear blue sky, fresh tall sugarcane stalks, marigold flower garlands, crisp natural 5500K daylight, "
                "realistic natural skin tones, zero artificial yellow flare, authentic festive cultural atmosphere."
            ),
            "kling_prompt": (
                "Ultra-photorealistic 4K cinematic broadcast, handsome well-built 32-year-old South Indian man dynamically swagger-walking forward with joyful charisma, "
                "rhythmic shoulder shrugs and hands on waist matching the folk dappu beat, background male dancers energetically beating drums and clapping, "
                "silk dhoti swaying with natural fabric physics, crisp 5500K natural daylight, fluid human movement."
            ),
            "duration": "10",
        },
        {
            "id": "scene_2_hook_bokeh",
            "flux_prompt": (
                "Ultra-photorealistic 4K cinematic medium close-up portrait, handsome 32-year-old South Indian Telugu male lead with well-built athletic physique, "
                "singing passionately with expressive Telugu abhinaya, hand gesturing in rhythmic call-and-response, vibrant saffron silk kurta, groomed beard, "
                "shallow depth-of-field with creamy f/1.4 optical bokeh blurring the festive Sankranthi sugarcane arches and male troupe dancers in the soft background, "
                "crisp natural 5500K daylight on face, authentic skin texture, striking eye contact, festive Indian celebration."
            ),
            "kling_prompt": (
                "Ultra-photorealistic 4K cinematic medium close-up, handsome South Indian man singing with expressive facial acting, joyful smile, "
                "rhythmic hand gestures and subtle head tilts matching the song, background male dancers clapping in soft focus, "
                "natural daylight, fluid facial and hand motion."
            ),
            "duration": "10",
        },
        {
            "id": "scene_3_mass_hook_lowangle",
            "flux_prompt": (
                "Ultra-photorealistic 4K cinematic dynamic low-angle shot, handsome well-built 32-year-old South Indian male lead executing a high-energy mass dance hook step, "
                "vigorous foot stomping kicking up golden ground dust, waist twist, traditional orange silk kurta and hitched-up silk dhoti flowing with realistic motion, "
                "flanked by background male dancers jumping and dancing in explosive synchronization, Sankranthi harvest fairgrounds with decorated bullocks and flying kites against clear blue sky, "
                "crisp natural daylight, heroic celebratory perspective."
            ),
            "kling_prompt": (
                "Ultra-photorealistic 4K cinematic dynamic low-angle dance motion, handsome well-built South Indian man performing vigorous synchronized mass hook step, "
                "rapid foot-stomping, waist twists, joyful celebration, background troupe dancing with high energy, dust particles and fabric movement under crisp daylight."
            ),
            "duration": "10",
        },
    ]

    video_clips = []

    # Process each scene
    for i, sc in enumerate(prompts):
        print(f"\n>>> PROCESSING SCENE {i+1}/3: {sc['id']} <<<")
        keyframe_name = f"{sc['id']}_keyframe.jpg"
        img_url, img_path = await generate_flux_keyframe(sc["flux_prompt"], keyframe_name)

        video_name = f"{sc['id']}_motion_{sc['duration']}s.mp4"
        vid_path = await generate_kling_motion(img_url, sc["kling_prompt"], video_name, duration=sc["duration"])
        video_clips.append(vid_path)

    # 3. Final Single-Pass 4K Mastering
    final_master = OUT_DIR / "sankranthi_30s_4k_master.mp4"
    print("\n==================================================================")
    print("🎬 MASTERING 30-SECOND 4K UHD 30FPS BROADCAST VIDEO")
    print("==================================================================")

    # Concat filter complex with 30fps and 4K UHD scaling
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_clips[0]),
        "-i", str(video_clips[1]),
        "-i", str(video_clips[2]),
        "-i", str(audio_path),
        "-filter_complex",
        "[0:v]scale=3840:2160:flags=lanczos,fps=30,setpts=PTS-STARTPTS[v0];"
        "[1:v]scale=3840:2160:flags=lanczos,fps=30,setpts=PTS-STARTPTS[v1];"
        "[2:v]scale=3840:2160:flags=lanczos,fps=30,setpts=PTS-STARTPTS[v2];"
        "[v0][v1][v2]concat=n=3:v=1:a=0[vmaster];"
        "[3:a]aformat=sample_rates=48000:channel_layouts=stereo[amaster]",
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-t", "30.0",
        str(final_master),
    ]

    print("Running FFmpeg master render command...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg stderr:", res.stderr[-800:])
        raise RuntimeError(f"FFmpeg mastering failed with code {res.returncode}")

    print(f"\n🎉 30-SECOND 4K MASTER READY: {final_master} ({final_master.stat().st_size // (1024*1024)} MB)")


if __name__ == "__main__":
    asyncio.run(main())
