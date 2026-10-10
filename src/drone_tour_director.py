"""Drone Tour Director - Multi-Chapter 4K Travel Documentary Producer.

Renders and orchestrates long-form episodic travel chapters from panoramic photos
and assembles them into a single broadcast-grade master video with seamless cross-fades
and optional background music.
"""

import os
import sys
import argparse
import time
import subprocess
import cv2
import numpy as np

# Import core matrix calculation and FFmpeg helpers from drone_view
from drone_view import (
    FFMPEG_BIN,
    get_ffmpeg_writer,
    precompute_sequence_matrices,
    CinematicRainEngine,
)
from cinematic_atmosphere_engine import (
    GoldenHourAtmosphereEngine,
    DocumentaryHUDEngine,
    TimedSubtitleRenderer,
    CinematicPostProcessingEngine,
)


SICILY_CHAPTERS = [
    {
        "id": "ch1_rooftops",
        "title": "Chapter 1: The Rooftops & Alleys of Medieval Taormina",
        "image_file": "sicily_03_village_alleys.jpg",
        "coords": "37.8524 N, 15.2862 E",
        "altitude": 195,
        "subtitle": "Winding cobblestones and blooming bougainvillea across medieval Corso Umberto.",
        "start_pan": "left",
        "start_tilt": "down",
        "start_zoom": "in",
        "depth": 0.50,
        "sequence": [
            ("stay", 15.0),
            ("pan-right", 30.0),
            ("stay", 20.0),
            ("tilt-up", 20.0),
            ("stay", 15.0),
            ("pan-left", 20.0),
        ],
    },
    {
        "id": "ch2_theatre",
        "title": "Chapter 2: The Ancient Greek Theatre & Classical Columns",
        "image_file": "sicily_02_theatre_ruins.jpg",
        "coords": "37.8525 N, 15.2922 E",
        "altitude": 204,
        "subtitle": "Carved into Monte Tauro in the 3rd Century BC overlooking the Ionian Sea.",
        "start_pan": "center",
        "start_tilt": "down",
        "start_zoom": "in",
        "depth": 0.55,
        "sequence": [
            ("stay", 15.0),
            ("pan-right", 25.0),
            ("stay", 20.0),
            ("tilt-up", 20.0),
            ("stay", 15.0),
            ("zoom-out", 25.0),
        ],
    },
    {
        "id": "ch3_ocean",
        "title": "Chapter 3: The Azure Mediterranean & Isola Bella Bay",
        "image_file": "sicily_01_ocean_coast.jpg",
        "coords": "37.8504 N, 15.3009 E",
        "altitude": 42,
        "subtitle": "The Pearl of the Ionian Sea, sheltered beneath sheer limestone cliffs.",
        "start_pan": "right",
        "start_tilt": "center",
        "start_zoom": "in",
        "depth": 0.50,
        "sequence": [
            ("stay", 20.0),
            ("dollyin", 25.0),
            ("stay", 20.0),
            ("pan-left", 20.0),
            ("stay", 15.0),
            ("zoom-out", 20.0),
        ],
    },
    {
        "id": "ch4_etna",
        "title": "Chapter 4: The Slopes & Volcanic Majesty of Mount Etna",
        "image_file": "sicily_04_etna_summit.jpg",
        "coords": "37.7510 N, 14.9934 E",
        "altitude": 3357,
        "subtitle": "Europe's highest active volcano, puffing white steam into the twilight sky.",
        "start_pan": "left",
        "start_tilt": "up",
        "start_zoom": "in",
        "depth": 0.55,
        "sequence": [
            ("stay", 25.0),
            ("pan-right", 25.0),
            ("stay", 20.0),
            ("dollyin", 20.0),
            ("stay", 15.0),
            ("zoom-out", 15.0),
        ],
    },
    {
        "id": "ch5_panorama",
        "title": "Chapter 5: The Grand Sunset Master Horizon",
        "image_file": "sicily.jpg",
        "coords": "37.8516 N, 15.2853 E",
        "altitude": 280,
        "subtitle": "An eternal Mediterranean spectacle spanning ancient history and volcanic majesty.",
        "start_pan": "center",
        "start_tilt": "center",
        "start_zoom": "in",
        "depth": 0.40,
        "sequence": [
            ("stay", 20.0),
            ("zoom-out", 30.0),
            ("stay", 70.0),
        ],
    },
]


def scale_chapter_sequence(raw_seq: list, target_duration: float) -> list:
    """Scales a sequence proportionally or pads hold to meet chapter target duration."""
    total_raw = sum(dur for _, dur in raw_seq)
    if total_raw <= 0:
        return [("stay", target_duration)]
    scale = target_duration / total_raw
    scaled = []
    for act, dur in raw_seq:
        scaled.append((act, max(1.0, dur * scale)))
    return scaled


def render_chapter_clip(
    img: np.ndarray,
    chapter_info: dict,
    output_path: str,
    target_duration: float,
    fps: float = 30.0,
    output_size: tuple = (3840, 2160),
    rain: bool = False,
    rain_intensity: str = "medium",
    force: bool = False,
    letterbox: bool = True,
) -> str:
    """Renders a single chapter clip to disk with broadcast H.264."""
    if not force and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
        print(f" -> [Cached] Chapter '{chapter_info['id']}' already exists: {output_path}")
        return output_path

    seq = scale_chapter_sequence(chapter_info["sequence"], target_duration)
    out_w, out_h = output_size

    matrices, total_frames = precompute_sequence_matrices(
        img_shape=img.shape,
        sequence=seq,
        fps=fps,
        output_size=output_size,
        max_depth=chapter_info["depth"],
        start_pan=chapter_info["start_pan"],
        start_zoom=chapter_info["start_zoom"],
        start_tilt=chapter_info["start_tilt"],
        curve="cosine",
    )

    rain_engine = CinematicRainEngine(out_w, out_h, intensity=rain_intensity) if rain else None
    sun_engine = GoldenHourAtmosphereEngine(out_w, out_h)
    hud_engine = DocumentaryHUDEngine(out_w, out_h)
    sub_renderer = TimedSubtitleRenderer(out_w, out_h)
    post_engine = CinematicPostProcessingEngine(out_w, out_h, aspect_ratio=2.39, enable_letterbox=letterbox)

    ffmpeg_proc = get_ffmpeg_writer(output_path, out_w, out_h, fps)
    if ffmpeg_proc is None:
        raise RuntimeError("Failed to spawn FFmpeg process")

    # Prepare lower-third badge & subtitle text
    title_text = chapter_info.get("title", "")
    badge_frames = int(round(5.0 * fps))  # display badge for first 5 seconds
    coords_text = chapter_info.get("coords", "37.8516 N, 15.2853 E")
    altitude_m = chapter_info.get("altitude", 204)
    sub_text = chapter_info.get("subtitle", "")

    t0 = time.time()
    for i in range(total_frames):
        frame = cv2.warpPerspective(
            img,
            matrices[i],
            output_size,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        if rain_engine is not None:
            frame = rain_engine.render(frame)

        # 1. Atmospheric Golden-Hour Lens Flare & Dust Motes
        frame = sun_engine.render(frame, i)

        # 2. Minimalist Documentary Flight HUD Telemetry (Top Corner)
        frame = hud_engine.render(frame, "TAORMINA, SICILY", coords_text, altitude_m, i)

        # 3. Timed Narration Subtitle Overlay (Middle to End)
        sub_start_frame = int(2.0 * fps)
        sub_end_frame = int(total_frames - 2.0 * fps)
        if sub_start_frame <= i <= sub_end_frame:
            sub_alpha = 1.0
            if i < sub_start_frame + int(0.8 * fps):
                sub_alpha = (i - sub_start_frame) / float(0.8 * fps)
            elif i > sub_end_frame - int(0.8 * fps):
                sub_alpha = (sub_end_frame - i) / float(0.8 * fps)
            frame = sub_renderer.render(frame, sub_text, sub_alpha)

        # 4. Draw elegant cinematic lower-third badge during first 5 seconds
        if i < badge_frames and title_text:
            fade_frames = int(0.8 * fps)
            if i < fade_frames:
                alpha = i / float(fade_frames)
            elif i > badge_frames - fade_frames:
                alpha = (badge_frames - i) / float(fade_frames)
            else:
                alpha = 1.0

            if alpha > 0.05:
                scale = out_w / 3840.0
                font_scale = 1.35 * scale
                thickness = max(2, int(2.5 * scale))
                (tw, th), baseline = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)
                pad_x = int(32 * scale)
                pad_y = int(18 * scale)
                box_x = int(120 * scale)
                box_y = int(out_h - (240 * scale if letterbox else 170 * scale))
                
                # Dark frosted glass pill
                overlay = frame.copy()
                cv2.rectangle(overlay, (box_x - pad_x, box_y - th - pad_y), (box_x + tw + pad_x, box_y + pad_y), (15, 18, 22), -1)
                # Accent gold bar on left of pill
                cv2.rectangle(overlay, (box_x - pad_x, box_y - th - pad_y), (box_x - pad_x + int(8 * scale), box_y + pad_y), (60, 180, 240), -1)
                cv2.addWeighted(overlay, 0.65 * alpha, frame, 1.0 - (0.65 * alpha), 0, frame)
                cv2.putText(frame, title_text, (box_x, box_y), cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # 5. Hollywood 2.39:1 Letterbox, Vignette, and Diurnal Color Grading
        frame = post_engine.render(frame, i, total_frames)

        ffmpeg_proc.stdin.write(frame.tobytes())

    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()

    elapsed = time.time() - t0
    print(f" -> Rendered {total_frames} frames in {elapsed:.1f}s ({total_frames/max(0.1, elapsed):.1f} FPS)")
    return output_path


def assemble_master_tour(
    chapter_files: list,
    master_output: str,
    bgm_path: str = None,
    transition_sec: float = 1.5,
    fps: float = 30.0,
):
    """Concatenates chapter video files with smooth crossfade dissolves and optional BGM."""
    print(f"\n--- Assembling Broadcast Master Film ({len(chapter_files)} Chapters) ---")

    # Generate FFmpeg concat filter complex with smooth crossfades
    cmd = [FFMPEG_BIN, "-y"]
    for f in chapter_files:
        cmd.extend(["-i", f])

    if bgm_path and os.path.exists(bgm_path):
        cmd.extend(["-i", bgm_path])
        has_bgm = True
    else:
        has_bgm = False

    # Build filter complex for crossfading video clips sequentially
    filter_parts = []
    num_inputs = len(chapter_files)

    if num_inputs == 1:
        filter_parts.append("[0:v]copy[vout]")
    else:
        # Get duration of first clip
        curr_label = "0:v"
        accum_offset = 0.0

        for idx in range(1, num_inputs):
            # For each transition, offset = duration_so_far - transition_sec
            clip_dur = cv2.VideoCapture(chapter_files[idx - 1]).get(cv2.CAP_PROP_FRAME_COUNT) / fps
            accum_offset += clip_dur - (transition_sec if idx > 1 else 0.0)
            offset = accum_offset - transition_sec
            next_label = f"v{idx}"
            filter_parts.append(
                f"[{curr_label}][{idx}:v]xfade=transition=fade:duration={transition_sec}:offset={offset:.2f}[{next_label}];"
            )
            curr_label = next_label

        # Clean trailing semicolon
        filter_parts[-1] = filter_parts[-1].rstrip(";")

    filter_complex = "".join(filter_parts)

    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", f"[{curr_label}]"])

    if has_bgm:
        bgm_idx = num_inputs
        cmd.extend([
            "-map", f"{bgm_idx}:a",
            "-c:a", "aac",
            "-b:a", "256k",
            "-af", "afade=t=out:st=117:d=3",
            "-shortest",
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-threads", "4",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        master_output,
    ])

    print(f" -> Merging master film: {master_output}")
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] Master Tour Film Ready: {master_output}\n")


def run_tour_director(
    image_path: str,
    output_dir: str,
    total_duration_sec: float = 600.0,
    bgm_path: str = None,
    fps: float = 30.0,
    res_mode: str = "4k",
    rain: bool = False,
    rain_intensity: str = "medium",
):
    """Orchestrates multi-chapter rendering and assembly for panoramic image tours."""
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image: {image_path}")
        return

    output_size = (3840, 2160) if res_mode.lower() == "4k" else (1920, 1080)
    stem = os.path.splitext(os.path.basename(image_path))[0]
    num_chapters = len(SICILY_CHAPTERS)
    chap_dur = total_duration_sec / float(num_chapters)

    print(f"============================================================")
    print(f"       CINEMATIC 4K TOUR DIRECTOR: {stem.upper()}            ")
    print(f"============================================================")
    print(f"Target Duration: {total_duration_sec:.1f}s ({total_duration_sec/60:.1f} mins)")
    print(f"Chapters: {num_chapters} (~{chap_dur:.1f}s each) | Resolution: {output_size[0]}x{output_size[1]}")
    print(f"BGM Audio: {bgm_path if bgm_path else 'None (Silent Master)'}")
    print(f"============================================================\n")

    rendered_clips = []
    input_base_dir = os.path.dirname(image_path) if os.path.isfile(image_path) else image_path

    for idx, chap in enumerate(SICILY_CHAPTERS, start=1):
        # Resolve specific photo file for this chapter
        target_img_name = chap.get("image_file")
        chap_img_path = os.path.join(input_base_dir, target_img_name) if target_img_name else image_path
        if not os.path.exists(chap_img_path):
            chap_img_path = image_path

        chap_img = cv2.imread(chap_img_path)
        if chap_img is None:
            chap_img = img

        chap_filename = f"{stem}_{chap['id']}_{int(chap_dur)}s.mp4"
        chap_path = os.path.join(output_dir, chap_filename)
        print(f"[{idx}/{num_chapters}] Rendering {chap['title']} ({chap_dur:.1f}s) from {os.path.basename(chap_img_path)}...")
        clip_path = render_chapter_clip(
            img=chap_img,
            chapter_info=chap,
            output_path=chap_path,
            target_duration=chap_dur,
            fps=fps,
            output_size=output_size,
            rain=rain,
            rain_intensity=rain_intensity,
        )
        rendered_clips.append(clip_path)

    # Final Assembly
    master_name = f"{stem}_{int(total_duration_sec//60)}min_grand_tour_master.mp4"
    master_path = os.path.join(output_dir, master_name)
    assemble_master_tour(rendered_clips, master_path, bgm_path=bgm_path, fps=fps)


def run_tour_director(
    image_path: str,
    output_dir: str,
    total_duration_sec: float = 600.0,
    bgm_path: str = None,
    fps: float = 30.0,
    res_mode: str = "4k",
    rain: bool = False,
    rain_intensity: str = "medium",
    force: bool = False,
    letterbox: bool = True,
):
    """Orchestrates multi-chapter rendering and assembly for panoramic image tours."""
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image: {image_path}")
        return

    output_size = (3840, 2160) if res_mode.lower() == "4k" else (1920, 1080)
    stem = os.path.splitext(os.path.basename(image_path))[0]
    num_chapters = len(SICILY_CHAPTERS)
    chap_dur = total_duration_sec / float(num_chapters)

    print(f"============================================================")
    print(f"       CINEMATIC 4K TOUR DIRECTOR: {stem.upper()}            ")
    print(f"============================================================")
    print(f"Target Duration: {total_duration_sec:.1f}s ({total_duration_sec/60:.1f} mins)")
    print(f"Chapters: {num_chapters} (~{chap_dur:.1f}s each) | Resolution: {output_size[0]}x{output_size[1]}")
    print(f"Format: {'2.39:1 Anamorphic Letterbox' if letterbox else '16:9 Full Frame'} | Force Overwrite: {force}")
    print(f"BGM Audio: {bgm_path if bgm_path else 'None (Silent Master)'}")
    print(f"============================================================\n")

    rendered_clips = []
    input_base_dir = os.path.dirname(image_path) if os.path.isfile(image_path) else image_path

    for idx, chap in enumerate(SICILY_CHAPTERS, start=1):
        target_img_name = chap.get("image_file")
        chap_img_path = os.path.join(input_base_dir, target_img_name) if target_img_name else image_path
        if not os.path.exists(chap_img_path):
            chap_img_path = image_path

        chap_img = cv2.imread(chap_img_path)
        if chap_img is None:
            chap_img = img

        chap_filename = f"{stem}_{chap['id']}_{int(chap_dur)}s.mp4"
        chap_path = os.path.join(output_dir, chap_filename)
        print(f"[{idx}/{num_chapters}] Rendering {chap['title']} ({chap_dur:.1f}s) from {os.path.basename(chap_img_path)}...")
        clip_path = render_chapter_clip(
            img=chap_img,
            chapter_info=chap,
            output_path=chap_path,
            target_duration=chap_dur,
            fps=fps,
            output_size=output_size,
            rain=rain,
            rain_intensity=rain_intensity,
            force=force,
            letterbox=letterbox,
        )
        rendered_clips.append(clip_path)

    # Final Assembly
    master_name = f"{stem}_{int(total_duration_sec//60)}min_grand_tour_master.mp4"
    master_path = os.path.join(output_dir, master_name)
    assemble_master_tour(rendered_clips, master_path, bgm_path=bgm_path, fps=fps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Chapter 4K Travel Documentary Tour Director")
    parser.add_argument("-i", "--image", required=True, help="Input panoramic image path (e.g. C:\\test\\input1\\sicily.jpg)")
    parser.add_argument("-o", "--output", required=True, help="Output directory for chapters and master film")
    parser.add_argument("-d", "--duration", type=float, default=600.0,
                        help="Total film duration in seconds (default: 600.0 for 10-min master; use 120.0 for 2-min test)")
    parser.add_argument("--bgm", type=str, default=None, help="Optional background music audio file path (.mp3/.wav)")
    parser.add_argument("--fps", type=float, default=30.0, help="Framerate (default: 30.0)")
    parser.add_argument("--res", choices=["4k", "1080p"], default="4k", help="Resolution: 4k (default) or 1080p")
    parser.add_argument("--rain", action="store_true", help="Add cinematic atmospheric rainfall")
    parser.add_argument("--rain-intensity", choices=["light", "medium", "heavy"], default="medium")
    parser.add_argument("--force", action="store_true", help="Force re-rendering of all chapters instead of using cached clips")
    parser.add_argument("--no-letterbox", action="store_true", help="Disable 2.39:1 Hollywood anamorphic letterbox bars")

    args = parser.parse_args()

    run_tour_director(
        image_path=args.image,
        output_dir=args.output,
        total_duration_sec=args.duration,
        bgm_path=args.bgm,
        fps=args.fps,
        res_mode=args.res,
        rain=args.rain,
        rain_intensity=args.rain_intensity,
        force=args.force,
        letterbox=not args.no_letterbox,
    )
