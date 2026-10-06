import sys, time
sys.path.insert(0, ".")
from pathlib import Path
from src.scripts.local_perspective_drone import render_perspective_drone_clip_sync
from src.services.ambient_export_service import get_media_duration

ep_dir = Path("storage/user-knpillutla-gmail-com/channels/skylinediariesindia4k/EP-001")

shots = [
    (1, ep_dir / "keyframe_p1.jpg", ep_dir / "motion_p1.mp4", 41.03, "slow_drone_forward"),
    (2, ep_dir / "keyframe_p2.jpg", ep_dir / "motion_p2.mp4", 40.00, "slow_drone_forward"),
    (3, ep_dir / "keyframe_p3.jpg", ep_dir / "motion_p3.mp4", 40.00, "slow_drone_forward"),
]

for idx, kf, out_v, dur_target, movement in shots:
    print(f"Rendering Shot {idx} full unlooped drone glide for {dur_target:.2f}s...")
    t0 = time.time()
    render_perspective_drone_clip_sync(
        image_path=kf,
        output_path=out_v,
        duration_seconds=dur_target,
        fps=24,
        target_res=(3840, 2160),
        camera_movement=movement,
        speed_factor=1.0,
        force_rerun=True,
    )
    render_time = time.time() - t0
    final_dur = get_media_duration(out_v)
    size_mb = out_v.stat().st_size / (1024 * 1024)
    print(f"Shot {idx} rendered in {render_time:.2f}s! Video duration: {final_dur:.2f}s, size: {size_mb:.2f}MB")
