"""Reusable Cross-Scene Environmental State and Physical Continuity Tracker."""

from typing import Any


class EnvironmentalStateTracker:
    """Tracks cumulative physical changes (wetness, snow accumulation, lighting progression) across scenes."""

    def compute_scene_environmental_state(
        self,
        scene_index: int,
        total_scenes: int,
        weather: str = "clear_daylight",
        space: str = "outdoor",
    ) -> dict[str, Any]:
        """Compute cumulative physical wetness and environmental state for scene prompt enhancement."""
        w_low = weather.lower()
        is_rain = any(k in w_low for k in ("rain", "monsoon", "downpour", "drizzle", "storm"))
        is_snow = any(k in w_low for k in ("snow", "blizzard", "winter"))

        if space.lower() == "indoor" or not (is_rain or is_snow):
            return {"wetness_level": "dry", "environmental_prompt": ""}

        # Calculate progression
        ratio = (scene_index + 1) / max(1, total_scenes)

        is_light = any(k in w_low for k in ("light", "drizzle", "gentle", "soft", "mist"))
        is_heavy = any(k in w_low for k in ("heavy", "downpour", "storm", "deluge", "torrential", "monsoon", "thunderstorm"))

        if is_rain:
            if is_light:
                state = "lightly_misted"
                desc = "clothing and hair lightly misted with delicate micro water droplets, soft damp sheen"
            elif is_heavy:
                if ratio < 0.40:
                    state = "moderately_wet"
                    desc = "clothing wet with visible water droplets and rain sheen, damp clinging hair"
                else:
                    state = "soaked_drenched"
                    desc = "clothing heavily rain-drenched with water streaming off fabric, dripping wet hair"
            else:
                if ratio < 0.35:
                    state = "lightly_misted"
                    desc = "clothing and hair lightly misted with fine water droplets"
                elif ratio < 0.70:
                    state = "moderately_wet"
                    desc = "clothing damp with glistening rain sheen, hair wet with clinging strands"
                else:
                    state = "soaked_drenched"
                    desc = "clothing heavily rain-drenched with water streaming off fabric, wet hair with water droplets"
            return {"wetness_level": state, "environmental_prompt": desc}

        if is_snow:
            if ratio < 0.50:
                state = "light_frost"
                desc = "fine crystalline frost on coat shoulders and beanie"
            else:
                state = "snow_dusted"
                desc = "shoulders and collar dusted with fresh white snow powder"
            return {"wetness_level": state, "environmental_prompt": desc}

        return {"wetness_level": "dry", "environmental_prompt": ""}


environmental_state_tracker = EnvironmentalStateTracker()

__all__ = ["EnvironmentalStateTracker", "environmental_state_tracker"]
