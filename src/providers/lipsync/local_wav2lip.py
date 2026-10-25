"""Local CPU Wav2Lip Lipsync Adapter via ONNX Runtime ($0.00 spend).

Provides fast, 100% offline local mouth synchronization on CPU for test cuts
and rapid iteration before committing to paid broadcast engines.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess
from typing import Optional, Tuple
import cv2
import numpy as np

from src.core.telemetry import logger
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.providers.base import is_mock_mode

_WAV2LIP_SESSION = None
_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "wav2lip.onnx"
_MEL_STEP_SIZE = 16


def _get_wav2lip_session():
    global _WAV2LIP_SESSION
    if _WAV2LIP_SESSION is None and _MODEL_PATH.is_file():
        try:
            import onnxruntime as ort
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 4
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            _WAV2LIP_SESSION = ort.InferenceSession(str(_MODEL_PATH), sess_options=opts, providers=["CPUExecutionProvider"])
        except Exception as ex:
            logger.warning(f"local_wav2lip_session_error: {ex}")
            _WAV2LIP_SESSION = False
    return _WAV2LIP_SESSION if _WAV2LIP_SESSION is not False else None


def _compute_mel_spectrogram(audio_path: Path) -> np.ndarray:
    import librosa
    wav, sr = librosa.load(str(audio_path), sr=16000)
    mel = librosa.feature.melspectrogram(
        y=wav, sr=sr, n_fft=800, hop_length=200, win_length=800, n_mels=80, fmin=55, fmax=7600
    )
    return np.log(np.clip(mel, a_min=1e-5, a_max=None)).astype(np.float32)


def _detect_face_box(frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Detects primary performer face bounding box (x1, y1, x2, y2)."""
    try:
        from src.scripts.local_perspective_drone import detect_lead_face_center
        h, w = frame.shape[:2]
        center = detect_lead_face_center(frame)
        if center is not None:
            cx, cy = center
            # Lead face box estimated from face center (~18% of frame height)
            box_sz = int(h * 0.22)
            x1 = max(0, int(cx - box_sz // 2))
            x2 = min(w, int(cx + box_sz // 2))
            y1 = max(0, int(cy - int(box_sz * 0.35)))
            y2 = min(h, int(cy + int(box_sz * 0.65)))
            if (x2 - x1) > 30 and (y2 - y1) > 30:
                return (x1, y1, x2, y2)
    except Exception:
        pass
    # Center fallback
    h, w = frame.shape[:2]
    sz = int(min(h, w) * 0.25)
    cx, cy = w // 2, int(h * 0.35)
    return (cx - sz // 2, cy - sz // 2, cx + sz // 2, cy + sz // 2)


class LocalWav2LipAdapter:
    """Local CPU Lip-sync Engine via ONNX Runtime."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or _MODEL_PATH

    async def sync_lips(
        self,
        video_path: Path | str,
        audio_path: Path | str,
        output_path: Path | str,
        force_live: bool = False,
        **kwargs,
    ) -> Path:
        """Alias for lipsync_video matching standard studio directorial calls."""
        return await self.lipsync_video(
            video_url=str(video_path),
            audio_path=Path(audio_path),
            output_path=output_path,
            force_live=force_live,
        )

    async def lipsync_video(
        self,
        video_url: str | Path,
        audio_path: Path,
        output_path: Path | str,
        force_live: bool = False,
        **kwargs,
    ) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 50_000:
            logger.info(f"local_wav2lip_cache_hit: {out.name} ({out.stat().st_size} B)")
            return out

        if (is_mock_mode() and not force_live) or not self.model_path.is_file():
            return self._fallback_passthrough(Path(video_url), audio_path, out)

        return await asyncio.to_thread(self._render_wav2lip_sync, Path(video_url), audio_path, out)

    def _render_wav2lip_sync(self, video_path: Path, audio_path: Path, out_path: Path) -> Path:
        sess = _get_wav2lip_session()
        if sess is None:
            return self._fallback_passthrough(video_path, audio_path, out_path)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return self._fallback_passthrough(video_path, audio_path, out_path)

        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        try:
            mel = _compute_mel_spectrogram(audio_path)
        except Exception as ex:
            logger.warning(f"local_wav2lip_mel_failed: {ex}")
            cap.release()
            return self._fallback_passthrough(video_path, audio_path, out_path)

        ffmpeg_bin = get_ffmpeg_binary()
        chunk_dir = out_path.parent / f".wav2lip_chunks_{out_path.stem}"
        chunk_dir.mkdir(parents=True, exist_ok=True)

        chunk_duration_sec = 8.0
        frames_per_chunk = max(24, int(fps * chunk_duration_sec))
        batch_size = 16
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        chunk_files: list[Path] = []
        chunk_idx = 0
        global_frame_idx = 0
        last_box = None

        while True:
            chunk_synced = chunk_dir / f"chunk_{chunk_idx:03d}.mp4"
            chunk_raw = chunk_dir / f"raw_{chunk_idx:03d}.mp4"

            # Rule 3: Check existing valid chunk on disk (idempotent resumption)
            if chunk_synced.is_file() and chunk_synced.stat().st_size > 30_000:
                chunk_files.append(chunk_synced)
                global_frame_idx += frames_per_chunk
                cap.set(cv2.CAP_PROP_POS_FRAMES, global_frame_idx)
                chunk_idx += 1
                if total_frames > 0 and global_frame_idx >= total_frames:
                    break
                continue

            writer = None
            chunk_rendered_frames = 0
            chunk_start_time = global_frame_idx / fps

            while chunk_rendered_frames < frames_per_chunk:
                to_read = min(batch_size, frames_per_chunk - chunk_rendered_frames)
                batch = []
                for _ in range(to_read):
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        break
                    batch.append(frame)

                if not batch:
                    break

                if writer is None:
                    writer = cv2.VideoWriter(str(chunk_raw), fourcc, fps, (width, height))

                if last_box is None or (global_frame_idx % 32 == 0):
                    b = _detect_face_box(batch[0])
                    if b:
                        last_box = b
                box = last_box or (width // 4, height // 4, 3 * width // 4, 3 * height // 4)
                x1, y1, x2, y2 = box
                target_w, target_h = x2 - x1, y2 - y1

                mel_chunks, vid_crops = [], []
                for local_i, frame in enumerate(batch):
                    f_idx = global_frame_idx + local_i
                    m_idx = int(f_idx * (16000.0 / 200.0) / fps)
                    m_chunk = mel[:, m_idx:m_idx + _MEL_STEP_SIZE] if (m_idx + _MEL_STEP_SIZE <= mel.shape[1]) else (mel[:, -_MEL_STEP_SIZE:] if mel.shape[1] >= _MEL_STEP_SIZE else np.pad(mel, ((0, 0), (0, _MEL_STEP_SIZE - mel.shape[1]))))
                    fc = cv2.resize(frame[y1:y2, x1:x2], (96, 96)) if (target_w > 0 and target_h > 0) else np.zeros((96, 96, 3), dtype=np.uint8)
                    m_crop = (fc.astype(np.float32) / 255.0)
                    m_crop[48:, :] = 0.0
                    ref = (fc.astype(np.float32) / 255.0)
                    mel_chunks.append(m_chunk[None, ...])
                    vid_crops.append(np.concatenate([m_crop, ref], axis=-1).transpose(2, 0, 1))

                out_faces = sess.run(None, {"mel": np.stack(mel_chunks, axis=0), "vid": np.stack(vid_crops, axis=0)})[0]

                mask = np.zeros((target_h, target_w), dtype=np.float32)
                cv2.ellipse(mask, (target_w // 2, int(target_h * 0.65)), (int(target_w * 0.38), int(target_h * 0.28)), 0, 0, 360, 1.0, -1)
                mask = cv2.GaussianBlur(mask, (21, 21), 0)[..., None]

                for idx, out_face in enumerate(out_faces):
                    face_s = cv2.resize((out_face.transpose(1, 2, 0) * 255.0).clip(0, 255).astype(np.uint8), (target_w, target_h))
                    orig = batch[idx][y1:y2, x1:x2].astype(np.float32)
                    batch[idx][y1:y2, x1:x2] = (face_s.astype(np.float32) * mask + orig * (1.0 - mask)).astype(np.uint8)
                    writer.write(batch[idx])

                chunk_rendered_frames += len(batch)
                global_frame_idx += len(batch)
                del batch

            if writer is not None:
                writer.release()

            if not chunk_raw.is_file() or chunk_rendered_frames == 0:
                chunk_raw.unlink(missing_ok=True)
                break

            chunk_dur = chunk_rendered_frames / fps
            cmd = [
                ffmpeg_bin, "-y", "-i", str(chunk_raw),
                "-ss", f"{chunk_start_time:.3f}", "-t", f"{chunk_dur:.3f}", "-i", str(audio_path),
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest", str(chunk_synced),
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            chunk_raw.unlink(missing_ok=True)

            if res.returncode == 0 and chunk_synced.is_file():
                chunk_files.append(chunk_synced)
                logger.info(f"local_wav2lip_chunk: {chunk_synced.name} ({chunk_dur:.1f}s)")
            else:
                logger.warning(f"local_wav2lip_chunk_mux_failed: {chunk_synced.name}")

            chunk_idx += 1
            if total_frames > 0 and global_frame_idx >= total_frames:
                break

        cap.release()

        if not chunk_files:
            return self._fallback_passthrough(video_path, audio_path, out_path)

        concat_txt = chunk_dir / "concat_list.txt"
        with open(concat_txt, "w") as f:
            for c in chunk_files:
                f.write(f"file '{c.resolve().as_posix()}'\n")

        cmd_concat = [
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt), "-c", "copy", str(out_path),
        ]
        res_concat = subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res_concat.returncode != 0 or not out_path.is_file():
            logger.warning("local_wav2lip_concat_failed, using fallback")
            return self._fallback_passthrough(video_path, audio_path, out_path)

        try:
            import shutil
            shutil.rmtree(chunk_dir, ignore_errors=True)
        except Exception:
            pass

        logger.info(f"local_wav2lip_ok [chunks={len(chunk_files)}, CPU]: {out_path.name} ({out_path.stat().st_size} B, $0.00)")
        return out_path

    def _fallback_passthrough(self, video_path: Path, audio_path: Path, out_path: Path) -> Path:
        ffmpeg_bin = get_ffmpeg_binary()
        cmd = [
            ffmpeg_bin, "-y", "-i", str(video_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path),
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_path


local_wav2lip_adapter = LocalWav2LipAdapter()
__all__ = ["LocalWav2LipAdapter", "local_wav2lip_adapter"]
