import asyncio
from pathlib import Path
import json
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary, execute_single_pass_render
from src.compositor.timeline import compile_timeline_from_scenes
from src.scripts.local_pan_zoom import render_steadycam_clip_sync, CameraMovement

ep_dir = Path("storage/user-133db3ee-33de-42e0-8798-a2970a5f555a/creative_vault/shows_and_titles/paris_montmartre_in_the_rain_4k/episodes/2e2f726c-62d8-4f21-8236-c8faa900bd7a")
scenes_dir = ep_dir / "scenes"
renders_dir = ep_dir / "master_renders"
stems_dir = ep_dir / "audio_stems"

# Storyboard movements
movements = {
    0: CameraMovement.SLOW_ZOOM_IN,
    2: CameraMovement.PAN_RIGHT,
    4: CameraMovement.TILT_UP,
    5: CameraMovement.SLOW_ZOOM_OUT,
}

for idx, mov in movements.items():
    img_path = scenes_dir / f"scene_{idx:02d}.jpg"
    vid_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
    vid_path.unlink(missing_ok=True)
    print(f"Re-rendering scene_{idx:02d}_motion.mp4 with continuous {mov.value}...")
    render_steadycam_clip_sync(
        image_path=img_path,
        output_path=vid_path,
        duration_seconds=10.0,
        fps=30,
        target_res=(1920, 1080),
        movement=mov,
        ffmpeg_bin=get_ffmpeg_binary(),
    )
    print(f"Rendered: {vid_path.name} ({vid_path.stat().st_size} bytes)")

# Recompile timeline
scene_objs = []
for i in range(6):
    v_path = scenes_dir / f"scene_{i:02d}_motion.mp4"
    voice_path = stems_dir / f"voice_scene_{i:02d}.wav"
    scene_objs.append({
        "scene_index": i,
        "duration_seconds": 10.0,
        "video_path": v_path,
        "voice_path": voice_path if voice_path.exists() else None,
        "camera_movement": "static"
    })

bgm_path = stems_dir / "bgm_master.wav"
foley_path = stems_dir / "foley_master.wav"
sub_path = ep_dir / "subtitles" / "burned_subtitles.ass"

timeline = compile_timeline_from_scenes(
    scene_data=scene_objs,
    bgm_path=bgm_path if bgm_path.exists() else None,
    foley_path=foley_path if foley_path.exists() else None,
    subtitle_path=sub_path if sub_path.exists() else None,
    target_resolution=(1920, 1080),
    fps=30,
)

master_mp4 = renders_dir / "master_16x9_ep01.mp4"
master_mp4.unlink(missing_ok=True)
print("Re-rendering master video...")
asyncio.run(execute_single_pass_render(timeline=timeline, output_path=master_mp4, dry_run=False))
print(f"Master re-rendered successfully: {master_mp4} ({master_mp4.stat().st_size} bytes)")
