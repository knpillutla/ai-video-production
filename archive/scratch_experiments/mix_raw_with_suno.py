"""Mix raw video clips from Kling v3 Pro and Alibaba Wan 2.1 with pure Suno live audio."""

import subprocess
import imageio_ffmpeg
from pathlib import Path

ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
audio_path = Path("storage/audio_vault/test_live_suno_10s.wav")
comp_dir = Path("storage/live_production/waterfall_patio_retreat/comparison")

kling_raw = comp_dir / "patio_waterfall_kling_raw_5s.mp4"
wan_raw = comp_dir / "patio_waterfall_wan21_raw_5s.mp4"

kling_out = comp_dir / "patio_waterfall_kling_4k_suno.mp4"
wan_out = comp_dir / "patio_waterfall_wan21_4k_suno.mp4"


def render_4k_master(video_src: Path, dest: Path):
    print(f"[*] Rendering 4K Lanczos Master: {video_src.name} + Suno Audio -> {dest.name}")
    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(video_src),
        "-i", str(audio_path),
        "-filter_complex", "[0:v]scale=3840:2160:flags=lanczos,setsar=1,fps=24[v0]",
        "-map", "[v0]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(dest)
    ]
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Ready: {dest} ({dest.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    if kling_raw.exists():
        render_4k_master(kling_raw, kling_out)
    else:
        print(f"[!] Missing {kling_raw}")

    if wan_raw.exists():
        render_4k_master(wan_raw, wan_out)
    else:
        print(f"[!] Missing {wan_raw}")
