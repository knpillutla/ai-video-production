---
name: nature-retreat-studio
description: Studio-grade 4K nature documentary, ambient soundscape, and biophilic retreat video production skill with 3-tier water dynamics, Suno acoustic scoring, and single-pass FFmpeg 4K mastering.
---

# Nature Retreat Studio Skill

Direct and produce broadcast-grade 4K UHD biophilic nature retreats, cozy soundscapes, and scenic walking tours with zero synthetic hiss and 100% YouTube monetization clearance. Built on and strictly adhering to the [ai-video-producer-core](file:///c:/neel-1/projects/content-generation/.agents/skills/ai-video-producer-core/SKILL.md) skill and the 4-Stage Progressive Quality Gate.

## Core Directives

1. **Photorealistic Cinematography (FLUX 1.1 Pro Ultra)**:
   - Full-frame 24mm/35mm prime lenses (Arri Alexa 35mm Master Prime).
   - Natural 5400K–5600K daylight. Strictly PROHIBIT artificial golden-hour lens flare blowouts, flat grey concrete, or washed-out lighting.
   - Zero human characters in pure nature/relaxation productions (`characters: []`).
2. **3-Way Ocean & Water Dynamics Strategy**:
   - **`water_impact_collision` $\rightarrow$ Kling v3 Pro ($0.280/s)**: Heavy cascading waterfalls plunging over rocks, white-water rapids, stormy coastal surf crashing against cliffs, splashing subjects.
   - **`water_fluid` $\rightarrow$ Alibaba Wan 2.1 ($0.080/s)**: Continuous smooth laminar rivers, meandering streams, gentle ocean swells, rain, canal flows.
   - **`landscape_solid` $\rightarrow$ Tencent Hunyuan Video 1080p ($0.075/s)**: Calm glassy glacial lakes, mirror fjords, solid mountain peaks, architectural facades.
3. **Pristine Broadcast Audio & Dynamic Caching**:
   - Audio must be 48,000 Hz 24-bit stereo at -14.0 LUFS.
   - Always check `AudioVault` first to reuse existing matching ambient stems ($0.00 cost).
   - Fall back on-the-fly to **MusicAPI.ai / Suno v3.5 Pro** with organic tags (`[ambient nature], crystal-clear mountain waterfall, soothing gentle water splash and babbling brook, soft acoustic meditative harp and bamboo flute, zero hiss, 48kHz broadcast master`).
4. **Single-Pass 4K Mastering**:
   - Master in 4K UHD (3840×2160 @ 24fps) at CRF 18 visually lossless via Lanczos filtering and `+faststart`.

## Workflow & CLI Commands

```bash
# Run standalone nature retreat generation
python -m src.studios.nature_retreat.retreat_agent --theme "Rainforest Waterfall Patio" --duration 20

# Run with custom scene count
python -m src.studios.nature_retreat.retreat_agent --theme "Japanese Zen Garden & Koi Pond" --scenes 4
```
