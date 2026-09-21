"""Production pipeline for Afghanistan Blizzard Shepherd Survival Documentary Showcase.
Adheres strictly to Directives 11, 14, and 18.
"""

import asyncio
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
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter

FAL_KEY = "82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258"
HEADERS = {
    "Authorization": f"Key {FAL_KEY}",
    "Content-Type": "application/json",
}

OUT_DIR = Path("storage/live_production/afghanistan_blizzard_survival_10s")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = get_ffmpeg_binary()


async def generate_blizzard_keyframe(prompt: str, out_path: Path) -> tuple[str, Path]:
    """Generate ultra-photorealistic survival documentary keyframe via Fal Flux Dev."""
    if out_path.exists() and out_path.stat().st_size > 50000:
        print(f"Keyframe already exists: {out_path}")
        return "", out_path

    print(f"\n--- Generating Blizzard Survival Keyframe ---")
    endpoint = "https://queue.fal.run/fal-ai/flux/dev"
    payload = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        if sub.status_code not in (200, 201):
            raise RuntimeError(f"Flux submission failed: {sub.status_code} {sub.text}")
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")

        for _ in range(40):
            await asyncio.sleep(2.5)
            s = await client.get(status_url, headers=HEADERS)
            status = s.json().get("status")
            if status == "COMPLETED":
                res = await client.get(resp_url, headers=HEADERS)
                data = res.json()
                img_url = data["images"][0]["url"]
                print(f"Generated Keyframe URL: {img_url}")
                img_resp = await client.get(img_url)
                out_path.write_bytes(img_resp.content)
                print(f"Saved keyframe: {out_path} ({out_path.stat().st_size // 1024} KB)")
                return img_url, out_path
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Flux generation failed: {status}")

    raise TimeoutError("Flux keyframe timed out")


async def generate_blizzard_motion(image_url: str, prompt: str, out_path: Path, duration: str = "10") -> Path:
    """Generate 10s video motion via Kling v1.5 Pro."""
    if out_path.exists() and out_path.stat().st_size > 1000000:
        print(f"Motion video already exists: {out_path}")
        return out_path

    print(f"\n--- Submitting Kling Motion Task ({duration}s) ---")
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

        for i in range(80):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            status = s_resp.json().get("status")
            if i % 3 == 0:
                print(f"Kling progress: {status} ({i*4}s elapsed)")
            if status == "COMPLETED":
                r = await client.get(resp_url, headers=HEADERS)
                video_url = r.json().get("video", {}).get("url")
                vid_resp = await client.get(video_url)
                out_path.write_bytes(vid_resp.content)
                print(f"Saved Kling video: {out_path} ({out_path.stat().st_size // 1024} KB)")
                return out_path
            elif status in ("FAILED", "CANCELLED"):
                raise RuntimeError(f"Kling failed with status {status}")

    raise TimeoutError("Kling motion generation timed out")


async def synthesize_authoritative_narration(text: str, out_path: Path) -> Path:
    """Synthesize BBC/NatGeo style measured documentary voiceover."""
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path

    tts = AzureSpeechTTSAdapter()
    audio_bytes = await tts.synthesize_speech(
        text=text,
        voice_id="en-GB-RyanNeural",
        language_code="en-GB",
    )
    out_path.write_bytes(audio_bytes)
    print(f"Synthesized voiceover: {out_path} ({out_path.stat().st_size} bytes)")
    return out_path


def synthesize_procedural_blizzard_audio(dest_path: Path, duration_seconds: float = 10.0) -> Path:
    """Procedurally synthesize sub-zero howling blizzard wind and haunting cello drone via NumPy DSP."""
    wav_path = dest_path.with_suffix(".wav")
    if wav_path.exists() and wav_path.stat().st_size > 50000:
        return wav_path

    import wave
    import numpy as np

    sample_rate = 48000
    total_samples = int(sample_rate * duration_seconds)
    t = np.linspace(0, duration_seconds, total_samples, endpoint=False)

    # 1. Howling sub-zero wind (low rumble + wind gusts)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 0.2, total_samples)
    # Slow wind gusts envelope
    gusts = 0.5 + 0.5 * (np.sin(2 * np.pi * 0.22 * t) ** 2)
    wind = noise * gusts * 9000

    # 2. Haunting mountain cello drone (C2 + G2 + C3 harmonics)
    drone = (
        0.24 * np.sin(2 * np.pi * 65.41 * t)
        + 0.16 * np.sin(2 * np.pi * 98.00 * t)
        + 0.09 * np.sin(2 * np.pi * 130.81 * t)
    ) * 11000

    combined = wind + drone
    fade_len = int(sample_rate * 1.5)
    combined[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)

    sig_l = np.clip(combined * 0.9, -32767, 32767).astype(np.int16)
    sig_r = np.clip(combined * 0.75, -32767, 32767).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(np.column_stack((sig_l, sig_r)).tobytes())

    print(f"Synthesized procedural blizzard foley and score: {wav_path} ({wav_path.stat().st_size} bytes)")
    return wav_path


async def main():
    print("==================================================================")
    print("🎬 STARTING AFGHANISTAN BLIZZARD SHEPHERD SURVIVAL SHOWCASE")
    print("==================================================================")

    # 1. Narrator Script (Directive 11 & 18 YPP Compliance)
    narration_text = (
        "High in the frozen passes of the Hindu Kush, a sub-zero blizzard threatens everything. "
        "Against nature's fiercest fury, an Afghan shepherd battles the whiteout, leading his flock toward shelter."
    )
    narration_file = OUT_DIR / "blizzard_survival_narration.mp3"
    await synthesize_authoritative_narration(narration_text, narration_file)

    # 2. Procedural Blizzard Soundscape (Tier 0 Local DSP)
    bgm_file = OUT_DIR / "blizzard_foley_score.wav"
    synthesize_procedural_blizzard_audio(bgm_file, duration_seconds=10.0)

    # 3. Keyframe Prompt (Directive 18 Visceral Realism)
    flux_prompt = (
        "Ultra-photorealistic 4K cinematic medium-wide shot, weathered 55-year-old Afghan mountain shepherd in the Hindu Kush mountains, "
        "battling a fierce sub-zero winter blizzard with heavy blowing powder snow. Wearing a heavy traditional sheepskin coat (postin) "
        "and rough-spun wool scarf caked in frost and ice crystals, dignified resilient eyes, breath condensing into thick white vapor. "
        "Guiding a flock of hardy mountain sheep through knee-deep snowdrifts toward a crude stone and mud-brick shelter in the background, "
        "desolate rocky peaks shrouded in whiteout mist, raw cold 6000K overcast winter light, extreme visceral realism, National Geographic cover quality."
    )
    keyframe_file = OUT_DIR / "afghan_shepherd_blizzard_keyframe.jpg"
    img_url, _ = await generate_blizzard_keyframe(flux_prompt, keyframe_file)

    # 4. Kling Video Motion (Directive 18 & 14: 24 fps cadence)
    kling_prompt = (
        "Ultra-photorealistic 4K cinematic broadcast, heavy sub-zero blizzard wind howling and blowing powder snow sideways across the mountain pass, "
        "Afghan shepherd trudging slowly and determinedly through deep snowdrifts with walking staff, sheep moving steadily behind him, "
        "heavy woolen garments swaying in freezing gale, steam rising from breath, slow deliberate cinematic 24fps film cadence."
    )
    raw_video = OUT_DIR / "blizzard_shepherd_kling_raw.mp4"
    await generate_blizzard_motion(img_url, kling_prompt, raw_video, duration="10")

    # 5. Final Master: Single-Pass FFmpeg 4K 24fps with -18dB Sidechain Ducking
    master_file = OUT_DIR / "afghanistan_blizzard_survival_4k_master.mp4"
    print("\n--- Mastering 4K 24fps Visually Lossless MP4 ---")
    cmd = [
        FFMPEG, "-y",
        "-i", str(raw_video),
        "-i", str(narration_file),
        "-i", str(bgm_file),
        "-filter_complex",
        "[0:v]scale=3840:2160:flags=lanczos,fps=24,setpts=PTS-STARTPTS[vmaster];"
        "[2:a][1:a]sidechaincompress=threshold=0.08:ratio=6:attack=50:release=400[ducked_bgm];"
        "[1:a]volume=1.0[vox];"
        "[ducked_bgm][vox]amix=inputs=2:weights='0.4 1.0':normalize=0[mixed_audio];"
        "[mixed_audio]loudnorm=I=-14.0:TP=-1.0:LRA=7,aformat=sample_rates=48000:channel_layouts=stereo[amaster]",
        "-map", "[vmaster]",
        "-map", "[amaster]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-t", "10.0",
        str(master_file),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg stderr:", res.stderr[-800:])
        raise RuntimeError(f"FFmpeg mastering failed with code {res.returncode}")

    print(f"\n🎉 AFGHANISTAN BLIZZARD SURVIVAL 4K MASTER READY: {master_file} ({master_file.stat().st_size // (1024*1024)} MB)")


if __name__ == "__main__":
    asyncio.run(main())
