# CineAI Studio - Production Tier, SLA & Customer Pricing Matrix

This document provides the authoritative, empirically calibrated reference for internal production costs (COGS), customer credit consumption, delivery turnaround SLAs, and credit top-up packages.

---

## 1. Production Package & Service SLA Matrix

| Package Tier | Target Duration | Expected Delivery SLA | Customer Price | Credits | Internal COGS | Quality & Technical Specification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Shorts / Reels Ultra** | **15 sec** | **~1.5 – 2.5 mins** | **$1.65** | 165 | ~$0.55 | **4K UHD (3840×2160)**, 60 fps motion, Leica 24mm wide optics, 48kHz procedural Foley, Kodak 2383 3D color grade |
| **Viral Hook Clip** | **30 sec** | **~3.0 – 4.5 mins** | **$3.25** | 325 | ~$1.10 | **4K UHD**, 30/60 fps story-driven FPS, Arri 50mm lenses, multi-location transitions, custom Suno commercial music |
| **Full YouTube Short** | **60 sec** | **~5.5 – 7.5 mins** | **$6.50** | 650 | ~$2.20 | **4K UHD**, 3-Act tension pacing curve, continuous environmental wetness tracking, timed multi-language subtitles |
| **Mini-Story / Commercial** | **120 sec** *(2 min)* | **~10 – 14 mins** | **$12.50** | 1,250 | ~$4.40 | **4K UHD**, 4 location hubs, full cinematic score with -18 dB voice ducking, YPP monetization safety compliance |
| **Blue-Chip Documentary / Tour** | **300 sec** *(5 min)* | **~25 – 30 mins** | **$29.00** | 2,900 | ~$11.00 | **4K UHD @ 24/60 fps**, BBC/NatGeo style sweeping cinematography, atmospheric Foley, full evidence bundle |

---

## 2. Customer Top-Up Credit Packs

*Standard conversion rate: **100 Credits = $1.00 USD** ($0.01 per Credit)*

| Top-Up Pack | Price (USD) | Credits Issued | What Customer Can Produce | Internal Production Cost | Gross Margin |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **Starter Top-Up** | **$10.00** | **1,000** | **6× 15-Sec 4K Videos** *(or 3× 30s Videos)* | ~$3.30 | **67.0% Margin ($6.70 Profit)** |
| **Creator Pack** | **$29.00** | **3,200** | **20× 15-Sec 4K Videos** *(or 5× 60s Videos)* | ~$9.50 | **67.2% Margin ($19.50 Profit)** |
| **Studio Pro Pack** | **$99.00** | **12,000** | **75× 15-Sec 4K Videos** *(or 20× 60s Videos)* | ~$32.00 | **67.7% Margin ($67.00 Profit)** |

---

## 3. Database Persistence & Automated Self-Calibration

Every time a video is rendered:
1. **Model Spend Actuals** are calculated across all categories (Gemini tokens, FLUX keyframes, Kling video motion, Azure Speech chars, Suno tracks, Foley stems, and FFmpeg compute).
2. **Turnaround Timing Metrics** (`total_pipeline_seconds` and `render_seconds`) are recorded in the database.
3. **Empirical Benchmarks Database**:
   - Local / Testing: SQLite (`storage/production_benchmarks.db`)
   - Cloud Staging / Production: Azure / GCP PostgreSQL Flexible Server (`production_benchmarks` table with `pgvector` and `JSONB` support).
4. **Continuous Learning**: The system computes moving averages for cost-per-second and turnaround-per-second to automatically adjust pre-flight estimates and customer delivery SLAs on future runs.
