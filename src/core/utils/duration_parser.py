"""Deterministic Duration Parser Utility.

Parses human-readable duration strings into integer seconds.
Supports: '10', '10s', '30m', '1h', '1m30s', '45sec', '2hours', etc.
Defaults to seconds if no unit is provided.
"""

import re


def parse_duration(val: str | int | float | None, default_seconds: int = 10) -> int:
    """Parse a flexible duration input into an integer number of seconds.

    Examples:
        >>> parse_duration(20)
        20
        >>> parse_duration("10s")
        10
        >>> parse_duration("30m")
        1800
        >>> parse_duration("1h")
        3600
        >>> parse_duration("1m30s")
        90
        >>> parse_duration("45")
        45
        >>> parse_duration(None)
        10
    """
    if val is None:
        return max(1, int(default_seconds))
    if isinstance(val, (int, float)):
        return max(1, int(val))

    val_str = str(val).strip().lower()
    if not val_str:
        return max(1, int(default_seconds))

    if val_str.isdigit():
        return max(1, int(val_str))

    # Check composite or single units: hours, minutes, seconds
    total_seconds = 0
    matched = False
    units = [
        (r"(\d+(?:\.\d+)?)\s*h(?:our|ours)?", 3600),
        (r"(\d+(?:\.\d+)?)\s*m(?:in|ins|inute|inutes)?", 60),
        (r"(\d+(?:\.\d+)?)\s*s(?:ec|ecs|econd|econds)?", 1),
    ]

    for pattern, multiplier in units:
        match = re.search(pattern, val_str)
        if match:
            total_seconds += int(float(match.group(1)) * multiplier)
            matched = True

    if matched and total_seconds > 0:
        return total_seconds

    # Fallback attempt to parse standard float
    try:
        return max(1, int(float(val_str)))
    except ValueError:
        raise ValueError(
            f"Invalid duration format: '{val}'. Supported examples: '10', '10s', '30m', '1h', '1m30s'."
        )


__all__ = ["parse_duration"]
