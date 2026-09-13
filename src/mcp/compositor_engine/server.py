"""Compositor Engine MCP Server for single-pass FFmpeg compilation and video QA auditing."""

from pathlib import Path
from typing import Any
from src.compositor.ffmpeg_pipeline import build_single_pass_command
from src.compositor.timeline import compile_timeline_from_scenes
from src.mcp.base import MCPServerBase
from src.scripts.local_video_qa import run_video_qa_audit

server = MCPServerBase(server_name="mcp-compositor-engine", version="1.0.0")


async def compile_filter_complex(
    scenes: list[dict[str, Any]],
    output_mp4: str = "master.mp4",
) -> dict[str, Any]:
    """Compile single-pass -filter_complex FFmpeg command line from scene track layout."""
    timeline = compile_timeline_from_scenes(scenes)
    cmd = build_single_pass_command(timeline, output_path=output_mp4)

    # Extract filter complex string from cmd array
    fc_str = ""
    for i, part in enumerate(cmd):
        if part == "-filter_complex" and i + 1 < len(cmd):
            fc_str = cmd[i + 1]
            break

    return {
        "command": cmd,
        "filter_complex_graph": fc_str,
        "total_scenes": len(timeline.scenes),
        "total_duration_seconds": timeline.total_duration_seconds,
        "output_path": str(output_mp4),
        "is_single_pass": True,
    }


async def audit_rendered_mp4(
    video_path: str,
    duration_seconds: float = 12.0,
) -> dict[str, Any]:
    """Audit rendered MP4 for broadcast compliance (EBU R128 -14 LUFS and defects)."""
    report = run_video_qa_audit(video_path, duration_seconds=duration_seconds)
    return {
        "video_path": video_path,
        "passed": report.passed,
        "composite_score": report.scores.composite_score,
        "quality_tier": report.scores.quality_tier,
        "loudness": {
            "integrated_lufs": report.loudness.integrated_lufs,
            "true_peak_dbtp": report.loudness.true_peak_dbtp,
            "target_lufs": report.loudness.target_lufs,
            "passed": report.loudness.lufs_passed,
        },
        "defects": {
            "black_frame_seconds": report.defects.black_duration_seconds,
            "frozen_frame_seconds": report.defects.frozen_duration_seconds,
            "passed": report.defects.defects_passed,
        },
    }


server.register_tool(
    name="mcp_compile_filter_complex",
    description="Compile single-pass FFmpeg -filter_complex command with pan-zoom, ducking, and captions",
    input_schema={
        "type": "object",
        "properties": {
            "scenes": {"type": "array", "description": "List of scene layout objects"},
            "output_mp4": {"type": "string", "default": "master.mp4"},
        },
        "required": ["scenes"],
    },
    handler=compile_filter_complex,
)

server.register_tool(
    name="mcp_audit_rendered_mp4",
    description="Audit rendered MP4 file for EBU R128 -14 LUFS loudness and frame defects",
    input_schema={
        "type": "object",
        "properties": {
            "video_path": {"type": "string", "description": "Path to master MP4 file"},
            "duration_seconds": {"type": "number", "default": 12.0},
        },
        "required": ["video_path"],
    },
    handler=audit_rendered_mp4,
)

if __name__ == "__main__":
    server.run_cli()
