# AI Video Production Studio: Multi-Channel CLI & Stretch Cheatsheet

This cheatsheet contains all production and stretching commands for the automated YouTube channels, covering the 3-stage Human-in-the-Loop review workflow, Kling v3 4K Native diffusion, custom mood prompting (`--prompt "..."`), `--shots 1` single-scene living wallpapers, and ultra-fast long-play broadcast stretching.

---

## 📋 Channel Overview & Defaults

| Channel Name | Focus / Archetype | Master Set | Long-Play Target | Stretch Mode | Default Motion Model |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Earth Serenade** | 4K Scenic Nature Sanctuaries (`swiss_alps`, `mountains`, `ocean_world`) | 60s – 120s | 1.0 – 3.0 Hours | Direct Copy (~10s) | Kling v3 4K Native (`kling_v3`) |
| **2. Silent Hearth** | Deep Sleep & Insomnia (`blizzard`, `camp_fire`, `rain`) | 90s (3 shots min) | 8.0 Hours | Direct Copy (or `--sleep` for 2h fade) | Kling v3 4K Native (`kling_v3`) |
| **3. Rain & Quill** | Study, Focus & Ambience (`beach_house`, `cafe`, `rain`) | 90s (3 shots) | 3.0 Hours | Direct Copy (~10s) | Kling v3 4K Native (`kling_v3`) |

---

## 🔥 Single-Shot + Custom Mood Prompting (`--shots 1 --prompt "..."`)

Ideal for winter evenings, fireplace living wallpapers, or specific scenic aesthetics where you want **only 1 uninterrupted hypnotic shot** matching your custom direction ($2.10 total API spend):

```powershell
# Example 1: Cozy Stone Fireplace (1 Shot, Burning Oak Logs & Embers)
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --shots 1 --prompt "Rustic stone fireplace with burning oak logs, crackling flames and glowing orange charcoal embers" --photos-only
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id <episode_id> --shots 1

# Example 2: Swiss Alps Glacial Stream (1 Shot, Pure Crystalline Water Ripples)
python scripts/channels/nature_sanctuary_pipeline.py --archetype swiss_alps --shots 1 --prompt "Crystalline turquoise glacial mountain stream flowing over smooth pebbles with towering snow peaks in background" --photos-only
python scripts/channels/nature_sanctuary_pipeline.py --id <episode_id> --shots 1

# Example 3: Rain on Library Window (1 Shot, Warm Armchair & Raindrops)
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --shots 1 --prompt "Cozy library window with raindrops trickling down glass, warm glowing reading lamp and steaming ceramic tea cup" --photos-only
python scripts/channels/study_focus_cafe_pipeline.py --id <episode_id> --shots 1
```

---

## 1. Complete 3-Stage Human-in-the-Loop Workflow

### A. Channel 1: Earth Serenade (@EarthSerenade4K)

```powershell
# Stage 1: Generate 4K Keyframe Photos only ($0.20):
python scripts/channels/nature_sanctuary_pipeline.py --archetype swiss_alps --photos-only
# Output: Episode ID: ep_swiss_alps_1790365543

# Stage 2: After reviewing photos, synthesize Kling v3 4K Motion & Binaural Master:
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543
# Output: 60s/120s master_4k_ambient.mp4 + review notification

# Stage 3: Instant 3-Hour Long-Play Stretch (~10 seconds, $0.00 spend):
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543 --auto-stretch --hours 3.0
```

---

### B. Channel 2: Silent Hearth (@SilentHearthSleep)

```powershell
# Stage 1: Generate 3 Keyframe Photos only ($0.15):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --photos-only
# Output: Episode ID: ep_blizzard_1790363895

# Stage 2: After reviewing photos, synthesize Kling v3 4K Motion & 432Hz Delta Audio (3 shots min):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895
# Output: 90s master_4k_ambient.mp4 + review notification

# Stage 3 Option 1: Ultra-Fast Direct Copy Stretch to 8 Hours (~10 seconds, video loops entire 8h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0

# Stage 3 Option 2: Circadian Sleep Stretch with --sleep (Fades to OLED Pure Black after 2.0h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0 --sleep
```

---

### C. Channel 3: Rain & Quill (@RainAndQuill)

```powershell
# Stage 1: Generate 3 Focus Keyframe Photos only:
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --photos-only
# Output: Episode ID: ep_beach_house_1790365123

# Stage 2: Synthesize Kling v3 4K Motion & Felt Piano Master:
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123
# Output: 90s master_4k_ambient.mp4 + review notification

# Stage 3: Instant 3-Hour Long-Play Stretch (~10 seconds):
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123 --auto-stretch --hours 3.0
```

---

## 2. Standalone Long-Play Stretcher Commands

To stretch any pre-rendered `master_4k_ambient.mp4` directly without re-running pipeline scripts:

```powershell
# Fast Direct-Copy Stretch to 3 Hours (~10 seconds):
python src/services/long_play_stretcher.py --input storage/channels/earth_serenade/ep_swiss_alps_1790365543/master_4k_ambient.mp4 --hours 3.0

# Fast Direct-Copy Stretch to 8 Hours (~10 seconds):
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0

# Sleep Mode with 2-Hour Circadian Fade-to-Black:
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0 --fade-black 2.0
```

---

## 3. Multi-Channel Network Manager (Run All in Parallel)

```powershell
python scripts/channels/channel_network_manager.py --channel all
```
