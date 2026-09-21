"""Studio-Grade Cinematic Production System.

Modular package providing procedural spatial foley, film print LUT color science,
framing, narrative pacing curves, continuity tracking, and motion QA sentry.
"""

from src.cinematics.color.film_luts import FILM_LUT_PRESETS, resolve_film_lut
from src.cinematics.color.framing import build_framing_filter
from src.cinematics.continuity.environmental_state import EnvironmentalStateTracker, environmental_state_tracker
from src.cinematics.foley.foley_engine import FoleyEngine, foley_engine
from src.cinematics.pacing.tension_curves import calculate_scene_durations
from src.cinematics.qa.motion_sentry import MotionQASentry, motion_qa_sentry

__all__ = [
    "FoleyEngine",
    "foley_engine",
    "FILM_LUT_PRESETS",
    "resolve_film_lut",
    "build_framing_filter",
    "calculate_scene_durations",
    "MotionQASentry",
    "motion_qa_sentry",
    "EnvironmentalStateTracker",
    "environmental_state_tracker",
]
