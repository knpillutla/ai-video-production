# ==============================================================================
# 🎬 AI Video Production Studio - Multi-Channel Execution Commands Cheatsheet
# ==============================================================================

# ------------------------------------------------------------------------------
# 🪵 1-SHOT NATURAL AUDIO LIVING WALLPAPERS (--shots 1 --no-bgm --prompt "...")
# Uses natural audio from Kling video directly (crackling fire, rain) without BGM ($2.10 total spend)
# ------------------------------------------------------------------------------
# Example 1: Natural Crackling Fireplace (No BGM, 100% Native Audio)
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --shots 1 --no-bgm --prompt "Rustic stone fireplace with burning oak logs, crackling flames and glowing orange charcoal embers" --photos-only
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id <episode_id> --shots 1 --no-bgm

# Example 2: Natural Rain on Cabin Window (No BGM)
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --shots 1 --no-bgm --prompt "Cozy library window with gentle raindrops trickling down glass, warm glowing reading lamp" --photos-only
python scripts/channels/study_focus_cafe_pipeline.py --id <episode_id> --shots 1 --no-bgm


# ------------------------------------------------------------------------------
# 🌟 COMPLETE 3-STAGE WORKFLOW (Earth Serenade: 4K Scenic Nature Sanctuaries)
# ------------------------------------------------------------------------------
# Stage 1: Generate 4K Keyframe Photos only ($0.20):
python scripts/channels/nature_sanctuary_pipeline.py --archetype swiss_alps --photos-only
# -> Outputs: Episode ID: ep_swiss_alps_1790365543

# Stage 2: Run with --id to generate Kling v3 4K Video Motion & Binaural Master:
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543
# -> Outputs 60s/120s master_4k_ambient.mp4 and sends approval email

# Stage 3: Instant 3-Hour Long-Play Stretch (~10s, $0.00 spend):
python scripts/channels/nature_sanctuary_pipeline.py --id ep_swiss_alps_1790365543 --auto-stretch --hours 3.0


# ------------------------------------------------------------------------------
# 🌙 COMPLETE 3-STAGE WORKFLOW (Silent Hearth: 8-Hour Deep Sleep Sanctuary)
# ------------------------------------------------------------------------------
# Stage 1: Generate 3 Keyframe Photos only ($0.15):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --primary blizzard --secondary camp_fire --photos-only
# -> Outputs: Episode ID: ep_blizzard_1790363895

# Stage 2: Run with --id for Kling v3 4K Motion & 432Hz Delta Master (3 shots min):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895
# -> Outputs 90s master_4k_ambient.mp4 and sends approval email

# Stage 3A: Fast Direct-Copy Stretch to 8 Hours (~10s, video loops entire 8h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0

# Stage 3B: Circadian Sleep Stretch with --sleep (Fades to OLED Black after 2.0h):
python scripts/channels/deep_sleep_sanctuary_pipeline.py --id ep_blizzard_1790363895 --auto-stretch --hours 8.0 --sleep


# ------------------------------------------------------------------------------
# ☕ COMPLETE 3-STAGE WORKFLOW (Rain & Quill: 3-Hour Focus Cafe Lounge)
# ------------------------------------------------------------------------------
# Stage 1: Generate 3 Focus Photos only:
python scripts/channels/study_focus_cafe_pipeline.py --primary beach_house --secondary rain --photos-only

# Stage 2: Run with --id for 4K Motion & Felt Piano Master:
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123

# Stage 3: Instant 3-Hour Long-Play Stretch (~10s):
python scripts/channels/study_focus_cafe_pipeline.py --id ep_beach_house_1790365123 --auto-stretch --hours 3.0


# ------------------------------------------------------------------------------
# ⚡ STANDALONE STRETCH COMMANDS (Stretch Any Pre-Rendered Master Directly)
# ------------------------------------------------------------------------------
# Direct Fast Stretch (3 Hours, ~10s):
python src/services/long_play_stretcher.py --input storage/channels/earth_serenade/ep_swiss_alps_1790365543/master_4k_ambient.mp4 --hours 3.0

# Direct Fast Stretch (8 Hours, ~10s):
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0

# Sleep Mode Stretch (8 Hours with 2h Fade-to-Black):
python src/services/long_play_stretcher.py --input storage/channels/silent_hearth/ep_blizzard_1790363895/master_4k_ambient.mp4 --hours 8.0 --fade-black 2.0
