"""Local Hybrid Demonstration: 10-Second 4K Blue-Chip Nature Montage.

Demonstrates the Hybrid Pattern:
- Shot 1 (5s): Pristine 4K Sub-Pixel Optical Push-In & Pan on FLUX 1.1 Pro Ultra image (Zero AI motion cost, 100% 4K crisp stillness).
- Shot 2 (5s): Hunyuan Video 1080p Live Motion (Turquoise water flow, subtle mist & reflection drift).
- Total Cost for this demo: $0.00 (reusing already generated assets on disk).
"""

import os
import sys
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("storage/live_production/wild_canada_hybrid_demo")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HUNYUAN_DIR = Path("storage/live_production/wild_canada_hunyuan_test")
KEYFRAME = HUNYUAN_DIR / "shot_1_keyframe_pro_ultra.jpg"
MOTION_CLIP = HUNYUAN_DIR / "wild_canada_hunyuan_4k_master.mp4"

import imageio_ffmpeg
exe = imageio_ffmpeg.get_ffmpeg_exe()

def build_hybrid_demo():
    print("1. Generating Shot 1: Sub-pixel 4K optical camera glide on Ultra Keyframe...", flush=True)
    shot1_video = OUTPUT_DIR / "shot_1_optical_glide_5s.mp4"
    
    # 5s slow push-in (zoompan filter) at 4K 24fps
    cmd_shot1 = [
        exe, "-y",
        "-loop", "1",
        "-i", str(KEYFRAME),
        "-vf", "zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=120:s=3840x2160:fps=24",
        "-t", "5",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(shot1_video)
    ]
    subprocess.run(cmd_shot1, check=True, capture_output=True)
    print(f"   Shot 1 Ready: {shot1_video.name}")

    print("2. Generating continuous BBC voiceover and grand orchestral score...", flush=True)
    import edge_tts
    import asyncio
    
    narration_file = OUTPUT_DIR / "hybrid_narration_10s.mp3"
    score_file = OUTPUT_DIR / "hybrid_orchestral_10s.mp3"
    
    text = "Across the vast silence of the Rockies, timeless peaks stand as sentinels... while glacial waters breathe life into the valleys below."
    communicate = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="-5%")
    asyncio.run(communicate.save(str(narration_file)))

    synth_audio_cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=10:c=pink:r=48000:a=0.015",
        "-f", "lavfi", "-i", "sine=f=110:d=10:r=48000",
        "-f", "lavfi", "-i", "sine=f=164.81:d=10:r=48000",
        "-filter_complex",
        "[1:a]volume=0.22,afade=t=in:ss=0:d=2.0,afade=t=out:st=8.0:d=2.0[cello];"
        "[2:a]volume=0.18,afade=t=in:ss=0:d=2.5,afade=t=out:st=8.0:d=2.0[horn];"
        "[0:a][cello][horn]amix=inputs=3:dropout_transition=0,volume=1.2[out]",
        "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
        str(score_file)
    ]
    subprocess.run(synth_audio_cmd, check=True, capture_output=True)

    print("3. Assembling 10s Hybrid Master (Shot 1 Optical Glide + Shot 2 Hunyuan Motion)...", flush=True)
    final_hybrid_master = OUTPUT_DIR / "wild_canada_hybrid_nature_4k_master.mp4"

    # Concatenate Shot 1 (Optical Glide) and Shot 2 (Hunyuan Live Motion 4K) with crossfade / cut
    concat_filter = (
        "[0:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v0];"
        "[1:v]fps=24,scale=3840:2160:flags=lanczos,setsar=1[v1];"
        "[v0][v1]concat=n=2:v=1:a=0[vcat];"
        "[3:a]volume=0.18[bgm_quiet];"
        "[2:a][bgm_quiet]amix=inputs=2:duration=first:dropout_transition=0,volume=1.3[aout]"
    )

    cmd_master = [
        exe, "-y",
        "-i", str(shot1_video),
        "-i", str(HUNYUAN_DIR / "hunyuan_test_raw_5s.mp4"),
        "-i", str(narration_file),
        "-i", str(score_file),
        "-filter_complex", concat_filter,
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
        str(final_hybrid_master)
    ]
    subprocess.run(cmd_master, check=True, capture_output=True)
    print(f"4. Hybrid 4K Master Complete: {final_hybrid_master.name} ({final_hybrid_master.stat().st_size} bytes)")
    return final_hybrid_master

if __name__ == "__main__":
    build_hybrid_demo()
