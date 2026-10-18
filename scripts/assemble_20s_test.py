"""Assemble 20-second concert video test with Kling LipSync and guitar cutaways."""

from __future__ import annotations

import subprocess
from pathlib import Path
import imageio_ffmpeg


def main():
    out_dir = Path("storage/tests/lofi_singer_test").resolve()
    master_audio = out_dir / "trimmed_vocal_20s.mp3"
    guitar_vid = out_dir / "shot2_acoustic_guitar_5s.mp4"
    singing_vid = out_dir / "test20_cut2_singing_11s.mp4"
    living_base = out_dir / "unobstructed_living_motion_5s.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # Cut 1: 0.0s - 3.0s (3s Guitar intro pickup)
    c1 = out_dir / "test20_cut1_guitar_3s.mp4"
    subprocess.run(
        [
            ffmpeg, "-y", "-stream_loop", "-1", "-i", str(guitar_vid),
            "-t", "3.0", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
            "-pix_fmt", "yuv420p", "-an", str(c1)
        ],
        check=True,
    )

    # Cut 2: 3.0s - 14.0s (11s Singer Telugu LipSync)
    c2 = singing_vid

    # Cut 3: 14.0s - 17.0s (3s Guitar strumming cutaway)
    c3 = out_dir / "test20_cut3_guitar_3s.mp4"
    subprocess.run(
        [
            ffmpeg, "-y", "-ss", "1.0", "-i", str(guitar_vid),
            "-t", "3.0", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
            "-pix_fmt", "yuv420p", "-an", str(c3)
        ],
        check=True,
    )

    # Cut 4: 17.0s - 20.0s (3s Singer expressive movement)
    c4 = out_dir / "test20_cut4_singer_3s.mp4"
    subprocess.run(
        [
            ffmpeg, "-y", "-ss", "0.5", "-i", str(living_base),
            "-t", "3.0", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
            "-pix_fmt", "yuv420p", "-an", str(c4)
        ],
        check=True,
    )

    cuts = [c1, c2, c3, c4]
    concat_txt = out_dir / "test20_concat.txt"
    lines = [f"file '{p.resolve().as_posix()}'" for p in cuts]
    concat_txt.write_text("\n".join(lines), encoding="utf-8")

    master_out = out_dir / "master_telugu_concert_20s_test.mp4"
    cmd = [
        ffmpeg, "-y", "-nostats", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(master_audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-t", "20.0", "-movflags", "+faststart",
        str(master_out),
    ]
    subprocess.run(cmd, check=True)
    size_mb = master_out.stat().st_size / (1024 * 1024)
    print(f"🎉 MASTER 20S VIDEO ASSEMBLED: {master_out} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
