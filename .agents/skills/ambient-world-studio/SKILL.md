---
name: ambient-world-studio
description: Studio-grade 4K Velvet Ambient World Producer covering 14 archetypes with Velvet Anti-Fatigue Acoustic Mastering, 24/7 YouTube Live Streaming, A/B Thumbnails, and Multi-Language SEO.
---

# Velvet Ambient World Studio

Unified 4K Ambient, Sleep, and Relaxation Studio covering **14 atmospheric archetypes** with **Velvet Anti-Fatigue Acoustic Mastering**, **24/7 YouTube Live Streaming**, **Circadian Fade-to-Black**, **9:16 Vertical Shorts**, **3-Variant A/B Thumbnails**, and **Multi-Language Global SEO**.

## Supported Atmospheric Archetypes

1. **Alpine & Mountain Sanctuary:** `swiss_alps`, `himalayas`, `mountains`
2. **Aquatic & Coastal Haven:** `ocean_world`, `lake`, `beach`, `beach_house`
3. **Forest & Seasonal Retreat:** `forest`, `autumn`, `winter`, `rain`
4. **Cozy Shelter & Hearth:** `camp_fire`, `blizzard`
5. **Deep Sleep & Celestial Zen:** `night_sleep`

---

## The Complete Production & Growth Suite

1. **Velvet Sound Engine:** -21.0 LUFS sleep mastering with 6.5kHz low-pass roll-off, 180Hz warmth boost, lookahead de-pop limiter, and 432Hz binaural delta wave (2.0 Hz) sleep entrainment.
2. **2-Phase AI Video Diffusion & Local Stretch Architecture:**
   - **Phase 1 (60s Master Video):** Synthesizes true generative AI video diffusion motion using **Wan 2.1** (water/rain/snow/ocean), **Kling 1.6 Pro** (fireplaces/waterfalls/steam), or **Hunyuan Video** (mountain landscapes/clouds).
   - **Phase 2 (Long-Play Expansion):** Locally loops the pristine 60s 4K master into 1h, 3h, or 8h broadcasts via single-pass FFmpeg stream-looping with $0 extra compute.
3. **Circadian Fade-to-Black:** Smooth transition to an OLED pure black screen after 1–2 hours for bedroom comfort while continuous audio plays for 8 hours.
4. **9:16 Shorts & TikTok Teasers:** Auto-extracts vertical teaser clips with typography hooks for top-of-funnel viral reach.
5. **3-Variant A/B Thumbnails:** Generates 3 distinct visual compositions (Interior POV, Expansive Sanctuary, Hearth Detail) for YouTube's Test & Compare tool.
6. **Multi-Language Global SEO:** Localizes titles, descriptions, and tags into Japanese, German, Spanish, Portuguese, French, and Korean.
7. **24/7 RTMP Live Broadcaster:** Streams continuous video loops directly to YouTube Live via RTMP with auto-reconnect resilience.

---

## CLI Production Examples

### 1. 8-Hour Sleep Master (Fades to Black after 2 Hours) + 9:16 Short Teaser
```bash
python -m src.studios.ambient_world.ambient_agent \
  --archetype swiss_alps \
  --long-play-hours 8.0 \
  --fade-to-black-hours 2.0 \
  --generate-short
```

### 2. Multi-Atmosphere Blend: Coastal Beach House with Forest Rain (3 Hours)
```bash
python -m src.studios.ambient_world.ambient_agent \
  --archetype beach_house \
  --secondary rain \
  --long-play-hours 3.0 \
  --generate-short
```

### 3. Launching a 24/7 YouTube Live Stream
```python
from src.services.live_stream_broadcaster import YouTubeLiveBroadcaster

broadcaster = YouTubeLiveBroadcaster(stream_key="YOUR_YOUTUBE_LIVE_STREAM_KEY")
process = broadcaster.broadcast_single_loop("storage/ambient_world/ep_swiss_alps/master_4k_ambient.mp4")
```
