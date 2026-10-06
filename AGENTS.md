# Antigravity Workspace Rules: AI Video Producer Studio

All AI agents working within this workspace must adhere strictly to the engineering standards defined below and detailed in [AGENT_INSTRUCTIONS.md](file:///c:/neel-1/projects/content-generation/AGENT_INSTRUCTIONS.md).

## Non-Negotiable Directives

### 1. Token Economy & Model Tiering
* **Tier 0 (Local Scripts):** Never call an LLM for operations that can be solved deterministically with Python, Regex, NumPy, or FFmpeg (e.g., regex profanity filtering, SRT/VTT caption formatting, volume ducking math, cosine similarity, or YouTube API payload building).
* **Tier 1 (Fast Models - `flash` / `gpt-4o-mini`):** Used for lightweight tasks like JSON schema extraction, keyword/tag generation, transcription cleanup, and title variations.
* **Tier 2 (Flagship Models - `pro` / `sonnet`):** Reserved strictly for creative retention scriptwriting, cultural transcreation (Telugu comedic timing, Hindi idioms), and nuanced monetization safety arbitration.
* **Model Selector MCP Server:** Route all model choices through the Model Selector MCP server (`mcp_select_best_model`) across all categories (scripting, multilingual TTS, visuals, video motion, lipsync, BGM, SFX) based on cost, quality, and language fluency rather than hardcoding models.
* **Minified Output:** Enforce strict structured output (JSON/Pydantic). Reject conversational preamble.
* **Context Pruning:** Slice and feed only the minimum required tokens into prompts.

### 2. Code Performance Optimization
* **Asynchronous Non-Blocking I/O:** Use `async`/`await` for all network requests (Azure Blob Storage, YouTube Data API, LLM/TTS endpoints) and disk I/O. Use `asyncio.gather()` or `TaskGroup` to run independent tasks concurrently (e.g., multilingual voice stems).
* **Streaming Media (Zero RAM Bloat):** Never load large video or audio files directly into memory (`file.read()`). Stream in chunks or use memory-mapped buffers.
* **Single-Pass FFmpeg:** Combine transitions, overlays, audio ducking, and captions into a single `-filter_complex` execution. Never chain sequential re-encodings.
* **Vectorized Math & Connection Pooling:** Use NumPy for vector distance calculations and reuse persistent `httpx.AsyncClient` instances across requests.

### 3. Reusable Deterministic Scripts & Universal Artifact Caching
* Recurring tasks must be implemented as standalone, reusable Python scripts located in `scripts/` or modular service utilities.
* Cache assets and LLM outputs using SHA-256 prompt hashing to prevent redundant API expenditure.
* **Universal Artifact Caching & Idempotency Mandate (All Media Categories & All Channels):** Reuse created artifacts as much as possible; all production pipeline stages must be strictly idempotent. This rule applies universally across **ALL categories and ALL channels—images, references, backgrounds, scripts, songs, video, audio, lipsync, thumbnails, and composite renders**.
  - **Tier 1 (Local Disk Check):** If an artifact file already exists on disk and is non-empty (>1000 bytes) for that project/episode/task, **we MUST NOT create or call external models again**.
  - **Tier 2 (In-Flight Remote Request Resumption):** Persist in-flight asynchronous request tokens (e.g. FAL `request_id`, Suno task IDs) to local JSON state (`fal_req_p*.json`). On script restart/resumption, poll existing pending requests before ever initiating a new paid API call.
  - **Tier 3 (AudioVault & Stem Cache Check):** Search `AudioVault` / local stem caches for matching musical genres/moods before dispatching new Suno synthesis.
  - **Tier 4 (Idempotent `--id` Resumption):** All studio agents and channel scripts across all genres MUST support `--id <episode_id>` to resume interrupted productions, synthesizing ONLY the missing artifacts while preserving completed ones.

### 4. Hard 300-Line Limit Per File
* **No code file may exceed 300 lines** (target 120–220 lines).
* When a file approaches 250 lines, refactor immediately by decomposing into single-responsibility sub-modules within dedicated packages.

### 5. Modular, Functional & Reusable Code
* Prefer pure functions without hidden side effects.
* Use explicit dependency injection for all external clients (storage, LLMs, APIs).
* Enforce typed Pydantic contracts for all domain data passed between boundaries.
* Ensure all pipeline steps are 100% idempotent and fail-fast: if an artifact exists, reuse it; if deleted or missing, recreate as required.

### 6. Zero Duplication & Single Source of Truth
* Never create or keep duplicate code, redundant utility functions, or overlapping `.md` documentation files.
* Maintain exactly one authoritative source file per domain. Delete or consolidate superseded drafts immediately.

### 7. Mandatory Pre-Flight Cost Transparency
* When a user submits a video for production from the UI, the system must first calculate and display the total estimated cost and an itemized breakdown (tokens, voice characters, images/clips, compute).
* Generation jobs must remain blocked until the user explicitly clicks the confirmation button.

### 8. Model Testing Safety & Cost Guard (Strict Ban on Bulk Tests & Strict Ban on Live Models in Automated Tests)
* **STRICT BAN ON RUNNING AUTOMATED TESTS WITH LIVE MODELS:** **NEVER run any automated test with live external models.** Automated tests must ALWAYS run 100% locally and offline with deterministic mocks, local fallbacks, and test fixtures to guarantee $0.00 API expenditure. Live external models (Gemini, Flux, Fal.ai, Suno, Azure Speech) must NEVER be invoked during automated test runs.
* **STRICT BAN ON RUNNING ALL TESTS:** **NEVER, EVER automatically run all tests.** Running full test suites (`pytest tests/` or bulk passes) consumes enormous CPU/time and poses accidental cost risks. Agents must **NEVER run all tests** unless explicitly and verbatim instructed by the user.
* **Targeted Single-Test Execution Only:** When verifying a code change, run **ONLY the single specific local test file or specific test function** related directly to that change (e.g., `pytest tests/test_specific.py -k test_target`).
* **Zero Paid Calls in Test Suite:** The test suite must ALWAYS run 100% locally with offline deterministic mocks/fallbacks. Even if paid API keys are present in `.env` or system environment, automated tests must NEVER call external AI models.



### 9. Mandatory Terraform-Only IaC
* **Always create Terraform scripts only for all cloud platforms** (Azure, GCP, AWS, Multi-Cloud).
* Never use Bicep, ARM templates, CloudFormation, or platform-specific template languages. Standardize on HashiCorp Terraform (`.tf`) files for 100% of infrastructure declarations.

### 10. Topic Deduplication, Autonomous Creative Auto-Pivot & Persistent Memory
* **Mandatory Persistence:** Every time a video is created, save the topic, metadata information (genre, tags, audience, format), and the final story synthesized from the script into the persistent Topic Memory vault.
* **Pre-Creation Duplicate Guard & Autonomous Pivot:** When a request matches an existing topic (cosine similarity $\ge 0.80$ or heavy metadata overlap), the agent MUST NOT produce duplicate content or crash. Instead, the agent alerts the user of the conflicting episode, **autonomously generates a differentiated unique angle (new sub-location, time-of-day, or atmospheric fusion)** within that niche, and **seamlessly continues its production loop** until a novel, high-CTR master video is successfully created.


### 11. Mandatory YouTube Partner Program (YPP) Monetization-Safe Content Standards
* **Anti-Demonetization Narrative Guard (No Ambient-Only Loops):** Never produce silent, uncurated, or static ambient/nature loops without substantial narrative or editorial value. All scenic, travel, or ambient-style productions MUST incorporate scripted voiceover commentary, educational trivia, or cultural storytelling (via TTS narration and timed subtitles) to satisfy YouTube's strict editorial transformation criteria and avoid "Reused / Repetitive Content" demonetization.
* **100% Commercial Master Rights (Zero Content ID Claims):** Never scrape, sample, or re-upload third-party commercial audio tracks or copyrighted video clips. All BGM and soundtracks must be generated via commercially cleared AI engines (e.g., Suno v3.5 Pro with full commercial master rights) or local procedural DSP audio stems to guarantee zero Content ID strikes or revenue sharing.
* **AdSense Advertiser-Friendly Compliance (Green Dollar Guarantee):** Run all scripts, lyrics, and metadata through `local_compliance.py` across YouTube's 11 advertiser-unfriendly categories. For mass folk, dance, or comedic content, ensure lyrical themes and choreographic prompts remain strictly within family-friendly / advertiser-safe bounds to avoid yellow-dollar restricted ad placement.
* **Mandatory Synthetic Media Disclosure:** When publishing or preparing metadata via YouTube Data API v3 (`mcp-multi-publisher`), always set the synthetic/AI-generated content disclosure tag (`has_synthetic_media=True`) to maintain algorithmic trust and channel compliance.

### 12. Mandatory Character Physicality & Autonomous Contextual Wardrobe/Aesthetics Derivation
* **Default Physicality & Age (Balanced Fit Build):** All main characters (both male and female) MUST have a **balanced, naturally fit, healthy medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves for women, lean-athletic fit build for men)**, strikingly beautiful / handsome, and in their **mid-20s (ages 23–27)** unless explicitly instructed otherwise by the user.
* **Autonomous Aesthetic & Wardrobe Derivation:** The user must NEVER be required to manually specify clothing, background aesthetics, color palettes, or set design. The system and story agents must **autonomously derive** these elements directly from the narrative beats, cultural context, and genre synthesized by Gemini.
* **Contextual Scene-Matched Outfits:** Outfits and wardrobe MUST dynamically and authentically match the context of the specific scenes of the story (e.g., festive village jathara -> vibrant traditional festive attire; modern IT office/WFH -> stylish smart-casual; rainy alpine trek -> functional stylish waterproof alpine outdoor wear; romantic evening -> elegant evening wear).

### 13. Natural Daylight Lighting & Realistic Human Walking Cadence Standards
* **Natural Daylight Over Artificial Yellow Flares:** Outdoor productions (village celebrations, dance, street scenes) MUST default to crisp, balanced natural daylight (5400K–5600K color temperature, natural sky, realistic balanced skin tones). Strictly prohibit artificial golden-hour lens flare blowouts, oversaturated amber tints, or monochromatic yellow washes.
* **Ultra-Slow Walking Tour Cadence (1.5–2 km/h):** First-person POV walking tours (e.g., Swiss Alps, heavenly village walks, city strolls) MUST be paced at an ultra-slow, tranquil, leisurely human walking cadence (~0.5 m/s / 1.5–2.0 km/h) with subtle steadycam sway, matching real-world 4K Swiss countryside slow walks. Never generate high-speed forward rushes, aggressive zooms, or drone-velocity translations that disrupt calm viewer immersion.

### 14. Mandatory Broadcast Video, Audio & Story-Driven Dynamic FPS Standards
* **Directorial Story-Driven FPS Selection:** Frame rates must never be arbitrary or hardcoded; Gemini MUST autonomously determine `recommended_fps` as part of the story and scene direction:
  - **24 fps:** Cinematic drama, narrative shorts, emotional dialogues, and slow romance (provides natural cinematic motion blur; prevents the artificial "soap opera" effect).
  - **30 fps:** Music videos, mass folk dance, upbeat choreography, and stage comedy (provides optimal temporal sharpness for fast footwork and spinning costumes while retaining cinematic cadence).
  - **60 fps:** First-person POV walking tours, fluid scenic landscape tracking, and action motion (eliminates pan judder and creates realistic physical immersion).
* **Broadcast Audio Standards:** All audio stems and final masters MUST be formatted to **48,000 Hz (48 kHz) 24-bit stereo**, encoded in **AAC at 256–320 kbps**, normalized to **-14.0 LUFS (±1.0 LUFS)** integrated loudness (True Peak < -1.0 dBFS, YouTube & EBU R128 standard), with deterministic ducking of BGM down by -18 dB to -22 dB during speech.
* **Visually Lossless 4K Video (CRF 22 Global Standard):** Master all final video deliveries and long-play broadcasts in **4K UHD (3840×2160 for 16:9, 2160×3840 for 9:16 Shorts)** at **CRF 22** (~12–14 Mbps) via single-pass FFmpeg, `preset veryfast`, `threads 4`, `yuv420p` pixel format, and `+faststart` MP4 metadata. This cuts 3-hour broadcast file sizes in half (from 28.5 GB down to ~14–18 GB) with zero visible loss on 4K OLED screens while accelerating YouTube cloud processing.

### 15. Mandatory Beat-Driven Choreographic Progression & Musical Alignment Standards
* **Gemini Lyrics & Scriptwriting Contract:** In all dance, song, and musical productions, **Gemini MUST create the structured script and rhyming lyrical verse / hook couplets** with metric cadence (*prasa*), rhythmic meter, and cultural authenticity. Never allow Suno or external models to hallucinate arbitrary lyrics without Gemini's structured direction.
* **Suno Music & Beat Composition from Lyrics:** **Suno composes the song, instrumentation, and beats directly based on Gemini's lyrics.** Suno MUST receive Gemini's exact generated lyrics in its `prompt` parameter along with musical tags (`tags: "[genre], [BPM], [instruments], [vocal_gender] vocals"`). Suno then synthesizes the musical arrangement, rhythm, drum transients, and singing performance directly aligned to those lyrics.
* **Strict Vocal Gender & Lead Performer Consistency:** The vocal gender passed to Suno MUST strictly match the gender of the on-screen lead performer (e.g., Male lead dancer -> `male vocals` / deep energetic hero vocals; Female lead dancer -> `female vocals`). Strictly prohibit pairing a male dancer with a female vocal track or vice versa.
* **Mandatory Facial Lip-Sync for Musical Dance (`fal-ai/sync-lipsync`):** On-screen singing/dancing lead characters in medium shots and close-ups MUST be processed through the avatar lip-sync pipeline (`fal-ai/sync-lipsync` or `fal-ai/live-portrait`) driven by the Suno vocal track stem, ensuring the mouth moves in authentic synchronization with the sung lyrics.
* **Strict Ban on Hardcoded or Cached Audio Reuse Across Different Productions:** Never hardcode, recycle, or reuse audio stems across different productions (e.g. reusing legacy test audio like `surrumantadiro_song.mp3`). Every distinct production must use freshly composed Gemini lyrics and Suno music tailored to the episode topic.
* **Song Reusability During Iterative Video Improvements (No Duplicate Songs):** When testing and iterating on the same video/episode for visual, prompt, or editorial improvements, if a Suno song has already been created and exists on disk for that specific video project, NEVER invoke Suno again. Always reuse the existing synthesized song stem to prevent redundant API expenditures and unwanted duplicate song variations.
* **Musical Choreographic Progression (Anti-Monotony Guard):** Every dance production (folk, mass, classical, hip-hop, pop) must dynamically change its visual choreography in lockstep with the musical shifts of the song. Prohibit single, static dance loops that repeat across an entire track.
* **Three-Phase Musical-Choreography Mapping:**
  - **Phase 1: Rhythm Setup / Intro:** Swagger walk forward, rhythmic shoulder shrugs, subtle hip sway, teasing facial expressions (*abhinaya*).
  - **Phase 2: Lyrical Verse / Transitions:** Expressive narrative hand gestures matching lyrics, half-turn spins, call-and-response interactions with background troupe.
  - **Phase 3: The Beat Drop / Signature Hook:** High-intensity signature hook step—vigorous synchronized foot-stomping, rapid waist twists, spinning *chakkars* with whirling skirts, and explosive troupe jumps.
* **Deterministic Beat Alignment & Snapping:** Run audio through `LocalBeatDetector` (`local_beat_detector.py`) to compute BPM, downbeats, and drops. Scene transitions MUST snap directly to musical downbeats (`align_scene_cuts_to_beats`) so choreographic shifts hit precisely on kick drum transients.
* **Gemini Directorial Choreography Prompts:** Gemini's storyboard scenes must explicitly specify choreographic intensity tags (`intro_groove`, `verse_acting`, `beat_drop_hook`) and distinct physical steps for each musical beat.
* **Zero Spoken Narration in Dance Videos (Musical Lip-Sync Only):** In musical and dance videos, the character must NEVER speak spoken narrative text, video titles, or prompt descriptions. Lip-sync synchronization MUST be driven directly by the musical song track and sung lyrics (Suno stem), preserving 100% of the instrumentation, rhythm, and festive singing. Spoken dialogue TTS is strictly prohibited in dance music productions.

### 16. Mandatory Story-Driven Multi-Location Progression & Camera-Matched Background Depth
* **Multi-Location Hubs for Long-Form Songs (Anti-Static Set Guard):** In full songs (e.g., 2–3+ minute productions), never anchor the entire video to a single static set. Gemini must autonomously derive and rotate across **3 to 4 distinct location hubs** matching the lyrical narrative (e.g., village bazaar street -> lush green paddy fields -> ancient banyan tree platform -> twilight fairgrounds).
* **Camera-Matched Optical Background Depth (Angle Consistency):** Within each location, backgrounds must authentically adapt to shot geometry and focal length:
  - **Wide Shot:** Expansive environmental panorama with deep depth-of-field capturing full background architecture and troupe formations.
  - **Medium Shot:** 50mm cinematic perspective with moderate natural background depth and subtle bokeh.
  - **Close-Up:** 85mm portrait framing with creamy optical bokeh ($f/1.4$) dissolving background elements into soft blur to maximize facial expression and lipsync focus.
  - **Low-Angle:** Ground-level upward perspective capturing ground dust, dancing feet, and towering sky/flags.
* **Autonomous Directorial Derivation:** The user must NEVER have to specify location transitions or focal depth; Gemini dynamically enriches each scene's `location_hub`, `shot_type`, and optical background descriptors directly from lyrics and musical energy.

### 17. Mandatory Blue-Chip Nature & Wildlife Documentary Standards (BBC / NatGeo Style)
* **Cinematic 24 fps Film Cadence:** Blue-chip nature documentaries must default to **24.0 fps** with natural cinematic motion blur to convey majestic scale, monumental timelessness, and avoid high-speed artificial video effects.
* **Sweeping Expansive Cinematography:** Prioritize slow forward aerial glides over pristine glacial waters, slow crane descents over granite peaks and ancient canopies, and deep optical depth-of-field. Strictly prohibit aggressive zooms, rapid panning, or shaky-cam translations.
* **Grand Orchestral Score & Natural Foley:** Combine a sweeping orchestral score (swelling strings, French horn fanfares, resonant cellos) with natural environmental foley (mountain wind whispers, rushing glacial streams, bird calls). Enforce deterministic -18 dB sidechain ducking during speech with 2–3s musical breathing spaces between narration beats.
* **Authoritative Measured Narration:** Narration must be poetic, educational, and paced deliberately (~120–130 wpm) with rich geographical, ecological, and geological lore (guaranteeing YPP monetization safety).

### 18. Mandatory Mountain & Extreme Climate Survival Documentary Standards (BBC Human Planet / NatGeo Style)
* **Visceral Atmospheric Realism:** Capture the existential contrast between harsh unforgiving nature and human endurance. Exterior scenes must depict sub-zero blizzards, wind gusts carving powder drifts, desolate stone shelters, frost-crusted wood, and resilient shepherds guiding livestock. Interior scenes feature low-lit shelters, glowing hearth embers, boiling brass tea kettles with rising steam, and weathered, dignified faces.
* **Cinematic 24.0 fps Film Cadence:** Default strictly to **24.0 fps** with authentic motion blur to convey the heavy, monumental drift of snowstorms and deliberate human struggle.
* **Procedural Survival Foley & Sparse Melancholic Acoustic Score:** Layer authentic sub-zero wind howling, boots crunching deep snow, and fire embers with sparse traditional acoustic strings (e.g., rubab, mountain flute, low cello drone).
* **Authoritative Poetic Narration (YPP Anti-Demonetization Guard):** Deliver deliberate measured voiceover (~110–125 wpm) weaving survival tactics, nomadic culture, and geography to provide educational transformation and avoid YouTube's "Repetitive Content" demonetization.

### 20. Mandatory Natural Water Dynamics, Ocean Strategy & Fluid Physics Standards
* **Linear Flow Vector Alignment:** In rivers, streams, waterfalls, and ocean waves, always align camera motion parallel to the natural fluid velocity vector (e.g., slow forward glide looking downstream/shoreward, or slow pull-back looking upstream). Strictly prohibit contradictory perpendicular camera panning that confuses diffusion fluid displacement fields.
* **Smooth Glassy Laminar Currents (Zero Frozen Splash Splatter):** Image prompts for water surfaces must mandate continuous flowing glassy currents, natural ripples, rolling swells, and specular water reflections. Strictly prohibit chaotic frozen mid-air splash droplets, heavy static foam blobs across boulders, or turbulent spray that causes AI video diffusion models to produce melting foam or gelatinous water artifacts.
* **Mandatory Fluid Negative Tokens:** Video motion prompts must inject explicit fluid negative constraints (`"gelatinous water, melting foam, static frozen water, boiling water artifacts, rubbery water, unnatural foam blobs, zero static vertical streaks, zero falling wire artifacts"`).
* **3-Way Ocean & Water Model Strategy:**
  1. *Heavy Crashing Waterfalls, Plunging Cascades & Violent Rapids (`water_impact_collision`):* Route to **Kling v3 Pro** ($0.280/s) for high volumetric momentum, dynamic splash mist plumes, and avoidance of "falling wire/streak" artifacts.
  2. *Smooth Rivers, Laminar Streams, Gentle Rain & Ocean Swells (`water_fluid`):* Route to **Alibaba Wan 2.1** ($0.080/s) for accurate 3D liquid surface displacement, specular light glints, and natural rolling waves.
  3. *Calm Glassy Fjords & Mirror Lake Reflections (`landscape_solid`):* Route to **Tencent Hunyuan Video 1080p** ($0.075/s) for needle-sharp rock/tree reflections and rock-solid temporal stability.
  4. *Subject Interacting with Water (`wildlife_animal` / `human_action`):* Route to **Kling v3 Pro** ($0.280/s) for biological swimming kinematics, breaching marine life, or splashing characters.

### 21. Mandatory Consultative Alignment & Feedback First (No Premature / Blind Code Edits)
* **Feedback & Advice First:** When the user shares an idea, request, architectural preference, or direction, the agent must **first provide thoughtful feedback, engineering analysis, trade-off evaluation, and professional advice BEFORE making any code, file, or configuration changes**.
* **Co-Finalization Before Action:** Discuss the approach, pros, cons, edge cases, and alternatives with the user. Finalize the exact plan based on the user's intent combined with the agent's advice, and proceed with code modifications only once aligned.
* **Zero Premature Assumptions:** Never blindly jump to modify codebases, alter configurations, or create unilateral scripts without first consulting and aligning on the finalized decision with the user.

### 22. Mandatory 4-Stage Progressive Quality Gate & Cost Guard (All Production Pipelines & Studio Agents)
All studio agents, generation pipelines, and scratch production scripts must strictly enforce the **4-Stage Progressive Quality Gate** to prevent wasted time, unnecessary API spend, and flawed renders:
* **Stage 1: Pre-Flight Deduplication & Storyboard Gate:** Before generating any visual or video assets, verify topic uniqueness via Topic Memory (cosine similarity $\ge 0.80$ block) and review the Gemini storyboard structure, scene prompts, and itemized cost forecast.
* **Stage 2: Keyframe Image Quality Gate (FLUX 1.1 Pro Ultra):** Synthesize keyframe images first; inspect and approve before dispatching to video motion synthesis. Allow targeted single-scene image recreation or prompt tweaking ($0.06) rather than discarding an entire expensive video render ($1.40).
* **Stage 3: Audio & Soundtrack Gate (AudioVault & Suno v3.5 Pro):** Verify or retrieve matching 48kHz stereo audio from the AudioVault cache ($0.00 cost) or generate fresh Suno stems with full commercial rights and zero synthetic hiss.
* **Stage 4: Domain Video Motion & 4K Master Assembly:** Animate only approved keyframes using domain-specific models (Kling v3 Pro for waterfall/collisions, Wan 2.1 for laminar fluid, Hunyuan for solid vistas) and assemble visually lossless 4K master (CRF 18, -14 LUFS).

### 23. Mandatory 2-Phase AI Video Diffusion & Local Long-Play Stretch Architecture (All Agents & All Channels)
* **Phase 1 (Authentic AI Video Diffusion for Master Scenes):** Every production across all channels MUST synthesize genuine cinematic AI video diffusion motion for the initial master scenes using domain-optimized models (**Alibaba Wan 2.1** for water/rain/snow, **Kling v1.6 Pro** for fireplaces/mist/waterfalls, **Tencent Hunyuan Video** for mountain landscapes).
* **Phase 2 (Deterministic Zero-Cost Local Long-Play Stretched Broadcast):** Once the pristine 4K AI diffusion master is synthesized and approved, all long-play expansions (1h, 3h, 8h sleep broadcasts) MUST be generated locally using single-pass FFmpeg seamless stream looping (`-stream_loop`) with optional Circadian OLED fade-to-black.

### 24. Mandatory Autonomous Goal-Completion & Self-Healing Execution Loop (Zero Stalls / Zero Aborts)
* **Never Stalling or Giving Up:** AI agents within this studio must NEVER halt, crash, or abort prematurely when encountering recoverable edge cases (e.g. topic duplicates, API queue latencies, transient timeouts, or intermediate render retries).
* **Continuous Execution Loop:** An agent MUST autonomously self-heal (auto-pivot on duplicates, resume in-flight request IDs on timeout, auto-regenerate failed shots) until the verified final 4K video is rendered.

### 25. Mandatory Directorial Decision & Cache Transparency Logging (All Agents & Studios)
* **Explicit Rationale for Every Action:** Every agent, studio producer, and pipeline stage MUST log the complete rationale for its decisions in telemetry and console output:
  - **Storyboard Decisions:** Log why a specific duration (e.g., 120s vs 60s) and shot count (e.g., 4 vs 2 shots) were selected based on the archetype/cluster context.
  - **Cache vs. Invocation Transparency:** Explicitly declare `CACHE HIT` (with filename, local path, and similarity score) or `CACHE MISS -> INVOKING [MODEL]` with the reason why fresh synthesis is required.
  - **Audio & Suno Invocations:** If Suno is called, explicitly log why an existing AudioVault stem was not reused (e.g. `AudioVault checked (0 matching stems >= 0.70 similarity) -> Invoking Suno v3.5 Pro for fresh [genre] soundscape`).
  - **Motion Routing:** For every scene, log the model choice and why it was routed (e.g. `Wan 2.1 for laminar river currents` or `Kling 1.6 Pro for campfire embers`).

### 26. Mandatory Extended Perspective Hold & YouTube-Compliant Monotonic Long-Play Standards (All Relaxation Channels)
* **60s Extended Perspective Hold (Anti-Fatigue Standard):** In all multi-shot ambient, nature, and relaxation productions, each scenic perspective MUST linger peacefully for **60.0 seconds (1 full minute)** before transitioning via a slow **2.0-second cross-dissolve**. Rapid cycling (e.g. 5–10s scene cuts) causes cognitive arousal and visual fatigue and is strictly prohibited for relaxation and sleep broadcasts.
* **Forward-Flowing Continuous Cineloop Engine (Zero Reverse / Zero Seam Jumps):** All short AI video diffusion clips (5s/10s) must be transformed via `build_seamless_forward_cineloop` (1.2s head-to-tail forward cross-fade with `format=yuv420p`) prior to hold assembly. This guarantees water, rain, mist, and smoke **ALWAYS flow in their natural forward direction 100% of the time** while dissolving loop boundaries with **zero seam jump cuts, zero flicker, and zero backward flow**.
* **YouTube Ingest Compliance (Monotonic Timestamps & CRF 22):** All long-play stretch broadcasts (1h, 3h, 8h) MUST encode with continuous, monotonically increasing DTS/PTS timestamps (`-preset veryfast -threads 4 -crf 22 -c:a aac -b:a 320k -movflags +faststart`) to eliminate timestamp discontinuities across loop boundaries and guarantee 100% YouTube cloud ingest compliance with zero "Processing abandoned" errors.

### 27. Mandatory Agentic Context Enrichment & Gemini Directorial Scripting Standard (All Studios & Channels)
* **Never Dispatch Raw Prompts or Rely on Static Catalog Fallbacks:** An AI studio agent must NEVER blindly forward raw, sparse user prompt strings to image/video synthesis models, nor rely on static, generic hardcoded templates when custom topics are provided.
* **Autonomous Agentic Context Enrichment Before LLM Dispatch:** The specific studio agent for each domain (Ambient World, Cozy Ambiance, Healing Relaxation, Rain Retreat, Blue-Chip Nature / Wildlife, Mountain Survival, Dance Music, Comedy) must first autonomously enrich the narrative context with:
  - **Geographic & Environmental Lore:** Archetype-specific architectural styles, botany, geology, and authentic cultural materials (e.g. Bernese Oberland chalets, wooden shingle eaves, mist-shrouded limestone peaks).
  - **Atmospheric & Fluid Dynamics:** Specific fluid kinematics (e.g. gentle vertical rain streaks, water droplets glistening on timber eaves, specular puddle reflections, rising steam, chimney smoke).
  - **Strict 35mm Optical Specifications:** Focal length (24mm/35mm/50mm/85mm), depth-of-field, balanced 5600K daylight or warm interior lighting, neutral natural contrast.
  - **Proactive Negative Purity Tokens:** Mandatory proactive suppression of modern urban clutter, moving vehicles, vans, cars, trucks, asphalt roads, and crowds in natural/rural settings.
  - **Acoustic Scoring & Soundscape Tags:** Instruments, natural foley layers, BPM, and mood parameters.
* **Structured Gemini Screenplay & Storyboard Contract:** Dispatches the enriched context to Gemini LLM (`gemini-1.5-pro` / `gemini-2.0-flash`) via structured JSON schema to synthesize the full directorial storyboard: rich visual prompts ($\ge 130$ words), tailored motion dynamics prompts aligned to active diffusion engines (Wan 2.1, Kling 1.6 Pro, Hunyuan), camera framing, dynamic story FPS, and lyrical/narration scripts.
* **Transparent Logging & Episode Manifest Persistence:**
  - Every agent MUST log the exact prompt dispatched (`[GEMINI STORYBOARD REQUEST DISPATCHED]`) and the structured screenplay returned (`[GEMINI STORYBOARD RESPONSE RECEIVED]`).
### 28. Mandatory Anti-Fatigue Music & Video Motion Standards (All Relaxation Channels & Options)
* **Natural Gentle Micro-Kinematics (Water, Clouds, Flowers, Grass):** For all relaxation, sleep, meditation, ambient, nature, and cozy channels, environmental motion prompts MUST enforce tranquil, hypnotic, and organic micro-movements:
  - **Water Fluid:** Gentle continuous ripples, slow tranquil streams, soft expanding circular ripples from droplets (zero violent splashes, zero boiling waves).
  - **Clouds & Mist:** Slow, dreamy, continuous drifting clouds and soft mountain mist (zero fast storm rushes or jarring time-lapse jumps).
  - **Flowers & Foliage:** Delicate, rhythmic swaying of wildflowers and pine boughs in a faint, soothing mountain breeze (zero unnatural whipping).
  - **Grass & Lawns:** Subtle, gentle undulating wave motion across alpine meadows matching a light natural breeze.
* **Seamless Forward Stitching for Multi-Hour Stretched Broadcasts (1h, 3h, 8h):**
  - Because 5s/10s AI video clips are forward-crossfaded (`build_seamless_forward_cineloop` with 1.2s head-to-tail dissolve) and stretched into multi-hour living wallpapers, motion vectors MUST be constant, forward-directional, and seam-free.
  - Pacing must be locked tripod framing (or ultra-slow steadycam drift $\le 0.5$ m/s / 1.5 km/h) with 100% rock-solid background structures (chalets, mountains, rocks, architectural walls) so only the natural fluid elements gently move.
  - Strictly prohibit rapid panning, sudden zooms, fast object movements, erratic rotations, high-frequency camera jitters, or flashing/strobing lights that cause cognitive arousal or visual fatigue.
* **Zero Acoustic Ear Fatigue in Music & Foley:** Audio stems and musical scores for all relaxation productions MUST be mastered to velvet acoustic standards:
  - Soft, warm acoustic textures (432Hz tuning, warm piano, bamboo flute, Celtic harp, gentle cello/synth pads, binaural nature foley).
  - Strictly prohibit harsh high-frequency spikes (>8 kHz sharp sizzle/hiss), jarring percussion transients, loud claps of thunder, sudden dramatic volume shifts, repetitive sharp loops, or discordant intervals that trigger sensory arousal or ear fatigue during extended listening and sleep.
  - Master with gentle low-pass rolloff and normalized to -14.0 LUFS velvet integrated loudness.

### 29. Mandatory Relaxation Agent Creation Contract & Invariant Blueprint (Applied Every Time a Relax Agent is Created)
Every time a relaxation, ambient, nature, sleep, meditation, or cozy studio agent or pipeline is created or implemented, it MUST strictly adhere to this 5-point contract:
1. **Natural Micro-Kinematics Mandate:** Base prompts MUST explicitly instruct models to animate gentle movement for fluid water (soft ripples, tranquil streams, circular droplet ripples), drifting clouds/mist, gently swaying wildflowers/pine boughs, and undulating grass meadows.
2. **Seamless 3-Hour Forward-Stitching Guarantee:** All 5s/10s diffusion motion prompts MUST enforce locked framing, static structural backgrounds, and unidirectional motion vectors compatible with `build_seamless_forward_cineloop` (1.2s head-to-tail forward dissolve) for zero-seam multi-hour stretching.
3. **Anti-Fatigue Guardrails:** Explicitly prohibit rapid pans, abrupt zooms, high-frequency jitters, flashing lights, and harsh audio frequencies (>8 kHz sizzle/hiss, jarring drum hits, loud thunder) to guarantee zero visual and auditory fatigue.
4. **Mandatory Pure Nature Purity Guard (Zero Vehicles, Zero Humans, Zero Animals by Default):** Auto-enrich regional architecture, natural lighting (5400K daylight / warm amber glow), and proactive negative purity tokens (`zero humans, zero people, zero characters, zero crowds, zero cars, zero vehicles, zero vans, zero trucks, zero modern traffic, zero asphalt highways, zero modern clutter, zero animals, zero wildlife, zero birds, zero pets, zero livestock`) unless explicitly requested in the user's prompt.
5. **Directorial Screenplay & Manifest Contract:** Query Gemini LLM with structured JSON output, log dispatched prompt and response, and persist complete directorial decisions to `episode_manifest.json`.

### 30. Mandatory Genre-Specific Studio Platform (Strict Ban on Universal Platform, Schemas & Global Screenplay Caching)
* **Strict Ban on Universal Platform & Universal Schemas:** Never create, import, or maintain generic "universal" platform schemas, universal models, or universal directorial engines. The architecture is strictly **Genre-Specific**.
* **Self-Contained Genre Studios:** Every genre and studio category (Relaxation/Living Wallpapers, BBC Documentaries, Telugu Comedy, Mass Dance Music, Travel Walking Tours) MUST maintain its own dedicated, self-contained:
  - **Genre Schema Models** (e.g., `src/studios/ambient_world/relax_models.py` defining `RelaxScreenplay`, `RelaxSceneDirective`, `LoopStrategySpec`).
  - **Genre Directorial Prompt Builder** (e.g., `src/studios/ambient_world/ambient_directorial_prompt.py`).
  - **Genre Director Engine** (e.g., `src/studios/ambient_world/relax_director.py`).
* **Zero Cross-Genre Contamination:** Relaxation rules (such as Living Wallpaper framing, locked tripod, zero humans, 5500K uniform overcast daylight, cyclic loop crossfades) must never pollute global domain models or non-relaxation genres.
* **Fresh Screenplay Generation (Zero Global Screenplay Caching):** Screenplays are creative directorial outputs generated by Gemini Flash ($0.0001 cost, ~1s execution). Never cache screenplays globally across runs. Every production run must synthesize a fresh, creative, and distinct screenplay directly tailored to the user's concept. Caching is strictly reserved for downstream heavy media assets (images, audio stems, video diffusion renders) during `--id` episode resumption.

### 31. Mandatory 100% Autonomous Geographic & Ecosystem Derivation (Strict Ban on Hardcoded Templates, Regional Fallbacks & Geographic Vocabulary Contamination)
* **Zero Hardcoded Geographic Defaults or Fallbacks:** Never hardcode regional defaults (such as defaulting unmapped prompts to `"swiss_alps"` or hardcoding `"Glacial Alpine Valley"` in prompt builders or schema examples).
* **100% Autonomous Ecosystem & Landmark Derivation:** The directorial engine and prompt builder MUST instruct the LLM (Gemini) to **autonomously derive** all topographical, ecological, and cultural parameters directly from the user's prompt or chosen landmark:
  - `sub_genre`: Exact ecological category (e.g., `waterfall_gorge`, `river_canyon`, `coastal_ocean`, `alpine_mountains`, `temperate_forest`, `zen_waters`, `cozy_hearth`).
  - `continent_region`: True continent/region (e.g., `Great Lakes Basin / North America`, `Alpine Central Europe`, `Scandinavia / Arctic Fjords`).
  - `culture_heritage`: Authentic regional natural and conservation heritage.
  - `attraction_type`: Authentic geological/topographical structure (e.g., `River Escarpment & Waterfall Cascade`, `Glacial Fjord`, `Granite Canyon & Whitewater Rapids`).
  - `audio_master.suno_musical_tags`: Foley and musical textures strictly matching the authentic terrain (e.g., thunderous waterfall roar for waterfalls, ocean surf for coasts, mountain breeze for peaks).
* **Strict Ban on Vocabulary Contamination:** Never inject or permit vocabulary from one geographic archetype to contaminate another:
  - Strictly prohibit words like `"alpine"`, `"meadow"`, `"chalet"`, `"glacier"` in river gorge, escarpment, ocean coast, canyon, or woodland environments (e.g. Niagara Falls, Iguazu, Redwoods, Big Sur).
### 32. Mandatory raw_gemini_screenplay.json Persistence Across All Studios (Zero Missing Raw JSON Guarantee)
* **Mandatory Creation on Every Screenplay Execution:** Every single studio director (`*_director.py`) across all genres (travel, scenic, ocean, mountain, desert, living art, zen, alpine, cozy, dance, etc.) MUST write `raw_gemini_screenplay.json` to `raw_output_path` whenever `raw_output_path` is passed.
* **Fail-Safe Fallback & Offline Persistence:** If the Gemini API fails, times out, throws an exception, or is bypassed offline, the studio director MUST still write the structured fallback screenplay payload to `raw_output_path` (with `_source: "fallback"` diagnostic marker). Under NO circumstances may a studio director exit without persisting `raw_output_path` when specified.
* **Parent Directory Safety:** Always call `raw_p.parent.mkdir(parents=True, exist_ok=True)` prior to writing to prevent path errors.
* **Central Safety Net Guarantee:** The central pipeline dispatcher (`channel_production_service.py`) and studio runners must enforce a post-dispatch check: if `raw_gemini_screenplay.json` does not exist on disk after director dispatch, the system immediately persists `screenplay.model_dump()` to `raw_gemini_screenplay.json`, guaranteeing 100% artifact availability for telemetry, auditability, and debugging across all current and future studios.

Refer to [AGENT_INSTRUCTIONS.md](file:///c:/neel-1/projects/content-generation/AGENT_INSTRUCTIONS.md) for detailed architecture, code patterns, and the pre-commit self-audit checklist.




