"""Reusable Aspect Ratio, Framing, and CinemaScope Letterboxing Filters for FFmpeg."""


def build_framing_filter(aspect_ratio: str = "16:9", target_res: tuple[int, int] = (3840, 2160), enable_cinemascope: bool = False) -> str:
    """Construct FFmpeg filter chain for resolution scaling, pixel aspect ratio, and optional 2.39:1 CinemaScope bars."""
    w, h = target_res
    base_scale = f"scale={w}:{h}:flags=lanczos,setsar=1"
    if not enable_cinemascope or aspect_ratio != "16:9":
        return base_scale

    # 2.39:1 CinemaScope matte calculation (e.g. 3840 x 1606 active image inside 3840 x 2160 canvas)
    scope_height = int(w / 2.39)
    bar_height = (h - scope_height) // 2
    matte_filter = f"drawbox=y=0:h={bar_height}:color=black:t=fill,drawbox=y={h - bar_height}:h={bar_height}:color=black:t=fill"
    return f"{base_scale},{matte_filter}"


__all__ = ["build_framing_filter"]
