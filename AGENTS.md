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

### 3. Reusable Deterministic Scripts First
* Recurring tasks must be implemented as standalone, reusable Python scripts located in `scripts/` or modular service utilities.
* Cache assets and LLM outputs using SHA-256 prompt hashing to prevent redundant API expenditure.

### 4. Hard 300-Line Limit Per File
* **No code file may exceed 300 lines** (target 120–220 lines).
* When a file approaches 250 lines, refactor immediately by decomposing into single-responsibility sub-modules within dedicated packages.

### 5. Modular, Functional & Reusable Code
* Prefer pure functions without hidden side effects.
* Use explicit dependency injection for all external clients (storage, LLMs, APIs).
* Enforce typed Pydantic contracts for all domain data passed between boundaries.
* Ensure all pipeline steps are idempotent and fail-fast.

### 6. Zero Duplication & Single Source of Truth
* Never create or keep duplicate code, redundant utility functions, or overlapping `.md` documentation files.
* Maintain exactly one authoritative source file per domain. Delete or consolidate superseded drafts immediately.

### 7. Mandatory Pre-Flight Cost Transparency
* When a user submits a video for production from the UI, the system must first calculate and display the total estimated cost and an itemized breakdown (tokens, voice characters, images/clips, compute).
* Generation jobs must remain blocked until the user explicitly clicks the confirmation button.

### 8. Model Testing Safety & Cost Guard (Single Test Only, Max 10s Duration)
* **Automated Tests Core Mandate:** When testing models as part of automated tests, **only run one test only with 10 sec duration**, to ensure we do not call more than one test, to save on costs.
* **Zero Paid Calls in Default Test Suite:** The standard test suite (`pytest`) must ALWAYS run 100% locally with offline deterministic mocks/fallbacks. Even if paid API keys are present in `.env` or system environment, the full test suite must NEVER call external AI models.
* **Strict Single Test Limit for Live Models:** When testing actual/live external AI models (Gemini, Together Flux, Azure Speech, Suno, Fal) as part of automated tests, you must **run only ONE test only**. Never call or run more than one test against live models.
* **Hard 10-Second Duration Cap:** Any automated test that calls an actual model or synthesizes video/audio must be strictly capped to a **maximum duration of 10 seconds** (and minimal token/character count) to prevent enormous API expenditures.


### 9. Mandatory Terraform-Only IaC
* **Always create Terraform scripts only for all cloud platforms** (Azure, GCP, AWS, Multi-Cloud).
* Never use Bicep, ARM templates, CloudFormation, or platform-specific template languages. Standardize on HashiCorp Terraform (`.tf`) files for 100% of infrastructure declarations.

### 10. Topic, Metadata & Final Story Deduplication & User Alerting
* **Mandatory Persistence:** Every time a video is created, save the topic, metadata information (genre, tags, audience, format), and the final story synthesized from the script into the persistent Topic Memory vault.
* **Pre-Creation Duplicate Guard:** When a user creates or estimates a video with similar metadata or topic (cosine similarity $\ge 0.80$ or heavy metadata overlap), the system MUST NOT create the duplicate content.
* **Mandatory User Alert:** Immediately block the request (HTTP 409 Conflict) and display a prominent alert to the user detailing the existing conflicting topic, episode ID, and similarity percentage to prevent channel demonetization and wasted budget.


Refer to [AGENT_INSTRUCTIONS.md](file:///c:/neel-1/projects/content-generation/AGENT_INSTRUCTIONS.md) for detailed architecture, code patterns, and the pre-commit self-audit checklist.


