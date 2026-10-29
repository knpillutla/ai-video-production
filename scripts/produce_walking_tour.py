"""Studio 4K Ultra-Tranquil Walking Tour Producer (Z-Image Turbo + Local Drone).

Generates a continuous 2-minute 4K first-person POV walking tour:
1. Z-Image Turbo: Generates 10 successive path-progressing keyframe perspectives.
2. Local Perspective Drone: Warps each keyframe with ultra-slow dolly-in (~1.5 km/h).
3. Procedural Foley & Single-Pass Concat: Streams 4K video clips into master MP4 ($0.00 motion).
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import subprocess
import sys
import time

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"

from src.core.telemetry import logger
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync
from src.services.procedural_foley import synthesize_foley_stem

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


WALKING_PRESETS: dict[str, list[str]] = {
    "swiss_alps": [
        "First-person POV walking tour perspective, looking forward down a narrow sunlit alpine gravel trail near Grindelwald, rustic wooden Swiss chalets with red geranium flower boxes, lush green hillside, majestic snow-covered Eiger mountain in the distance, crisp open-air natural daylight (5500K), eye-level human walking height, ultra-sharp 4K landscape photorealism.",
        "First-person POV walking tour perspective, continuing forward along the mountain path, rolling emerald green pastures, gentle wildflowers along the path edge, Simmental dairy cows grazing calmly, sharp towering granite summits under clear daylight, leading lines down the walking trail.",
        "First-person POV walking tour perspective, walking toward a pine forest border, crystal clear glacial runoff stream flowing alongside the path, smooth mountain stones, sunbeams through evergreen branches, eye-level human walking cadence, deep optical depth of field.",
        "First-person POV walking tour perspective, approaching an authentic rustic timber footbridge spanning the clear mountain stream, hand-hewn logs, wildflowers lining the creek bank, panoramic snow peaks ahead, natural balanced daylight.",
        "First-person POV walking tour perspective, crossing the wooden footbridge looking straight forward along the trail into the open meadow, sound of rushing water, majestic alpine panorama under crisp natural sun, realistic photorealistic textures.",
        "First-person POV walking tour perspective, exiting the bridge into an open high-alpine meadow, sweeping panoramic vista of the Lauterbrunnen valley unfolding ahead, distant cliffside waterfalls, tranquil open path, eye-level human perspective.",
        "First-person POV walking tour perspective, strolling past a traditional historic Swiss farmhouse with neatly stacked firewood, carved wooden balconies, lush valley slope dropping off to the right, crystal clear mountain atmosphere.",
        "First-person POV walking tour perspective, gentle path following the contour of the valley ridge, breathtaking views of sheer rock cliffs and Staubbach waterfall mist in the distance, soft alpine breeze, leading lines down the dirt trail.",
        "First-person POV walking tour perspective, cobblestone path entering the upper outskirts of a quiet mountain village, rustic timber trail markers, stone water trough with fresh mountain spring water, flower beds, warm natural sunlight.",
        "First-person POV walking tour perspective, arriving at a panoramic wooden overlook terrace at trail end, sweeping majestic 360-degree vista of the entire Swiss alpine valley, sunlit peaks, tranquil serene finish.",
    ],
    "portugal_coastal": [
        "First-person POV walking tour perspective, looking forward down a charming sunlit cobblestone pedestrian alley in historic Alfama Lisbon, vibrant pastel townhouses with blue azulejo ceramic tiles, wrought iron balconies with colorful flower pots, open-air natural daylight (5500K), eye-level human walking height.",
        "First-person POV walking tour perspective, continuing forward along the gentle cobblestone incline, terracotta rooflines framing blue sky, bougainvillea vines spilling over ancient stone walls, authentic street textures, leading lines down the pathway.",
        "First-person POV walking tour perspective, approaching an historic carved stone archway framing a sun-drenched village plaza ahead, soft morning daylight, quiet morning ambiance, eye-level human perspective.",
        "First-person POV walking tour perspective, stepping through the archway into the open cobbled square, historic limestone fountain with clear trickling water, rustic outdoor cafe tables, colorful Portuguese facades.",
        "First-person POV walking tour perspective, turning down a wide sunlit street descending toward the sparkling blue riverfront, golden daylight reflecting off polished cobblestones, distant river views.",
        "First-person POV walking tour perspective, walking past traditional pastel yellow and terracotta houses, historic tiled facade panels, gentle downhill slope leading directly toward the waterfront promenade.",
        "First-person POV walking tour perspective, emerging onto the wide stone riverfront promenade, historic wrought iron streetlamps, open panoramic river vista under crisp blue skies, gentle sea breeze.",
        "First-person POV walking tour perspective, walking along the sunlit Douro river promenade, traditional wooden rabelo wine boats bobbing in the blue water, historic port wine lodges on opposite bank.",
        "First-person POV walking tour perspective, approaching the grand double-deck Dom Luis I iron bridge along the river quay, sunlight glinting across gentle river ripples, wide panoramic framing.",
        "First-person POV walking tour perspective, arriving at the scenic stone pier overlook at the waterfront, expansive breathtaking panoramic view of the historic city skyline and sparkling river, sunlit finish.",
    ],
    "kyoto_bamboo": [
        "First-person POV walking tour perspective, looking forward down the entrance of the serene Arashiyama bamboo forest path, towering green bamboo stalks arching overhead, neat woven bamboo fences lining the dirt trail, crisp morning daylight, eye-level human walking height.",
        "First-person POV walking tour perspective, continuing forward along the secluded earthen path, gentle rustling bamboo leaves, soft green filtered natural light, tranquil walking tour cadence, deep optical depth of field.",
        "First-person POV walking tour perspective, walking deeper into the grove, bright komorebi sunlight filtering through the dense bamboo canopy onto the path, peaceful atmosphere, authentic Japanese woodland.",
        "First-person POV walking tour perspective, approaching a weathered moss-covered stone toro lantern beside a gentle bend in the path, leading lines of the bamboo railings guiding forward.",
        "First-person POV walking tour perspective, stepping around the curved bend, revealing a clean raked gravel path ahead bordered by lush green moss gardens and delicate ferns under soft natural daylight.",
        "First-person POV walking tour perspective, exiting the bamboo grove into a serene Zen temple courtyard, vibrant Japanese red maple trees, manicured pine shrubs, peaceful gravel trail.",
        "First-person POV walking tour perspective, following stepping stones across a tranquil garden path alongside a still koi reflection pond, water lilies, subtle water ripple reflections.",
        "First-person POV walking tour perspective, walking along a tranquil cedar-lined gravel pathway leading toward an ancient dark timber temple gate, peaceful contemplative walking cadence.",
        "First-person POV walking tour perspective, approaching the traditional wooden gate with stone steps and moss-draped clay walls under clear open daylight, authentic heritage architecture.",
        "First-person POV walking tour perspective, stepping through the gate to a scenic wooden terrace overlook, breathtaking panoramic vista of forested misty mountains in the distance, serene tranquil finish.",
    ],
}


def build_custom_walking_prompts(topic: str, num_shots: int = 10) -> list[str]:
    """Dynamically generate progressive first-person POV walking tour prompts for any topic."""
    stages = [
        f"Trailhead entrance of {topic}, looking forward down the continuous path, welcoming natural daylight.",
        f"Moving forward along the trail in {topic}, path bordered by authentic scenery, eye-level steadycam framing.",
        f"Continuing down the gentle walkway in {topic}, approaching scenic architectural or landscape features.",
        f"Walking past distinctive regional landmarks along the path in {topic}, crisp 5500K natural sunlight.",
        f"Halfway point along the walkway in {topic}, path curving gently forward, deep optical depth of field.",
        f"Stepping forward along the central promenade in {topic}, expansive mid-point perspective under open skies.",
        f"Progressing past tranquil local surroundings in {topic}, textured walking surface, authentic atmosphere.",
        f"Approaching the scenic overlook section in {topic}, picturesque path leading forward into golden daylight.",
        f"Walking toward the final clearing in {topic}, panoramic surroundings opening up ahead.",
        f"Arriving at the breathtaking panoramic overlook terminus in {topic}, expansive vista, serene final view.",
    ]
    base = [f"First-person POV cinematic 4K walking tour perspective, {st} 16:9 ratio, balanced natural daylight." for st in stages]
    return base[:num_shots]


async def produce_walking_tour(
    preset_name: str = "swiss_alps",
    topic: str | None = None,
    num_shots: int = 10,
    duration_per_shot: float = 12.0,
    output_dir: Path | str = "output/walking_tour_2min",
    skip_images: bool = False,
    skip_motion: bool = False,
    force_live: bool = False,
    with_audio: bool = True,
    custom_audio_path: Path | str | None = None,
    crossfade: float = 2.0,
) -> Path:
    """Execute end-to-end 2-minute 4K walking tour production with Z-Image and local drone."""
    out_dir = Path(output_dir)
    kf_dir = out_dir / "keyframes"
    clips_dir = out_dir / "clips"
    kf_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)

    master_path = out_dir / "master_walking_tour_4k_2min.mp4"
    prompts = build_custom_walking_prompts(topic, num_shots) if topic else WALKING_PRESETS.get(preset_name, WALKING_PRESETS["swiss_alps"])[:num_shots]

    print("=" * 70)
    print("🚶 Studio 4K Ultra-Tranquil Walking Tour Producer")
    print(f"📍 Theme: {topic or preset_name} | Shots: {len(prompts)} × {duration_per_shot:.1f}s = {len(prompts) * duration_per_shot:.0f}s (~2 min)")
    print(f"📁 Output Directory: {out_dir.resolve()}")
    print("=" * 70)

    # 1. Keyframes via Z-Image Turbo
    kf_paths: list[Path] = []
    if skip_images:
        kf_paths = sorted([f for f in kf_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])[:num_shots]
        print(f"⏩ Skipping image generation: Reusing {len(kf_paths)} existing keyframes.")
    else:
        print("\n📸 Stage 1: Synthesizing Progressive Path Keyframes (Z-Image Turbo)...")
        adapter = FalZImageAdapter()
        for i, prompt in enumerate(prompts):
            target_kf = kf_dir / f"shot_{i+1:02d}.jpg"
            if target_kf.exists() and target_kf.stat().st_size > 10_000:
                print(f"  [Shot {i+1:02d}/{len(prompts):02d}] 💾 Cache hit: {target_kf.name} ({target_kf.stat().st_size // 1024} KB)")
                kf_paths.append(target_kf)
                continue
            print(f"  [Shot {i+1:02d}/{len(prompts):02d}] ⚡ Generating {target_kf.name}...")
            _, saved = await adapter.generate_to_file(
                prompt=prompt,
                output_path=target_kf,
                aspect_ratio="16:9",
                force_live=force_live,
                upscale_4k=False,
            )
            kf_paths.append(saved)

    if not kf_paths:
        raise FileNotFoundError(f"No keyframes found or generated in {kf_dir}")

    # 2. Local Perspective Drone Flight (Dolly-In at ~1.5 km/h)
    clip_paths: list[Path] = []
    if skip_motion:
        clip_paths = sorted([f for f in clips_dir.iterdir() if f.name.endswith(".mp4") and not f.name.startswith("_")])[:len(kf_paths)]
        print(f"⏩ Skipping motion rendering: Reusing {len(clip_paths)} existing drone clips.")
    else:
        print("\n🛸 Stage 2: Local 4K Perspective Drone Dolly-In ($0.00 compute)...")
        for i, kf in enumerate(kf_paths):
            target_clip = clips_dir / f"clip_{i+1:02d}.mp4"
            if target_clip.exists() and target_clip.stat().st_size > 1000:
                print(f"  [Clip {i+1:02d}/{len(kf_paths):02d}] 💾 Cache hit: {target_clip.name} ({target_clip.stat().st_size // 1024} KB)")
                clip_paths.append(target_clip)
                continue
            print(f"  [Clip {i+1:02d}/{len(kf_paths):02d}] 🎬 Rendering dolly-in on {kf.name} ({duration_per_shot:.1f}s)...")
            t_start = time.time()
            render_perspective_drone_clip_sync(
                image_path=kf,
                output_path=target_clip,
                duration_seconds=duration_per_shot,
                fps=24,
                target_res=(3840, 2160),
                choreography="dollyin",
                curve="cosine",
                interpolation="cubic",
            )
            elapsed = time.time() - t_start
            print(f"  [Clip {i+1:02d}/{len(kf_paths):02d}] ✅ Rendered in {elapsed:.1f}s ({target_clip.stat().st_size // (1024*1024)} MB)")
            clip_paths.append(target_clip)

    # 3. Procedural Audio Foley & Single-Pass Master Assembly
    print("\n🎞️ Stage 3: Assembling Master 4K Walking Tour Video...")
    total_dur = len(clip_paths) * duration_per_shot
    concat_txt = out_dir / "concat_list.txt"
    concat_txt.write_text("\n".join(f"file '{p.resolve().as_posix()}'" for p in clip_paths), encoding="utf-8")

    audio_file = Path(custom_audio_path) if custom_audio_path and Path(custom_audio_path).is_file() else None
    if with_audio and not audio_file:
        audio_file = out_dir / "ambient_walking_foley.wav"
        if not audio_file.exists() or audio_file.stat().st_size < 1000:
            print("  🔊 Synthesizing 48kHz stereo procedural footsteps & daylight breeze ($0.00)...")
            synthesize_foley_stem(
                weather_type="breeze",
                setting_type="walking_tour",
                space="outdoor",
                duration_seconds=total_dur,
                output_path=audio_file,
                sample_rate=48000,
            )

    if crossfade > 0.0 and len(clip_paths) > 1:
        print(f"  ✨ Applying {crossfade:.1f}s smooth breathing crossfades between clips...")
        inputs: list[str] = []
        for p in clip_paths:
            inputs.extend(["-i", str(p.resolve())])
        filter_parts = [f"[{i}:v]null[s{i}]" for i in range(len(clip_paths))]
        prev_tag = "s0"
        curr_offset = duration_per_shot - crossfade
        for i in range(1, len(clip_paths)):
            out_tag = f"v{i}" if i < len(clip_paths) - 1 else "v_out"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={crossfade:.2f}:offset={max(0.1, curr_offset):.2f}[{out_tag}]")
            prev_tag = out_tag
            curr_offset += duration_per_shot - crossfade
        total_dur = curr_offset
        cmd = [FFMPEG_BIN, "-y", *inputs]
        if audio_file and audio_file.is_file():
            cmd.extend([
                "-i", str(audio_file.resolve()),
                "-filter_complex", ";".join(filter_parts),
                "-map", "[v_out]", "-map", f"{len(clip_paths)}:a",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=7.0",
                "-t", f"{total_dur:.2f}", "-movflags", "+faststart", str(master_path),
            ])
        else:
            cmd.extend([
                "-filter_complex", ";".join(filter_parts),
                "-map", "[v_out]",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "22",
                "-t", f"{total_dur:.2f}", "-movflags", "+faststart", str(master_path),
            ])
    else:
        cmd = [FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt.resolve())]
        if audio_file and audio_file.is_file():
            cmd.extend([
                "-i", str(audio_file.resolve()),
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=7.0",
                "-shortest",
                "-movflags", "+faststart",
                str(master_path),
            ])
        else:
            cmd.extend(["-c:v", "copy", "-movflags", "+faststart", str(master_path)])

    subprocess.run(cmd, check=True, capture_output=True)
    master_mb = master_path.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 70)
    print("🎉 4K Walking Tour Master Video Successfully Created!")
    print(f"🎬 Video File: {master_path.resolve()}")
    print(f"⏱️ Duration: {total_dur:.1f}s (~{total_dur / 60:.1f} min) | Size: {master_mb:.2f} MB")
    print(f"💰 External Video AI Compute Cost: $0.00 (Pure Local Drone + Fast Concat)")
    print("=" * 70 + "\n")
    return master_path


def main():
    parser = argparse.ArgumentParser(description="Produce a 2-minute 4K Walking Tour with Z-Image Turbo and Local Drone.")
    parser.add_argument("--preset", choices=list(WALKING_PRESETS.keys()), default="swiss_alps", help="Preset tour theme")
    parser.add_argument("--topic", default=None, help="Custom tour topic (e.g. 'Rome Historic Cobblestone Walk')")
    parser.add_argument("--shots", type=int, default=10, help="Number of walking perspectives (default: 10)")
    parser.add_argument("--duration", type=float, default=12.0, help="Duration per shot in seconds (default: 12.0s)")
    parser.add_argument("--output-dir", default="output/walking_tour_2min", help="Output directory")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation and reuse existing keyframes")
    parser.add_argument("--skip-motion", action="store_true", help="Skip drone motion rendering and reuse existing clips")
    parser.add_argument("--force-live", action="store_true", help="Force live API calls for Z-Image Turbo")
    parser.add_argument("--no-audio", action="store_true", help="Render video without procedural foley audio")
    parser.add_argument("--audio-path", default=None, help="Path to custom audio file")
    args = parser.parse_args()

    asyncio.run(produce_walking_tour(
        preset_name=args.preset,
        topic=args.topic,
        num_shots=args.shots,
        duration_per_shot=args.duration,
        output_dir=args.output_dir,
        skip_images=args.skip_images,
        skip_motion=args.skip_motion,
        force_live=args.force_live,
        with_audio=not args.no_audio,
        custom_audio_path=args.audio_path,
    ))


if __name__ == "__main__":
    main()
