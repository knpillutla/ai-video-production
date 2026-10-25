"""4K Multi-Camera Live Stadium Concert Studio.

Independent production studio for live stadium concert broadcasts across all languages.
Features:
- Exactly 1 character shot (Lead Singer Master) + 5 distinct concert elements
  (Instrument Macro, Live Orchestra, Overall Stadium Vista, Cheering Audience, Stage Pyro/Lightshow)
- Dynamic folder naming based on Gemini generated song title slug
- Script validation gate prompting user confirmation before generation
- Fail-fast Suno audio synthesis
"""

from __future__ import annotations

from src.studios.concert_studio.concert_producer import produce_concert_video
from src.studios.concert_studio.concert_setting_catalog import resolve_concert_setting
from src.studios.concert_studio.concert_style_catalog import resolve_concert_style
from src.studios.concert_studio.concert_workspace import resolve_concert_workspace

__all__ = [
    "produce_concert_video",
    "resolve_concert_setting",
    "resolve_concert_style",
    "resolve_concert_workspace",
]
