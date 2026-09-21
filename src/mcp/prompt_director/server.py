"""Directorial Prompt MCP Server for dynamic context-specific instruction routing."""

import asyncio
from typing import Any
from src.core.telemetry import logger
from src.mcp.base import MCPServerBase
from src.mcp.prompt_director.directorial_router import (
    build_directorial_prompt,
    classify_directorial_mode,
)


class PromptDirectorMCPServer(MCPServerBase):
    """MCP Server providing contextual directorial prompts and modular instruction templates."""

    def __init__(self):
        super().__init__(server_name="mcp-prompt-director", version="1.0.0")
        self._register_tools()

    def _register_tools(self) -> None:
        self.register_tool(
            name="mcp_get_directorial_prompt",
            description="Dynamically select and build a lean, context-tailored directorial instruction prompt.",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Video theme or topic"},
                    "genre": {"type": "string", "description": "Genre category"},
                    "video_format": {"type": "string", "description": "Target video format"},
                    "style_name": {"type": "string", "description": "Visual art style name"},
                    "decorations": {"type": "string", "description": "Art style prompt decorations"},
                    "lighting": {"type": "string", "description": "Lighting scheme"},
                    "palette": {"type": "string", "description": "Color palette"},
                    "guidance": {"type": "string", "description": "Directorial guidance"},
                    "target_duration_seconds": {"type": "integer", "description": "Target video duration"},
                    "language": {"type": "string", "description": "Language code (e.g. te, hi, en)"},
                },
                "required": ["topic"],
            },
            handler=self._handle_get_directorial_prompt,
        )

    async def _handle_get_directorial_prompt(
        self,
        topic: str = "",
        genre: str = "comedy",
        video_format: str = "",
        style_name: str = "Broadcast 4K Photorealistic Cinematic",
        decorations: str = "",
        lighting: str = "",
        palette: str = "",
        guidance: str = "",
        target_duration_seconds: int = 60,
        language: str = "en",
        **kwargs: Any,
    ) -> dict[str, Any]:
        prompt, mode = build_directorial_prompt(
            topic=topic,
            genre=genre,
            video_format=video_format,
            style_name=style_name,
            decorations=decorations,
            lighting=lighting,
            palette=palette,
            guidance=guidance,
            target_duration_seconds=int(target_duration_seconds),
            language=language,
        )

        logger.info(f"mcp_prompt_director: mode='{mode}', prompt_length={len(prompt)} chars")
        return {
            "prompt": prompt,
            "mode": mode,
            "topic": topic,
            "genre": genre,
        }


prompt_director_server = PromptDirectorMCPServer()


async def get_directorial_prompt(
    topic: str,
    genre: str = "comedy",
    video_format: str = "",
    style_name: str = "Broadcast 4K Photorealistic Cinematic",
    decorations: str = "",
    lighting: str = "",
    palette: str = "",
    guidance: str = "",
    target_duration_seconds: int = 60,
    language: str = "en",
) -> dict[str, Any]:
    return await prompt_director_server._handle_get_directorial_prompt(
        topic=topic,
        genre=genre,
        video_format=video_format,
        style_name=style_name,
        decorations=decorations,
        lighting=lighting,
        palette=palette,
        guidance=guidance,
        target_duration_seconds=target_duration_seconds,
        language=language,
    )


if __name__ == "__main__":
    asyncio.run(prompt_director_server.run_stdio())
