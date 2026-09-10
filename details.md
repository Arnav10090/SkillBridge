# PROJECT INTERVIEW PREPARATION — SKILLBRIDGE

## INTERVIEW READINESS: 74/100

> ⚠️ **Key risks**: "Blake2b hashing embeddings" called "semantic" on resume, no authentication, no tests, trace generator doesn't actually call LLM.

---

# 1. Project Overview

| # | Item | Detail |
|---|------|--------|
| 1 | **Project Name** | SkillBridge |
| 2 | **One-line** | AI-adaptive onboarding engine that analyzes resumes against JDs to generate personalized learning roadmaps |
| 3 | **Problem** | Corporate onboarding is one-size-fits-all — experienced hires waste time, beginners get overwhelmed |
| 4 | **Target Users** | HR teams, L&D managers, hiring managers, new hires |
| 5 | **Core Functionality** | Upload resume + JD → AI extracts skills → 3-layer gap analysis → WGT algorithm generates prioritized learning pathway → interactive DAG roadmap |
| 6 | **Why it exists** | To personalize onboarding by measuring the exact skill gap between a candidate and a role |
| 7 | **Main Technologies** | Python, FastAPI, React 19, Vite, SQLite, SQLAlchemy, NetworkX, Docker |
| 8 | **AI/ML Components** | LLM-based skill extraction (Groq/Ollama), Blake2b hashing vectors for similarity, NO trained ML models |
| 9 | **Database** | SQLite (default), PostgreSQL-compatible via SQLAlchemy |
| 10 | **Backend** | FastAPI + Python 3.11, async background tasks, Pydantic v2 schemas |
| 11 | **Frontend** | React 19 + Vite, Zustand state management, @xyflow/react (ReactFlow) for DAG, recharts for charts, TailwindCSS |
| 12 | **Authentication** | ❌ **NONE** — No auth, no user sessions, no RBAC |
| 13 | **Deployment** | Docker Compose (3 services: api, frontend/nginx, redis), Render.com (backend), Vercel (frontend), GitHub Actions (keep-alive cron) |
| 14 | **External APIs** | Groq API (hosted LLM), Ollama (local LLM) |
| 15 | **Complexity** | Medium — non-trivial algorithm (WGT), multi-stage async pipeline, LLM integration, DAG visualization |

---

# 2. 30-Second Interview Answer

> "SkillBridge is an AI-powered onboarding engine I built with FastAPI and React. You upload a resume and a job description, and it runs a 6-stage async pipeline — first it extracts skills using a combination of LLM calls and alias-based pattern matching against a 71-skill taxonomy I built from O*NET data. Then it does 3-layer gap analysis — exact match, skill-family match, and cosine similarity. Finally, it runs my WGT algorithm, which is basically Kahn's topological sort with a custom priority score, to generate a prerequisite-aware learning roadmap. The frontend renders this as an interactive DAG using ReactFlow."

---

# 3. 90-Second Interview Answer

> "SkillBridge solves the problem that corporate onboarding is one-size-fits-all. An experienced hire shouldn't sit through beginner training, and a junior shouldn't be thrown into advanced material.
>
> I built a FastAPI backend with a 6-stage async processing pipeline. When you upload a resume and JD, it first extracts text from PDFs using pdfplumber, then identifies skills using a hybrid approach — alias-based regex matching against a 71-skill taxonomy I curated from O*NET, enriched with demand weights computed from 2,277 real job descriptions from a Kaggle dataset.
>
> The gap analysis runs three layers: exact skill ID match, skill-family matching — so if your resume has PostgreSQL it gets partial credit for a SQL requirement — and then cosine similarity using 384-dimensional hashing vectors for fuzzy name matching.
>
> The interesting algorithmic part is the WGT engine. I compute a priority score for each gap skill combining gap severity, requirement weight, dependency urgency, and an experience penalty. Then I use Kahn's topological sort with a min-heap for P-score tie-breaking to order skills so prerequisites always come first. There's also a difficulty ramp that prevents consecutive skills from jumping more than 1.5 difficulty levels.
>
> The frontend is React with Zustand for state management. The roadmap is rendered as an interactive directed acyclic graph using ReactFlow, with color-coded nodes showing gap type, coverage, and reasoning traces. Everything's Dockerized — a 3-service compose stack with nginx reverse proxy."

---

# 4. 3-Minute Deep-Dive Answer

> *Include everything from the 90-second version, plus:*
>
> "Let me walk through the technical decisions more specifically.
>
> **On the skill extraction**: I built a fast-path where alias-based pattern matching runs first. If it finds at least 3 skills, we skip the LLM call entirely — this keeps latency under control. If we get fewer than 3 skills from aliases, we make a concurrent LLM call to Groq using Llama 3.1 8B with a strict JSON schema prompt, and then merge both results, preferring LLM outputs but enriching with any alias-only matches at lower confidence.
>
> **On the embeddings**: I want to be upfront — these are NOT learned semantic embeddings like Sentence-BERT. I implemented deterministic hashing vectors using Blake2b. Each skill name is tokenized, character n-grams are generated, each feature is hashed to an index in a 384-dim vector with a sign determined by the hash's LSB. This gives consistent, reproducible similarity scores without needing an embedding model, which keeps the system lightweight and deployment-free of GPU requirements. The cosine similarity threshold is 0.62, tuned to avoid false matches.
>
> **On the WGT algorithm**: The P-score formula is `0.4 × gap_severity + 0.3 × requirement_weight + 0.2 × dependency_urgency + 0.1 × experience_penalty`. The requirement weight gets boosted by data-driven demand weights I computed from the Kaggle JD dataset — high-frequency skills like JavaScript and SQL get a priority boost. Dependency urgency measures how many other gap skills depend on this one as a prerequisite. The topological sort uses Python's `heapq` — it's essentially Kahn's algorithm but with a priority queue instead of a regular queue.
>
> **On the data**: I processed 2,484 resumes and 2,277 JDs offline with a separate Python script to enrich my taxonomy with 11 new aliases and compute demand weights. The taxonomy has 71 skills, 43 prerequisite edges, and maps to a 58-module curated course catalog.
>
> **On deployment**: Docker Compose runs three services — the FastAPI backend, an nginx-fronted React build, and a Redis instance. Redis is in the compose file but I should mention it's not actively used in the current code. In production, the backend runs on Render's free tier with a GitHub Actions cron pinging it every 10 minutes to prevent cold starts, and the frontend is on Vercel.
>
> **On limitations**: There's no authentication — it's an open API. No automated tests exist. The reasoning traces use template-based generation, not actual LLM calls at runtime, which I chose for latency. And the course catalog is static, not pulled from any API."

---

# 5. Resume Claim Validation

## SkillBridge Resume Bullet Analysis

| # | Resume Claim | Evidence in Code | Confidence | Risk Level |
|---|-------------|------------------|------------|------------|
| 1 | "Architected an AI-adaptive onboarding engine using FastAPI and React" | ✅ FastAPI in [main.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/main.py), React in [App.jsx](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/frontend/src/App.jsx) | **Fully supported** | 🟢 Low |
| 2 | "orchestrating a 6-stage asynchronous processing pipeline" | ✅ `run_analysis()` in [routes.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/api/routes.py#L161-L251) has 6 stages (QUEUED→PARSING→ANALYZING→GENERATING→COMPLETE), uses `BackgroundTasks` | **Fully supported** | 🟢 Low |
| 3 | "with real-time status polling" | ✅ `GET /status/{job_id}` endpoint exists. **BUT**: uses HTTP polling, NOT WebSockets. README says "WebSocket-style polling" which is misleading. | **Partially supported** | 🟡 Medium — interviewer may ask "is it WebSockets or polling?" |
| 4 | "Engineered a 3-layer skill matching pipeline" | ✅ Exact match → family match → cosine similarity in [gap_analyzer.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/gap_analyzer.py#L49-L180) | **Fully supported** | 🟢 Low |
| 5 | "hybrid LLM-based skill extraction" | ✅ Alias-based extraction + optional LLM call in [parser.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/parser.py#L307-L338). LLM only called when alias finds < 3 skills | **Fully supported** | 🟢 Low |
| 6 | "skill-family normalization" | ✅ `SKILL_FAMILIES` dict in [gap_analyzer.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/gap_analyzer.py#L22-L46) | **Fully supported** | 🟢 Low |
| 7 | **"custom 384-dimensional Blake2b hashing embeddings for deterministic semantic similarity search"** | ⚠️ **PARTIALLY MISLEADING**. Code in [embeddings.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/embeddings.py) uses Blake2b feature hashing, NOT learned semantic embeddings. Calling it "semantic" is technically inaccurate. | **Partially supported** | 🔴 **HIGH RISK** — An interviewer who knows embeddings will challenge "semantic" |
| 8 | "Designed an original Weighted Graph Traversal (WGT) algorithm implementing Kahn's Topological Sort" | ✅ [wgt_engine.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L158-L202) implements Kahn's with heapq | **Fully supported** | 🟢 Low |
| 9 | "difficulty ramping, and P-score prioritization" | ✅ `apply_difficulty_ramp()` at [wgt_engine.py L207](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L207-L237), `compute_p_score()` at [L28](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L28-L84) | **Fully supported** | 🟢 Low |
| 10 | "prerequisite-aware learning pathways across a 71-skill taxonomy" | ✅ 71 skills verified in taxonomy, 43 prerequisite edges | **Fully supported** | 🟢 Low |
| 11 | "demand weights derived from 2,277 job descriptions" | ✅ [skill_frequency_stats.json](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/data/skill_frequency_stats.json) has `total_jds_processed: 2277`, demand weights used in P-score | **Fully supported** | 🟢 Low |
| 12 | "taxonomy enriched using 2,484 resumes" | ✅ [dataset_report.json](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/data/dataset_report.json) confirms `rows_processed: 2484`, `new_aliases_added: 11` | **Fully supported** | 🟢 Low |
| 13 | "restricting recommendations to a curated 58-module catalog for deterministic roadmap generation" | ✅ 58 modules confirmed in [course_catalog.json](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/data/course_catalog.json). Truly deterministic — no LLM involved in course selection | **Fully supported** | 🟢 Low |

### 🔴 CRITICAL FLAG: "Blake2b hashing embeddings" as "semantic"

**Why an interviewer will challenge this:**
- True semantic embeddings (BERT, Sentence-BERT, OpenAI Ada) encode meaning from trained neural networks
- Blake2b hashing is a **deterministic feature hashing technique** — it maps character n-grams to vector positions
- Two completely different skill names that mean the same thing (e.g., "AI" and "Artificial Intelligence") will get LOW similarity scores because their character sequences differ
- This is closer to **locality-sensitive hashing** or **feature hashing** than semantic similarity

**What you should say:**
> "I should clarify — these aren't learned semantic embeddings. I use deterministic feature hashing with Blake2b to create 384-dimensional vectors from character n-grams of skill names. It captures lexical similarity — so 'PostgreSQL' and 'Postgres' score high — but not true semantic similarity. I chose this deliberately because it's deterministic, lightweight, requires no model downloads, and for skill names, which are short and often share substrings, lexical similarity works well enough. For true semantic search I'd use Sentence-BERT or Ada embeddings."

**What the resume SHOULD say:**
> "custom 384-dimensional Blake2b **feature hashing vectors** for deterministic **lexical** similarity search"

---

# 6. Architecture

## Textual Architecture Diagram

```
 User (Browser)
       │
       ▼
┌──────────────────────────────────────────────┐
│        FRONTEND (React 19 + Vite + Nginx)    │
│  UploadScreen → ProcessingScreen →           │
│  ResultsDashboard → RoadmapView (ReactFlow)  │
│  State: Zustand + localStorage               │
└──────────────────┬───────────────────────────┘
                   │ REST API (Axios, HTTP polling)
                   ▼
┌──────────────────────────────────────────────┐
│       BACKEND (FastAPI + Python 3.11)        │
│  /api/v1/analyze  (POST — file upload)       │
│  /api/v1/status   (GET  — poll progress)     │
│  /api/v1/results  (GET  — fetch results)     │
│  /api/v1/trace    (GET  — reasoning trace)   │
│  /api/v1/stats    (GET  — system stats)      │
│  /health          (GET  — healthcheck)       │
└──────┬───────────────────────────────────────┘
       │  BackgroundTasks (async)
       ▼
┌──────────────────────────────────────────────┐
│         6-STAGE PROCESSING PIPELINE          │
│                                              │
│  Stage 1: Text Extraction (pdfplumber/docx)  │
│  Stage 2: Skill Parsing                      │
│     ├── Alias-based regex (fast path)        │
│     └── LLM call (Groq/Ollama, if needed)    │
│  Stage 3: Gap Analysis (3-layer matching)    │
│     ├── Exact ID match                       │
│     ├── Skill-family match                   │
│     └── Cosine similarity (Blake2b vectors)  │
│  Stage 4: WGT Pathway Generation             │
│     ├── P-Score computation                  │
│     ├── Implied prerequisite discovery       │
│     ├── Kahn's topological sort + heapq      │
│     ├── Difficulty ramp enforcement          │
│     └── Course module selection              │
│  Stage 5: Reasoning Trace Generation         │
│     └── Template-based (NOT LLM)             │
│  Stage 6: Persist to Database                │
└──────┬──────────┬────────────────────────────┘
       │          │
       ▼          ▼
┌──────────┐ ┌──────────────────────┐
│  SQLite  │ │  External LLM API    │
│  (JSON   │ │  ├── Groq (Llama 3.1)│
│  columns)│ │  └── Ollama (Mistral) │
└──────────┘ └──────────────────────┘

Static Data (loaded at startup):
  ├── skill_taxonomy.json    (71 skills, 43 prerequisites)
  ├── course_catalog.json    (58 curated modules)
  └── skill_frequency_stats.json (demand weights from 2277 JDs)
```

## Component Details

### Frontend (React 19 + Vite)
- **What**: SPA with 4 screens — Upload, Processing, Results Dashboard, Roadmap (DAG)
- **Why**: Interactive data visualization, drag-and-drop file upload, real-time progress display
- **Communication**: REST via Axios with polling for status updates
- **Key files**: [App.jsx](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/frontend/src/App.jsx), [useAppStore.js](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/frontend/src/store/useAppStore.js), [client.js](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/frontend/src/api/client.js)
- **Failure cases**: API timeout (120s Axios timeout), network failure → error banner

### Backend (FastAPI)
- **What**: REST API with 6 endpoints + background processing
- **Why**: FastAPI for async support, auto-generated OpenAPI docs, Pydantic validation
- **Communication**: Receives multipart file uploads, returns JSON
- **Key files**: [main.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/main.py), [routes.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/api/routes.py)
- **Failure cases**: LLM timeout, file parsing error, DB connection lost → job status set to FAILED

### AI / Services Layer
- **What**: Skill extraction, gap analysis, WGT pathway generation
- **Why**: Core business logic — converts raw documents into a structured learning roadmap
- **Key files**: [parser.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/parser.py), [gap_analyzer.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/gap_analyzer.py), [wgt_engine.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py), [embeddings.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/embeddings.py)

### Database (SQLite)
- **What**: Single table `analysis_jobs` storing job state and JSON results
- **Why**: Lightweight, zero-config, sufficient for prototype/demo
- **Key files**: [database.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/core/database.py), [db_models.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/models/db_models.py)

---

# 7. Repository Structure

```
SkillBridge/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # All 6 API endpoints + background pipeline
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings (env vars, LLM config)
│   │   │   ├── database.py         # SQLAlchemy engine + session factory
│   │   │   └── llm.py              # Unified LLM caller (Groq + Ollama)
│   │   ├── data/
│   │   │   ├── skill_taxonomy.json  # 71 skills, aliases, prereqs
│   │   │   ├── course_catalog.json  # 58 curated learning modules
│   │   │   ├── skill_frequency_stats.json  # Demand weights from datasets
│   │   │   └── dataset_report.json  # Processing audit log
│   │   ├── models/
│   │   │   ├── db_models.py        # SQLAlchemy ORM (AnalysisJob)
│   │   │   └── schemas.py          # Pydantic schemas (SkillEntity, GapItem, etc.)
│   │   ├── services/
│   │   │   ├── parser.py           # Text extraction + skill parsing (LLM + alias)
│   │   │   ├── embeddings.py       # Blake2b hashing vectors (384-dim)
│   │   │   ├── gap_analyzer.py     # 3-layer gap analysis engine
│   │   │   ├── wgt_engine.py       # WGT algorithm (P-score, topological sort)
│   │   │   ├── trace_generator.py  # Template-based reasoning traces
│   │   │   └── data_loader.py      # Taxonomy + catalog loader (LRU cached)
│   │   └── main.py                 # FastAPI entrypoint + CORS + lifespan
│   ├── scripts/
│   │   └── process_datasets.py     # Offline dataset processing script
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Python 3.11-slim, pip install, start.py
│   ├── start.py                    # Uvicorn launcher with PORT env
│   ├── render.yaml                 # Render.com deployment config
│   └── .env.docker.example         # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadScreen.jsx     # File upload with react-dropzone
│   │   │   ├── ProcessingScreen.jsx # Animated 6-stage progress display
│   │   │   ├── ResultsDashboard.jsx # Gap analysis charts (recharts)
│   │   │   └── RoadmapView.jsx      # Interactive DAG (ReactFlow)
│   │   ├── store/
│   │   │   └── useAppStore.js       # Zustand + localStorage persist
│   │   ├── api/
│   │   │   └── client.js            # Axios REST client
│   │   ├── App.jsx                  # Root component (step-based routing)
│   │   └── main.jsx                 # React DOM entry
│   ├── Dockerfile                   # Multi-stage: node build → nginx:alpine
│   ├── nginx.conf                   # SPA routing + API proxy
│   ├── vercel.json                  # Vercel SPA rewrite
│   └── package.json                 # React 19, xyflow, recharts, zustand, etc.
├── docker-compose.yml               # 3 services: api, frontend, redis
├── .github/workflows/
│   └── keep-render-awake.yml        # Cron ping every 10 min
└── README.md
```

---

# 8. Important Files

### [routes.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/api/routes.py)
**PURPOSE**: All API endpoints + the 6-stage background analysis pipeline
**USED BY**: Frontend API client
**IMPORTANT FUNCTIONS**: `analyze()`, `get_status()`, `get_results()`, `get_trace()`, `run_analysis()`
**DATA FLOW**: File upload → create DB job → spawn background task → poll status → fetch results
**INTERVIEW QUESTIONS**: "Walk me through what happens when a user uploads files", "Why background tasks instead of synchronous processing?", "What happens if the background task crashes?"

### [parser.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/parser.py)
**PURPOSE**: Text extraction from PDF/DOCX + hybrid skill extraction (alias + LLM)
**USED BY**: `run_analysis()` in routes.py
**IMPORTANT FUNCTIONS**: `extract_text_from_file()`, `alias_based_extraction()`, `normalize_skills()`, `parse_resume()`, `parse_jd()`, `safe_parse_json()`
**DATA FLOW**: Raw bytes → text → alias extraction → optional LLM call → normalize → deduplicate → SkillEntity list
**INTERVIEW QUESTIONS**: "Why two extraction methods?", "What if the LLM returns invalid JSON?", "How do you handle skill deduplication?"

### [embeddings.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/embeddings.py)
**PURPOSE**: Deterministic 384-dim hashing vectors for skill name similarity
**USED BY**: `compute_gap()` in gap_analyzer.py
**IMPORTANT FUNCTIONS**: `embed()`, `similarity()`, `_embed_one()`, `_char_ngrams()`
**DATA FLOW**: Skill name string → lowercase + clean → tokenize → char n-grams (3,4) → Blake2b hash → index + sign → L2 normalize
**INTERVIEW QUESTIONS**: "Is this a semantic embedding?", "Why Blake2b?", "Why 384 dimensions?", "What are character n-grams?"

### [gap_analyzer.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/gap_analyzer.py)
**PURPOSE**: 3-layer matching to find skill gaps between resume and JD
**USED BY**: `run_analysis()` in routes.py
**IMPORTANT FUNCTIONS**: `compute_gap()`, `_level_to_coverage()`, `compute_summary_stats()`
**DATA FLOW**: resume_skills + jd_skills → for each JD skill: exact → family → cosine → classify as covered/weak/missing
**INTERVIEW QUESTIONS**: "What are the three layers?", "What's the coverage threshold?", "How do you handle skill families?"

### [wgt_engine.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py)
**PURPOSE**: WGT algorithm — compute P-scores, discover implied prereqs, topological sort, difficulty ramp, course selection
**USED BY**: `run_analysis()` in routes.py
**IMPORTANT FUNCTIONS**: `compute_p_score()`, `compute_dependency_urgency()`, `discover_implied_prerequisites()`, `topological_sort_by_p_score()`, `apply_difficulty_ramp()`, `select_modules_for_skill()`, `generate_pathway()`
**DATA FLOW**: gap_items → implied prereqs → P-scores → Kahn's toposort → difficulty ramp → module selection → LearningStep list
**INTERVIEW QUESTIONS**: "Explain the P-score formula", "Why Kahn's instead of DFS-based toposort?", "What's the difficulty ramp?"

### [llm.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/core/llm.py)
**PURPOSE**: Unified LLM caller abstracting Groq API and Ollama
**USED BY**: `parser.py` for skill extraction
**IMPORTANT FUNCTIONS**: `call_llm()`, `_call_groq()`, `_call_ollama()`
**DATA FLOW**: prompt + system → select provider → httpx async POST → parse response → return string
**INTERVIEW QUESTIONS**: "Why httpx instead of the official SDK?", "How do you handle timeouts?", "What's the response format?"

---

# 9. Code Walkthrough

## 9.1 — The Background Pipeline (`run_analysis`)

This is the **heart of the application** — [routes.py L161-251](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/api/routes.py#L161-L251):

```python
async def run_analysis(
    job_id: str,
    resume_bytes: bytes, resume_filename: str,
    jd_bytes: bytes, jd_filename: str
):
    """Full async pipeline: parse → gap → pathway → traces → save."""
    from app.core.database import SessionLocal
    db = SessionLocal()  # ← Creates NEW session (not request-scoped)

    def update_job(status, progress, message, **kwargs):
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        # Update fields and commit

    try:
        # Stage 1: Extract text
        update_job(JobStatus.PARSING, 10, "Extracting text...")
        resume_text = extract_text_from_file(resume_bytes, resume_filename)
        jd_text = extract_text_from_file(jd_bytes, jd_filename)

        # Stage 2: Parse skills (LLM + alias, runs concurrently)
        resume_result, jd_result = await asyncio.gather(
            parse_resume(resume_text),
            parse_jd(jd_text)
        )

        # Stage 3: Gap analysis
        gap_items = compute_gap(resume_skills, jd_skills)

        # Stage 4: WGT Pathway
        pathway = generate_pathway(gap_items, resume_skills, ...)

        # Stage 5: Reasoning traces
        pathway = await generate_all_traces(pathway, gap_lookup)

        # Stage 6: Save to DB
        update_job(JobStatus.COMPLETE, 100, "Done!", ...)

    except Exception as e:
        update_job(JobStatus.FAILED, 0, f"Failed: {e}", error_message=str(e))
    finally:
        db.close()
```

**Key design decisions:**
1. Uses `BackgroundTasks` from FastAPI — the endpoint returns immediately with a `job_id`
2. Creates its OWN database session (not request-scoped) because background tasks outlive the HTTP request
3. `asyncio.gather()` runs resume + JD parsing concurrently — a real performance win
4. Single try/except catches ALL errors and sets job to FAILED — crude but effective
5. Progress is updated at each stage, enabling frontend polling

**Edge cases:**
- Empty text extraction → raises `ValueError`, caught by except, job set to FAILED
- LLM timeout → `_call_llm_json` has its own `asyncio.wait_for` timeout, falls back to alias extraction
- DB commit failure mid-pipeline → job stuck in intermediate state

**Alternatives:**
- Could use Celery + Redis for proper job queue (Redis is in docker-compose but unused)
- Could use SSE or WebSockets instead of polling

---

## 9.2 — The Embedding System (`embeddings.py`)

[Full file](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/embeddings.py):

```python
def _embed_one(self, text: str) -> np.ndarray:
    vec = np.zeros(self.dimensions, dtype=np.float32)  # 384-dim zero vector
    normalized = re.sub(r"[^a-z0-9+#.]+", " ", text.lower()).strip()

    tokens = normalized.split()
    features = tokens + self._char_ngrams(normalized.replace(" ", "_"))

    for feature in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        hashed = int.from_bytes(digest, "big")
        index = hashed % self.dimensions        # → position in vector
        sign = 1.0 if hashed & 1 else -1.0      # → +1 or -1
        vec[index] += sign                        # accumulate
    return vec
```

**Line-by-line:**
1. Start with a zero vector of 384 floats
2. Lowercase, strip non-alphanumeric (keeping `+`, `#`, `.` for C++, C#, etc.)
3. Split into word tokens
4. Generate character 3-grams and 4-grams (e.g., "python" → " py", "pyt", "yth", "tho", "hon", "on ", " pyt", "pyth", ...)
5. For each feature: hash with Blake2b → use `hash % 384` for index, LSB for sign
6. Accumulate into vector (can have collisions — that's expected in feature hashing)
7. After `embed()` call, L2-normalize all vectors

**Why this approach:**
- Deterministic: same input → same vector every time
- No model download, no GPU, no external API
- Fast: O(n × k) where n = features, k = hash cost
- For short skill names, character n-gram overlap captures lexical similarity well

**Limitations:**
- Not truly semantic: "Machine Learning" and "AI" will have LOW similarity
- Hash collisions can cause false similarity
- Works well for typo/abbreviation variants, poorly for synonym detection

**Complexity:** O(n) per embedding where n = total character n-grams + tokens

---

## 9.3 — The WGT Algorithm (`wgt_engine.py`)

### P-Score Formula ([L28-84](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L28-L84)):

```python
p_score = (
    0.40 * gap_severity        +   # 1.0 - coverage_score
    0.30 * requirement_weight  +   # 1.5→1.0 normalized + dataset boost
    0.20 * dependency_urgency  +   # blocked_gaps / total_gaps
    0.10 * experience_penalty      # reduced for trivial skills on seniors
)
```

### Kahn's Topological Sort ([L158-202](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L158-L202)):

```python
def topological_sort_by_p_score(skill_ids, p_scores):
    # Build in-degree restricted to gap skill set
    in_degree = {sid: 0 for sid in skill_ids}
    adj = {sid: [] for sid in skill_ids}

    for prereq in all_prereqs:
        if prereq["from"] in skill_set and prereq["to"] in skill_set:
            in_degree[prereq["to"]] += 1
            adj[prereq["from"]].append(prereq["to"])

    # Min-heap: (-p_score, skill_id) → highest p_score first
    heap = []
    for sid in skill_ids:
        if in_degree[sid] == 0:
            heapq.heappush(heap, (-p_scores.get(sid, 0.0), sid))

    ordered = []
    while heap:
        neg_p, skill_id = heapq.heappop(heap)
        ordered.append(skill_id)
        for neighbor in adj[skill_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, (-p_scores[neighbor], neighbor))

    # Handle cycles or disconnected nodes
    remaining = [s for s in skill_ids if s not in ordered]
    remaining.sort(key=lambda s: -p_scores.get(s, 0.0))
    ordered.extend(remaining)
    return ordered
```

**Key insight:** Standard Kahn's uses a regular queue (FIFO). This uses a **min-heap** (priority queue) with negated P-scores, so among skills with zero in-degree, the highest-priority skill is processed first.

**Time Complexity:** O(V + E) for the sort + O(V log V) for heap operations = O((V + E) log V)
**Space Complexity:** O(V + E) for adjacency list and in-degree map

**Cycle handling:** If the prerequisite graph has cycles, those nodes never reach in-degree 0 → appended at the end sorted by P-score. This is a pragmatic fallback, not mathematically optimal.

---

## 9.4 — LLM Integration ([llm.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/core/llm.py))

```python
async def call_llm(prompt: str, system: str = "", temperature: float = 0.1) -> str:
    if settings.LLM_PROVIDER == "groq":
        return await _call_groq(prompt, system, temperature)
    elif settings.LLM_PROVIDER == "ollama":
        return await _call_ollama(prompt, system, temperature)
```

**Design:** Strategy pattern — provider is selected via environment variable. Both use `httpx.AsyncClient` directly (no SDK).

**Groq specifics:**
- Uses `response_format: {"type": "json_object"}` — Groq's built-in JSON mode
- `max_tokens: 2048`, `temperature: 0.1` (low for determinism)
- Timeout: configurable via `LLM_TIMEOUT_SECONDS` (default 30s)

**Ollama specifics:**
- Uses `/api/chat` endpoint with `stream: False`
- No JSON mode enforced → relies on prompt to produce JSON
- Same timeout

**Missing:** No retry logic, no fallback between providers, no rate limiting.

---

## 9.5 — Trace Generator ([trace_generator.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/trace_generator.py))

> [!IMPORTANT]
> **Despite having LLM prompt templates defined, the trace generator does NOT actually call the LLM.** The `generate_trace()` function uses a template-based string interpolation approach. The LLM-calling code (TRACE_PROMPT) exists in the file but is unreachable.

```python
async def generate_trace(step, closest_match=""):
    """LLM traces are skipped to keep analysis under 60 seconds."""
    module = step.modules[0]
    trace = (
        f"Your resume shows {coverage_pct}% coverage of {step.skill_name} — ..."
    )
    return trace
```

**Interview implication:** If asked "how are reasoning traces generated?", say: "I have template-based traces that cite actual data from the gap analysis — coverage percentage, gap type, module details. I originally planned LLM-generated traces but found the added latency was too high for the user experience target of under 60 seconds, so I switched to data-driven templates."

---

# 10. End-to-End Data Flows

## Flow 1: User Uploads Resume + JD → Gets Roadmap

```
User clicks "Analyze" button in UploadScreen
    │
    ▼
UploadScreen.handleSubmit()
    │ FormData with resume + jd files
    ▼
client.js → analyzeDocuments(resumeFile, jdFile)
    │ POST /api/v1/analyze (multipart/form-data)
    ▼
routes.py → analyze() endpoint
    ├── Read file bytes, validate size (< 5MB)
    ├── Create AnalysisJob in SQLite (status=QUEUED)
    ├── background_tasks.add_task(run_analysis, ...)
    └── Return {job_id, status: "queued"}
    │
    ▼
Frontend receives job_id → store.setJobId()
    │ Switches to ProcessingScreen
    ▼
ProcessingScreen starts animated stage display
    │ Meanwhile, UploadScreen had started polling:
    ▼
client.js → pollStatus(jobId) every 2 seconds
    │ GET /api/v1/status/{job_id}
    ▼
routes.py → get_status() → reads job from DB
    │ Returns {progress: 50, message: "Computing gaps..."}
    ▼
Frontend updates store.setProgress()

[IN BACKGROUND:]
run_analysis() → Stage 1: extract_text_from_file()
    │ pdfplumber.open() or python-docx
    ▼
Stage 2: asyncio.gather(parse_resume(), parse_jd())
    ├── alias_based_extraction() → regex scan of taxonomy aliases
    ├── If < 3 skills found: call_llm() → Groq API → safe_parse_json()
    └── normalize_skills() → map to taxonomy IDs, deduplicate
    ▼
Stage 3: compute_gap(resume_skills, jd_skills)
    ├── Embed all skill names → Blake2b → 384-dim vectors
    ├── For each JD skill: exact → family → cosine → classify
    └── Returns List[GapItem]
    ▼
Stage 4: generate_pathway(gap_items, ...)
    ├── discover_implied_prerequisites() → BFS on reverse prereq graph
    ├── compute_p_score() for each gap
    ├── topological_sort_by_p_score() → Kahn's + heapq
    ├── apply_difficulty_ramp() → reorder for cognitive smoothness
    └── select_modules_for_skill() → 1-2 courses per skill
    ▼
Stage 5: generate_all_traces() → template strings
    ▼
Stage 6: update_job(COMPLETE, 100, ..., pathway=[...])
    │ Serializes all results as JSON in DB

[BACK IN FRONTEND:]
    ▼
pollStatus returns {status: "complete", progress: 100}
    ▼
client.js → getResults(jobId)
    │ GET /api/v1/results/{job_id}
    ▼
routes.py → get_results() → deserialize JSON from DB
    │ Returns full results object
    ▼
store.setResults(data) → store.setStep("results")
    ▼
ProcessingScreen unmounts → ResultsDashboard renders
    ├── ReadinessGauge (SVG circle)
    ├── StatCards (gaps, modules, hours)
    ├── RadarChart (recharts)
    ├── Gap skills table
    └── "View Roadmap" button
    ▼
User clicks "View Roadmap"
    │ store.setStep("roadmap")
    ▼
RoadmapView renders
    ├── Convert pathway to ReactFlow nodes/edges
    ├── Grid layout: 3 columns × N rows
    ├── Color-coded by gap type (red=missing, yellow=weak, purple=implied)
    └── Click node → side panel with reasoning trace + modules
```

## Flow 2: LLM Skill Extraction (with Fallback)

```
parse_resume(text)
    │
    ├── alias_based_extraction(text) → scan 71 skills × aliases
    │   Returns: List[dict] with {name, category, level, evidence, confidence}
    │
    ├── If len(alias_skills) >= FAST_PARSE_MIN_SKILLS (3):
    │   └── SKIP LLM call → use alias results directly
    │
    ├── If len(alias_skills) < 3:
    │   └── _call_llm_json(RESUME_USER_PROMPT, RESUME_SYSTEM_PROMPT, "Resume")
    │       ├── call_llm(prompt, system, temp=0.1)
    │       │   └── Groq: POST /openai/v1/chat/completions
    │       │       {model: "llama-3.1-8b-instant", response_format: json_object}
    │       ├── asyncio.wait_for(timeout=8s)  ← LLM_PARSE_TIMEOUT_SECONDS
    │       ├── safe_parse_json(response)
    │       │   ├── Try json.loads()
    │       │   ├── Strip ```json fences
    │       │   └── Regex extract first {...} block
    │       └── On timeout/error: return None → use alias results
    │
    ├── normalize_skills(raw_skills)
    │   ├── For each skill: alias_map lookup → partial match → CUSTOM_ prefix
    │   ├── Map requirement_type → weight (1.5 required, 1.0 preferred)
    │   └── Deduplicate by skill_id (keep highest confidence)
    │
    └── Merge: LLM results + alias enrichment (lower confidence 0.70)
        Returns: (List[SkillEntity], experience_years, domain)
```

## Flow 3: Gap Analysis for a Single JD Skill

```
compute_gap(resume_skills, jd_skills)
  │
  For jd_skill "DEVOPS_K8S" (Kubernetes, required):
  │
  ├── Step 1: Exact ID match
  │   resume_by_id.get("DEVOPS_K8S") → NOT FOUND
  │
  ├── Step 1.5: Skill family match
  │   SKILL_FAMILIES["DEVOPS_K8S"] = ["DEVOPS_DOCKER"]
  │   resume has "DEVOPS_DOCKER"? → YES
  │   base_coverage = 0.78
  │   family_bonus = min(1 * 0.06, 0.12) = 0.06
  │   coverage = 0.84 (< 0.85 threshold)
  │   → GapItem(gap_type="weak", coverage=0.84, closest_match="Docker")
  │
  └── If no family match either:
      Step 2: Cosine similarity
      jd_vec = embed("Kubernetes")
      scores = dot(resume_vecs, jd_vec)
      best_score = 0.43, best_match = "Docker"
      0.43 < 0.62 threshold
      → GapItem(gap_type="missing", coverage=0.43)
```

---

# 11. API Deep Dive

## Endpoint Table

| Method | Endpoint | Purpose | Input | Output | Auth | DB | External |
|--------|----------|---------|-------|--------|------|----|----------|
| POST | `/api/v1/analyze` | Upload files, start analysis | `resume` (file), `jd` (file) | `{job_id, status, message}` | ❌ None | CREATE AnalysisJob | ❌ |
| GET | `/api/v1/status/{job_id}` | Poll job progress | Path: `job_id` | `{job_id, status, progress, message}` | ❌ None | READ AnalysisJob | ❌ |
| GET | `/api/v1/results/{job_id}` | Fetch complete results | Path: `job_id` | Full results JSON | ❌ None | READ AnalysisJob | ❌ |
| GET | `/api/v1/trace/{job_id}/{skill_id}` | Get reasoning for one skill | Path: `job_id`, `skill_id` | `{skill_id, reasoning_trace, ...}` | ❌ None | READ AnalysisJob | ❌ |
| GET | `/api/v1/stats` | System statistics | None | `{total_analyses, completed, ...}` | ❌ None | COUNT AnalysisJob | ❌ |
| GET | `/health` | Health check | None | `{status, app, version, llm_provider}` | ❌ None | ❌ | ❌ |

## Deep Dive: POST /api/v1/analyze

**Why POST?** Creates a new resource (analysis job) + uploads binary data (files)
**Why multipart?** File uploads require `multipart/form-data`, not JSON
**Expected status codes:**
- `200` — Job created, analysis started
- `413` — File too large (> 5MB)
- `422` — Missing required files (FastAPI validation)

**No authentication** — anyone can submit files
**No rate limiting** — vulnerable to abuse
**No idempotency** — each request creates a new job even for identical files
**File validation**: Only checks size, not MIME type at backend level (frontend restricts to PDF/DOCX/TXT)

## Deep Dive: GET /api/v1/status/{job_id}

**Why GET?** Idempotent read operation
**Why path parameter?** `job_id` identifies a specific resource
**Expected status codes:**
- `200` — Returns current status
- `404` — Job not found

**Polling frequency:** Frontend polls every ~2 seconds (controlled by `UploadScreen`)
**Race condition risk:** If the job completes between `status` returning "complete" and the `results` call, it's fine — results are persisted.

---

# 12. Database Deep Dive

## Technology
- **SQLite** (default via `sqlite:///./skillbridge.db`)
- **PostgreSQL-compatible** (SQLAlchemy supports both, `psycopg2-binary` is in requirements)

## Schema

**Single table: `analysis_jobs`**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | String (PK) | UUID4 |
| `status` | Enum | QUEUED/PARSING/ANALYZING/GENERATING/COMPLETE/FAILED |
| `progress` | Integer | 0-100 |
| `status_message` | String | Human-readable status |
| `resume_filename` | String | Original filename |
| `jd_filename` | String | Original filename |
| `resume_text` | Text | First 5000 chars of extracted text |
| `jd_text` | Text | First 5000 chars of extracted text |
| `resume_skills` | JSON | Serialized List[SkillEntity] |
| `jd_skills` | JSON | Serialized List[SkillEntity] |
| `gap_report` | JSON | Serialized List[GapItem] |
| `pathway` | JSON | Serialized List[LearningStep] |
| `summary` | JSON | Readiness score, stats |
| `error_message` | Text | Error details if FAILED |
| `created_at` | DateTime | Auto-set on create |
| `updated_at` | DateTime | Auto-set on update |

**Key observations:**
- **No indexes** beyond the primary key — acceptable for SQLite demo, but would need indexes on `status` and `created_at` for production queries
- **JSON columns** store denormalized results — no relational modeling of skills/gaps
- **No foreign keys** — single table, no relationships
- **No user association** — jobs are anonymous

**Why SQLite?**
> "SQLite was the right choice for this prototype because it requires zero configuration, no separate server, and works perfectly for a demo where jobs are short-lived. For production with concurrent users, I'd switch to PostgreSQL — the code already supports it via SQLAlchemy."

---

# 13. AI/ML Deep Dive

## System Type
**LLM Application (augmented with deterministic hashing-based similarity)**

This is NOT:
- ❌ Traditional ML (no trained model)
- ❌ Deep learning (no neural networks)
- ❌ RAG (no retrieval from vector store)
- ❌ Agentic system (no agent loops)
- ❌ Multi-agent (single pipeline)
- ❌ Embedding-based in the learned sense

It IS:
- ✅ LLM-augmented skill extraction with deterministic fallback
- ✅ Feature hashing for fuzzy string similarity
- ✅ Graph algorithm (topological sort) on a curated ontology

## AI Pipeline

```
Resume/JD Text
    ▼
Alias-based extraction (regex scan against taxonomy)
    ▼
[If < 3 skills found] → LLM call (Groq/Ollama)
    │ System: "precision skill extraction engine"
    │ User: structured JSON prompt
    │ Temperature: 0.1
    │ Max tokens: 2048
    │ Response format: JSON object
    │ Timeout: 8 seconds
    ▼
safe_parse_json() — strip markdown, find JSON block
    ▼
normalize_skills() — map to taxonomy IDs
    ▼
Merge LLM + alias results
    ▼
[Used ONLY in gap_analyzer.py Layer 3]
Blake2b hashing → 384-dim vector → cosine similarity
```

## LLM Integration Details

| Parameter | Value |
|-----------|-------|
| **Provider** | Groq Cloud API (primary), Ollama (local fallback) |
| **Model** | Llama 3.1 8B Instant (Groq), Mistral (Ollama) |
| **Temperature** | 0.1 (low for determinism) |
| **Max tokens** | 2048 |
| **Response format** | JSON mode (Groq), prompt-enforced (Ollama) |
| **Timeout** | 8s for parsing, 30s overall |
| **Retries** | None |
| **Fallback** | If LLM fails/times out → use alias extraction results |
| **Cost** | Groq free tier (rate-limited), Ollama free (local) |

## Embedding System (Feature Hashing)

| Property | Value |
|----------|-------|
| **Type** | Deterministic feature hashing (NOT learned embedding) |
| **Algorithm** | Blake2b hash of word tokens + character n-grams |
| **Dimensionality** | 384 |
| **N-gram sizes** | 3, 4 |
| **Similarity metric** | Cosine similarity (dot product of L2-normalized vectors) |
| **Threshold** | 0.62 |
| **Storage** | Computed on-the-fly, not persisted |
| **False matches** | Possible via hash collisions; mitigated by n-gram diversity |
| **Limitations** | No semantic understanding — only lexical/substring similarity |

## Hallucination Prevention
- Course recommendations come ONLY from a closed 58-module catalog — LLM cannot invent courses
- Skill extraction is constrained to a 71-skill taxonomy via `normalize_skills()`
- Skills not in taxonomy get `CUSTOM_` prefix and lower confidence
- LLM is used only for extraction, never for generation of recommendations

---

# 14. Algorithms & DSA

## Algorithm 1: Kahn's Topological Sort with Priority Queue

**Where:** [wgt_engine.py L158-202](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L158-L202)
**Why:** Prerequisites must come before dependent skills in the learning pathway
**Input:** List of gap skill IDs + P-scores + prerequisite graph
**Output:** Topologically ordered list of skill IDs

**Step-by-step:**
1. Build in-degree map restricted to gap skills only
2. Initialize min-heap with all zero-in-degree nodes (negated P-scores)
3. Pop highest-priority node → append to result
4. Decrement in-degree of neighbors → push newly-zero nodes
5. Append any remaining nodes (cycles) sorted by P-score

**Time:** O((V + E) log V) — V = gap skills, E = prerequisite edges between them
**Space:** O(V + E)
**Why Kahn's over DFS-based?** Kahn's naturally supports priority-based tie-breaking via a heap. DFS-based toposort would require post-processing to inject priorities.

## Algorithm 2: BFS for Implied Prerequisite Discovery

**Where:** [wgt_engine.py L111-153](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L111-L153)
**Why:** If skill X depends on skill Y, and Y isn't in your resume or JD gaps, it should be auto-added
**Input:** Gap skill IDs + resume skill IDs + experience level
**Output:** Set of implied prerequisite skill IDs

**Step-by-step:**
1. Initialize queue with all gap skills
2. For each skill, check reverse prerequisite graph (what does this depend on?)
3. If prerequisite not in resume AND not already a gap → add as implied
4. BUT: skip prereqs below the experience-based difficulty floor
5. Continue BFS until queue empty

**Complexity:** O(V + E) where V = total skills, E = prerequisite edges

## Algorithm 3: Difficulty Ramp Enforcement

**Where:** [wgt_engine.py L207-237](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/wgt_engine.py#L207-L237)
**Why:** Prevents cognitive overload (e.g., jumping from difficulty 1.0 to 4.0)
**Algorithm:** Greedy — for each position, pick the first skill within 1.5 difficulty of the previous skill. If none found, force the next available.
**Complexity:** O(n²) worst case (linear scan for each position)

## Algorithm 4: Feature Hashing (Hash Trick)

**Where:** [embeddings.py](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/app/services/embeddings.py)
**What:** Maps variable-length text to fixed-size vector using hash functions
**Classical reference:** The "hashing trick" from Weinberger et al. (2009)
**Complexity:** O(k) per text where k = number of features (tokens + n-grams)

---

# 15. Async / Concurrency

## Why Asynchronous?
The pipeline involves I/O-bound operations (LLM API calls) and can take 10-60 seconds. Synchronous processing would block the API thread and cause client timeouts.

## Request Lifecycle
1. `POST /analyze` → synchronously validates files, creates DB record
2. `background_tasks.add_task(run_analysis, ...)` → spawns async background task
3. Client polls `GET /status/{job_id}` every ~2 seconds
4. Background task updates DB progress at each stage
5. Client fetches `GET /results/{job_id}` when status is "complete"

## Concurrent LLM Calls
```python
resume_result, jd_result = await asyncio.gather(
    parse_resume(resume_text),
    parse_jd(jd_text)
)
```
Resume and JD parsing run concurrently — this halves the LLM wait time.

## Race Conditions
- **Multiple polls to `/status` during update**: Each poll creates a new DB query — safe because SQLAlchemy sessions are isolated
- **Background task creates its own session**: `SessionLocal()` in `run_analysis()` — important because the original request session is closed

## What's Missing
- No **idempotency**: Same files uploaded twice create two separate jobs
- No **duplicate detection**: No check for identical uploads
- No **job queue**: BackgroundTasks is in-process, not persistent. Server restart loses running jobs
- **Redis in docker-compose but unused**: Appears to be a planned-but-unimplemented feature for proper job queuing

---

# 16. Performance

## Actual Performance-Sensitive Areas

| Area | Current Implementation | Potential Issue |
|------|----------------------|-----------------|
| **LLM latency** | 8s timeout per parse, concurrent via `asyncio.gather` | If Groq is slow, alias-only results may be less accurate |
| **Embedding computation** | On-the-fly, no caching | Re-computed for every analysis; ~71 skill names is fast enough |
| **Taxonomy loading** | `@lru_cache(maxsize=1)` on `load_taxonomy()` and `load_catalog()` | Loaded once, cached in memory — good |
| **DB queries** | Linear scan for `get_skill_by_id()` | `O(n)` per call, called inside loops — acceptable for 71 skills |
| **Prerequisite graph** | Rebuilt on every `build_prerequisite_graph()` call | Not cached — called multiple times per analysis |
| **Frontend polling** | ~2s interval | Could be replaced with SSE for less overhead |

## If Traffic Increased 10x
- SQLite would become a bottleneck (single-writer, file-level locking)
- BackgroundTasks would overwhelm the server (all tasks share the same process)
- No rate limiting → easy to DoS
- **Solution**: PostgreSQL + Celery + Redis + API rate limiting

---

# 17. Security

## Current Security Mechanisms

| Mechanism | Status | Implementation |
|-----------|--------|---------------|
| **Authentication** | ❌ NONE | No login, no tokens, no sessions |
| **Authorization** | ❌ NONE | Anyone can access any job by ID |
| **CORS** | ✅ Configured | Allows localhost + `*.vercel.app` regex |
| **File size limit** | ✅ 5MB | Checked in `analyze()` |
| **File type validation** | ⚠️ Frontend only | `ALLOWED_TYPES` defined but not enforced on backend |
| **SQL injection** | ✅ Protected | SQLAlchemy parameterized queries |
| **XSS** | ✅ React default | React escapes by default |
| **CSRF** | ⚠️ Not applicable | No session cookies, no state-changing forms requiring CSRF |
| **Prompt injection** | ⚠️ Minimal risk | LLM output parsed as JSON, not executed; taxonomy constrains results |
| **Secrets** | ⚠️ `SECRET_KEY` has default | `dev-secret-key-change-in-production` in config |
| **IDOR** | 🔴 Present | UUIDs are guessable in theory; no ownership check |
| **Rate limiting** | ❌ NONE | No protection against abuse |

## Key Vulnerability: No Authentication
If asked "how would you secure this?":
> "I'd add JWT-based authentication — issue tokens on login, validate on every API call. For the analyze endpoint, I'd associate jobs with user IDs and check ownership on status/results endpoints. Rate limiting via a middleware or API gateway to prevent abuse."

---

# 18. Error Handling & Failure Scenarios

| Scenario | Current Behavior | Production Improvement |
|----------|-----------------|----------------------|
| **LLM timeout** | Falls back to alias-only extraction (8s timeout) | Retry with backoff, try alternate provider |
| **LLM returns invalid JSON** | `safe_parse_json()` tries regex extraction, returns empty on failure | Log malformed responses, alert on high failure rate |
| **Empty resume text** | `ValueError` raised, caught, job set to FAILED | Return specific error code, suggest different format |
| **DB unavailable** | Unhandled — app crashes at startup | Health check, circuit breaker, connection pool retry |
| **File too large** | HTTP 413 returned to client | ✅ Already handled |
| **Unsupported file type** | `ValueError` from `extract_text_from_file()` | ✅ Error caught, job FAILED |
| **Background task crash** | Job stuck in intermediate state forever | Job timeout sweep, dead letter queue |
| **Concurrent requests** | SQLite single-writer lock → potential blocking | PostgreSQL for production |
| **Frontend/backend mismatch** | No API versioning — breaking changes crash frontend | API versioning, backward compatibility |

---

# 19. Cloud/DevOps

## Docker

### Backend Dockerfile ([Dockerfile](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/backend/Dockerfile))
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start.py"]
```

### Frontend Dockerfile ([Dockerfile](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/frontend/Dockerfile))
Multi-stage build:
1. Stage 1: `node:20-slim` → `npm install && npm run build`
2. Stage 2: `nginx:alpine` → copy dist + nginx.conf

### Docker Compose ([docker-compose.yml](file:///c:/Users/Asus/Desktop/My%20Projects/SkillBridge/docker-compose.yml))
3 services: `api` (backend), `frontend` (nginx), `redis` (unused)
- Volume for SQLite DB persistence
- Health check on backend
- `depends_on` ordering

## Deployment
- **Backend**: Render.com free tier (Python, auto-deploy from Git)
- **Frontend**: Vercel (static site)
- **Keep-alive**: GitHub Actions cron pings `/health` every 10 minutes to prevent Render cold starts

---

# 20. Design Decisions

| # | Decision | Why | Alternatives | Trade-off |
|---|----------|-----|-------------|-----------|
| 1 | **FastAPI over Flask** | Async support, auto OpenAPI docs, Pydantic integration | Flask, Django | FastAPI is newer, smaller community, but async is critical for LLM calls |
| 2 | **SQLite over PostgreSQL** | Zero config for demo/prototype | PostgreSQL, MongoDB | No concurrency, no production scaling |
| 3 | **Blake2b hashing over Sentence-BERT** | No model download, deterministic, lightweight | SBERT, OpenAI Ada, TF-IDF | Loses true semantic similarity, gains simplicity and speed |
| 4 | **HTTP polling over WebSockets** | Simpler implementation, stateless | WebSockets, SSE | More HTTP overhead, but no connection management complexity |
| 5 | **BackgroundTasks over Celery** | No extra infrastructure needed | Celery + Redis, RQ | Not persistent, not scalable, but sufficient for demo |
| 6 | **Groq over OpenAI** | Free tier, fast inference (LPU hardware) | OpenAI, Anthropic, local models | Rate limits on free tier, smaller model selection |
| 7 | **Zustand over Redux** | Minimal boilerplate, built-in persist middleware | Redux, Context API, Jotai | Less ecosystem, but simpler for this scale |
| 8 | **ReactFlow for DAG** | Purpose-built for node/edge graphs, drag/zoom | D3.js, vis.js, Cytoscape | Heavier dependency, but excellent developer experience |
| 9 | **Curated course catalog over API** | Deterministic, no hallucination, no rate limits | Coursera API, Udemy API | Stale content, limited to 58 modules |
| 10 | **Template traces over LLM traces** | <60s latency, deterministic, cost-free | LLM-generated traces | Less natural language quality, but faster and cheaper |
| 11 | **JSON columns over normalized tables** | Simpler schema, results are read as a blob | Separate skills/gaps/steps tables | Can't query individual skills, no relational integrity |
| 12 | **Alias-first then LLM** | Fast path avoids costly LLM call for most inputs | LLM-first, always-LLM | If aliases catch ≥3 skills, LLM is never called — risks missing nuanced skills |
| 13 | **Pydantic v2 models** | Validation, serialization, schema generation | Dataclasses, raw dicts | Slightly verbose, but type-safe |
| 14 | **`httpx` over Groq SDK** | Lightweight, no SDK dependency, same API | Official Groq Python SDK | Must handle API changes manually |
| 15 | **Nginx reverse proxy** | SPA routing + API proxy in Docker | Traefik, Caddy, direct Vite serve | Standard, well-documented, production-ready |

---

# 21. Weaknesses & Improvements

## Architecture
| Problem | Impact | How Interviewer Finds It | Improvement |
|---------|--------|------------------------|-------------|
| No authentication | Anyone can access any job | "How do you prevent unauthorized access?" | Add JWT auth + user ownership |
| Redis in compose but unused | Suggests incomplete feature | "What's Redis for?" | Either use it (job queue) or remove it |
| Background task not persistent | Server restart loses jobs | "What if the server restarts mid-analysis?" | Celery + message broker |

## Code Quality
| Problem | Impact | Improvement |
|---------|--------|-------------|
| No tests whatsoever | Can't verify correctness | Add pytest unit tests for gap_analyzer, wgt_engine |
| Dev test endpoints in main.py | Should be removed for production | Move to separate test file or remove |
| `get_skill_by_id()` is O(n) per call | Slow if taxonomy grows | Build dict lookup once |
| `build_prerequisite_graph()` not cached | Rebuilt on every call | Cache with `@lru_cache` |

## AI Reliability
| Problem | Impact | Improvement |
|---------|--------|-------------|
| No LLM retry logic | Single failure → alias-only results | Retry 2-3 times with backoff |
| No evaluation metrics tested | Claims F1 >0.82 but no test suite | Build evaluation dataset |
| Embedding not truly semantic | Misses synonyms | Use Sentence-BERT for production |

---

# 22. Testing

> **⚠️ Testing is NOT represented in the repository. No test files exist.**

## What Should Be Tested (Priority Order)

1. **`compute_gap()`** — Unit test with known resume/JD skills, verify gap types and coverage scores
2. **`topological_sort_by_p_score()`** — Test with known graph, verify prerequisite ordering
3. **`alias_based_extraction()`** — Test with sample text, verify correct skill extraction
4. **`normalize_skills()`** — Test deduplication, partial matching, CUSTOM_ prefix
5. **`safe_parse_json()`** — Test with malformed JSON, markdown fences, extra text
6. **API `/analyze` endpoint** — Integration test with sample files
7. **Difficulty ramp** — Verify no consecutive jump > 1.5
8. **P-score computation** — Verify formula with known inputs

---

# 23. 100+ Interview Questions

## A. Project Overview (10)

1. 🟢 [D] Tell me about SkillBridge in 30 seconds.
2. 🟢 [D] What problem does SkillBridge solve?
3. 🟢 [W] Why did you build this project?
4. 🟡 [W] Who are the target users and what's the user journey?
5. 🟡 [I] What are the 6 stages of the processing pipeline?
6. 🟡 [T] Why AI for onboarding instead of a rule-based system?
7. 🟠 [T] How is this different from existing skill assessment tools?
8. 🟠 [S] How would you scale this to 10,000 daily users?
9. 🟡 [W] Why did you choose a closed course catalog instead of an API?
10. 🔴 [C] What's the single biggest technical challenge you faced?

## B. Architecture (10)

11. 🟢 [D] Draw the architecture on a whiteboard.
12. 🟡 [W] Why FastAPI instead of Flask or Django?
13. 🟡 [W] Why did you separate frontend and backend?
14. 🟠 [T] Why HTTP polling instead of WebSockets?
15. 🟠 [F] What happens if the backend crashes mid-analysis?
16. 🟡 [W] Why is Redis in your docker-compose but not used?
17. 🟠 [S] How would you add real-time collaboration features?
18. 🔴 [S] Design a system to handle 100 concurrent analyses.
19. 🟡 [I] How does the frontend know when analysis is done?
20. 🟠 [T] Monolith vs microservices for this application?

## C. Code (15)

21. 🟢 [I] Walk through `run_analysis()` line by line.
22. 🟡 [I] How does `safe_parse_json()` handle malformed LLM output?
23. 🟡 [I] How does `normalize_skills()` map extracted names to taxonomy IDs?
24. 🟠 [I] Explain the `_embed_one()` function step by step.
25. 🟡 [W] Why does `parse_resume()` use `asyncio.gather()`?
26. 🟠 [F] What happens if `alias_based_extraction()` returns zero skills?
27. 🟡 [I] How does `_level_to_coverage()` work?
28. 🟠 [O] The `get_skill_by_id()` function scans all 71 skills linearly. How would you optimize it?
29. 🟡 [I] Explain the `update_job()` closure inside `run_analysis()`.
30. 🟡 [W] Why does the background task create its own DB session?
31. 🟠 [F] What happens if `compute_gap()` receives empty lists?
32. 🟡 [I] How does `select_modules_for_skill()` choose courses?
33. 🔴 [O] How would you optimize the embedding computation for a 10,000-skill taxonomy?
34. 🟡 [I] What does the `FAST_PARSE_MIN_SKILLS` config control?
35. 🟠 [F] What happens if the Groq API key is invalid?

## D. APIs / Backend (15)

36. 🟢 [D] List all API endpoints.
37. 🟡 [W] Why POST for `/analyze` and GET for `/results`?
38. 🟡 [I] How do you validate uploaded files?
39. 🟠 [W] Why return 202 when job isn't complete instead of 404?
40. 🟡 [I] How does CORS work in your app?
41. 🟠 [F] What happens if someone polls `/status` with a non-existent job_id?
42. 🟡 [T] Why `BackgroundTasks` instead of a proper task queue?
43. 🔴 [S] How would you add pagination to the results endpoint?
44. 🟠 [W] Why `multipart/form-data` instead of base64 in JSON?
45. 🟡 [I] What's the max file size and why 5MB?
46. 🟠 [T] REST vs GraphQL for this API?
47. 🟠 [F] What happens if two users submit the same files?
48. 🟡 [I] What status codes does your API return?
49. 🔴 [S] How would you add API versioning?
50. 🟡 [W] Why no authentication?

## E. Database (10)

51. 🟢 [D] What database does SkillBridge use?
52. 🟡 [W] Why SQLite instead of PostgreSQL?
53. 🟡 [I] Describe the schema of `analysis_jobs`.
54. 🟠 [T] Why JSON columns instead of normalized tables?
55. 🟠 [O] What indexes would you add for production?
56. 🟠 [F] What happens under concurrent writes to SQLite?
57. 🟡 [W] Why SQLAlchemy instead of raw SQL?
58. 🔴 [S] How would you migrate from SQLite to PostgreSQL?
59. 🟡 [I] How are UUIDs generated for job IDs?
60. 🟠 [F] What if the JSON in a column is corrupted?

## F. AI/ML (20)

61. 🟢 [D] What AI/ML does SkillBridge use?
62. 🟡 [W] Why Groq + Llama 3.1 instead of OpenAI?
63. 🟡 [I] Walk through the skill extraction prompt.
64. 🟠 [T] **Why not use true semantic embeddings like Sentence-BERT?**
65. 🔴 [C] **Is Blake2b hashing a "semantic embedding"? Explain the difference.**
66. 🟡 [I] How do you handle LLM hallucinations?
67. 🟠 [I] Explain the 3-layer gap analysis.
68. 🟡 [I] What's the cosine similarity threshold and why 0.62?
69. 🟠 [F] What if the LLM returns skills not in your taxonomy?
70. 🟡 [W] Why temperature 0.1?
71. 🟠 [I] How do you validate structured LLM output?
72. 🟠 [T] Template traces vs LLM traces — trade-offs?
73. 🟡 [I] How do character n-grams help in skill matching?
74. 🔴 [O] How would you evaluate the skill extraction accuracy?
75. 🟠 [F] What happens if Groq API goes down?
76. 🟡 [W] Why JSON mode for LLM response?
77. 🔴 [T] How would you add RAG to this system?
78. 🟠 [I] What's the P-score formula and what does each component mean?
79. 🟡 [W] Why the 8-second timeout for LLM parsing?
80. 🔴 [S] How would you evaluate and improve the system's accuracy over time?

## G. DSA / Algorithms (10)

81. 🟢 [D] What is topological sorting?
82. 🟡 [I] Explain Kahn's algorithm as implemented in your code.
83. 🟠 [W] Why Kahn's over DFS-based topological sort?
84. 🟡 [I] What's the time complexity of your topological sort?
85. 🟠 [I] How does the priority queue (heap) modify standard Kahn's?
86. 🟠 [F] What happens if the prerequisite graph has a cycle?
87. 🟡 [I] Explain BFS for implied prerequisite discovery.
88. 🟠 [I] Explain the difficulty ramp algorithm.
89. 🟡 [I] What data structure is the prerequisite graph?
90. 🔴 [O] How would you optimize the difficulty ramp from O(n²) to O(n log n)?

## H. Security (10)

91. 🟢 [D] What security measures does SkillBridge have?
92. 🟡 [F] What happens if someone uploads a malicious PDF?
93. 🟠 [W] How would you add authentication?
94. 🟠 [F] Can someone access another user's analysis results?
95. 🟡 [I] How does CORS protect your API?
96. 🟠 [W] How do you prevent prompt injection?
97. 🟡 [F] What happens if someone brute-forces job UUIDs?
98. 🔴 [S] Design a rate-limiting system for the analyze endpoint.
99. 🟡 [W] Why is `SECRET_KEY` hardcoded in config?
100. 🟠 [F] What if the Groq API key leaks?

## I. Cloud/DevOps (10)

101. 🟢 [D] How is SkillBridge deployed?
102. 🟡 [I] Explain the Docker Compose setup.
103. 🟡 [W] Why multi-stage Docker build for frontend?
104. 🟠 [W] Why the GitHub Actions cron job?
105. 🟠 [I] How does nginx proxy API calls?
106. 🟡 [T] Docker vs direct deployment on Render?
107. 🔴 [S] How would you add CI/CD with testing?
108. 🟡 [I] What environment variables does the app need?
109. 🟠 [F] What happens if the Docker container runs out of memory?
110. 🟠 [S] How would you add logging and monitoring?

## J. Testing / Performance (10)

111. 🟡 [W] Why are there no tests in the repository?
112. 🟡 [I] What would you unit test first?
113. 🟠 [I] How would you test the LLM integration?
114. 🟡 [I] How would you test the gap analyzer?
115. 🟠 [O] What's the bottleneck in the analysis pipeline?
116. 🟠 [I] How would you load test the API?
117. 🔴 [O] How would you reduce the total analysis time from 30s to 10s?
118. 🟡 [I] How does `@lru_cache` help performance?
119. 🟠 [F] What happens if analysis takes longer than the client timeout (120s)?
120. 🔴 [S] Design a caching strategy for repeated skill analyses.

---

# 24. Detailed Answers to Key Questions

## Q65: 🔴 Is Blake2b hashing a "semantic embedding"?

**ANSWER:**
"No, and I should be precise about the terminology. What I implemented is deterministic feature hashing, not a learned semantic embedding. A semantic embedding like Sentence-BERT uses a trained neural network to map text into a vector space where semantically similar inputs are close together — so 'Machine Learning' and 'AI' would have high similarity. My approach uses Blake2b to hash character n-grams into a 384-dimensional vector. This captures lexical similarity — 'PostgreSQL' and 'Postgres' score high because they share character sequences — but it won't recognize that 'AI' and 'Artificial Intelligence' are conceptually the same unless they share substrings. I chose this deliberately because it's deterministic, requires no model, and for short skill names where abbreviations and variants are the main matching challenge, it works well enough."

**DEEPER:** The hashing trick (Weinberger et al.) maps features to a fixed-size vector via hash functions. Each feature hashes to an index and sign, accumulating into a sparse-ish vector. After L2 normalization, cosine similarity approximates the Jaccard similarity of n-gram sets.

**FOLLOW-UP:** "When would you switch to actual semantic embeddings?"
**ANSWER:** "If I needed to match skills across languages, handle diverse phrasings, or scale beyond my curated taxonomy. For example, matching 'frontend development' to 'React' requires semantic understanding."

**TRAP:** Don't claim it's semantic. Own the limitation.

---

## Q82: 🟡 Explain Kahn's algorithm as implemented in your code.

**ANSWER:**
"Kahn's algorithm processes a DAG by repeatedly removing nodes with zero in-degree. In my implementation, I start by building an in-degree map restricted to only the gap skills — I filter the full prerequisite graph to only include edges between skills that are actually in our learning pathway. Then instead of a regular FIFO queue, I use a min-heap with negated P-scores, so among skills that have no pending prerequisites, the highest-priority one gets processed first. When I process a node, I decrement the in-degree of its successors, and when any reaches zero, I push it onto the heap. If there are remaining nodes at the end — which would indicate a cycle — I append them sorted by P-score."

**DEEPER:** Standard Kahn's guarantees correct topological ordering. The heap modification preserves this guarantee because all nodes popped from the heap have zero in-degree — the heap only changes the order among equally-valid candidates.

**COMPLEXITY:** O(V + E) base + O(V log V) for heap operations = O((V + E) log V)

---

## Q64: 🟠 Why not use true semantic embeddings like Sentence-BERT?

**ANSWER:**
"Three reasons. First, deployment simplicity — Sentence-BERT requires downloading a ~100MB model, which would slow down Docker builds and increase the container image size. Second, determinism — I wanted identical inputs to always produce identical results, which is easier to guarantee with hashing. Third, for skill name matching specifically, most variation is lexical — 'React.js' vs 'ReactJS' vs 'React' — and character n-gram similarity handles that well. If I were matching full job descriptions or sentences, I'd absolutely use SBERT."

---

## Q16: 🟡 Why is Redis in your docker-compose but not used?

**ANSWER:**
"Redis was originally planned for two things: first, as a proper job queue backend with Celery, and second, for caching LLM responses. I ended up using FastAPI's BackgroundTasks which runs in-process and doesn't need an external queue. The Redis service stayed in docker-compose because I didn't want to break the configuration for when I eventually add proper job queuing. In hindsight, I should either implement it or remove it to avoid confusion."

---

# 25. Ruthless Cross-Examination (10 Chains)

## Chain 1: The Embedding Challenge

**Interviewer:** "Your resume says 'custom 384-dimensional Blake2b hashing embeddings for deterministic semantic similarity search.' Is that accurate?"

**You:** "I should clarify — calling it 'semantic' is an overstatement. It's a feature hashing technique using Blake2b. It captures lexical similarity through character n-grams, not learned semantic relationships."

**Interviewer:** "So if a JD requires 'Machine Learning' and a resume has 'ML', would your system catch that?"

**You:** "Yes, actually — because 'ML' is an alias in my taxonomy. The primary matching is alias-based, not embedding-based. The embeddings are only the third layer, used when the first two layers — exact ID match and skill-family match — don't find a match."

**Interviewer:** "Then why have embeddings at all if aliases cover most cases?"

**You:** "Aliases cover known variants, but they can't cover everything. The embedding layer catches cases where someone writes a skill name in a way I didn't anticipate — like 'Postgres Database' matching against 'PostgreSQL'. The character n-grams share enough overlap for a reasonable similarity score."

**Interviewer:** "What similarity score would 'Postgres Database' and 'PostgreSQL' actually get?"

**You:** "They share the substring 'postgres' which produces identical n-grams for that portion. The additional characters 'ql' vs 'database' would add noise. I'd estimate roughly 0.5-0.7 depending on the n-gram distribution. My threshold is 0.62, so it might be a borderline match. That's actually a limitation — I'd need to verify empirically."

**Interviewer:** "Have you done that verification?"

**You:** "I haven't built a formal evaluation suite, which is a weakness. I'd need a labeled dataset of skill-name pairs with expected similarity to properly evaluate the threshold. For production, I'd replace this with Sentence-BERT."

---

## Chain 2: Architecture Scalability

**Interviewer:** "How does your system handle 100 concurrent users?"

**You:** "Honestly, the current architecture wouldn't handle that well. SQLite has file-level locking, BackgroundTasks run in-process, and there's no rate limiting."

**Interviewer:** "So what would you change?"

**You:** "Three things: PostgreSQL for proper concurrent writes, Celery with Redis for a distributed task queue, and an API rate limiter — maybe using the Redis-backed sliding window approach."

**Interviewer:** "Why didn't you build it that way from the start?"

**You:** "Scope and time constraints. This is a prototype/demo project. The current architecture validates the algorithm and UX. Adding Celery and PostgreSQL would add significant operational complexity for a project that's demonstrating an AI pipeline, not a production platform."

**Interviewer:** "Fair. But Redis is already in your docker-compose. Why not use it?"

**You:** "It was a planned feature. I added it early intending to use it for job queuing, but FastAPI's BackgroundTasks was simpler to implement and sufficient for the demo. I should have either used it or removed it."

---

## Chain 3: Testing

**Interviewer:** "How did you test the gap analyzer?"

**You:** "I used the test endpoints in main.py — `/test-gap` and `/test-pathway` — for manual verification during development. I tested with various combinations of resume and JD skills to verify the three-layer matching worked correctly."

**Interviewer:** "Those are manual test endpoints, not automated tests. Why no pytest?"

**You:** "That's a valid criticism. I prioritized building the core algorithm and UI over writing test suites. In a professional setting, I'd have unit tests for `compute_gap()`, `topological_sort_by_p_score()`, and `normalize_skills()` at minimum."

**Interviewer:** "What would your first unit test check?"

**You:** "I'd test `compute_gap()` with a resume that has exactly one skill matching a JD requirement at the same level — verify it returns zero gaps for that skill. Then test with a level mismatch — verify it returns a 'weak' gap with the correct coverage score from `_level_to_coverage()`. Then test the family-match path and the cosine path."

---

## Chain 4: The WGT Algorithm

**Interviewer:** "You call WGT an 'original algorithm.' What's original about it?"

**You:** "The specific combination and formula. Kahn's topological sort is well-known, and priority scoring is common. What's original is combining them with the P-score formula — the four-factor weighted score with dataset-driven demand weights — the difficulty ramp enforcement, and the implied prerequisite discovery using experience-based difficulty floors. No individual piece is novel, but the assembly and tuning for this specific use case is my design."

**Interviewer:** "Could you have used an existing algorithm instead?"

**You:** "A standard topological sort would handle the prerequisite ordering but wouldn't prioritize which skills to learn first. A pure shortest-path algorithm wouldn't make sense because there's no single destination. What I needed was a topological ordering with multi-factor prioritization — and I couldn't find an off-the-shelf algorithm that combined all four factors."

**Interviewer:** "What about your difficulty ramp — it's O(n²) worst case. Is that a problem?"

**You:** "For 71 skills, no. The gap list typically has 5-20 skills, making it negligible. If I needed to scale to thousands of skills, I'd reformulate it as a constrained optimization or use a more efficient greedy approach with a sorted auxiliary structure."

---

## Chain 5: Database Design

**Interviewer:** "Why store everything in JSON columns instead of normalized tables?"

**You:** "The results are always read and written as a complete unit — you never query 'find all analyses that found a gap in Python.' The access pattern is always by job_id, so denormalized JSON gives me simpler code and fewer joins. If I needed analytics across analyses, I'd normalize."

**Interviewer:** "What about data integrity?"

**You:** "Good point — there's no referential integrity. If the JSON is somehow malformed, there's no schema enforcement at the database level. Pydantic validates on write, but a corrupted row would cause a runtime error on read."

---

# 26. Project-Based Coding Questions

## Q1: Implement `_level_to_coverage()`

```python
def _level_to_coverage(resume_level: str, required_level: str) -> float:
    """
    Given resume skill level and required level, return coverage score.
    beginner < intermediate < expert
    Same or higher = 1.0, one below = 0.65, two below = 0.30
    """
    level_map = {"beginner": 1, "intermediate": 2, "expert": 3}
    r = level_map.get(resume_level, 2)
    req = level_map.get(required_level, 2)
    if r >= req: return 1.0
    elif r == req - 1: return 0.65
    else: return 0.30
```

## Q2: Write the SQL to find all failed jobs in the last 24 hours

```sql
SELECT id, error_message, created_at
FROM analysis_jobs
WHERE status = 'failed'
  AND created_at >= datetime('now', '-1 day')
ORDER BY created_at DESC;
```

## Q3: Implement cycle detection in the prerequisite graph

```python
def has_cycle(prerequisites: list[dict]) -> bool:
    """Detect cycles using Kahn's algorithm."""
    from collections import defaultdict, deque

    adj = defaultdict(list)
    in_degree = defaultdict(int)
    nodes = set()

    for p in prerequisites:
        adj[p["from"]].append(p["to"])
        in_degree[p["to"]] += 1
        nodes.add(p["from"])
        nodes.add(p["to"])

    queue = deque([n for n in nodes if in_degree[n] == 0])
    visited = 0

    while queue:
        node = queue.popleft()
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return visited != len(nodes)  # True if cycle exists
```

## Q4: Implement a simplified P-score function

```python
def compute_p_score(
    coverage: float,
    is_required: bool,
    blocked_count: int,
    total_gaps: int,
    experience_years: int,
    skill_difficulty: float
) -> float:
    gap_severity = 1.0 - coverage
    req_weight = 1.0 if is_required else 0.67
    dep_urgency = blocked_count / max(total_gaps, 1)
    exp_penalty = 0.2 if (experience_years > 5 and skill_difficulty <= 1.5) else 1.0

    return round(
        0.40 * gap_severity +
        0.30 * req_weight +
        0.20 * dep_urgency +
        0.10 * exp_penalty,
        4
    )
```

---

# 27. Whiteboard Diagrams

## 1. Overall Architecture
```
[Browser] → [React SPA] → [REST API (FastAPI)]
                              ↓
                         [6-Stage Pipeline]
                              ↓
                    [SQLite] ← [Groq LLM API]
```

## 2. Gap Analysis Pipeline
```
Resume Skills ──┐
                ├── Layer 1: Exact ID Match ──→ covered/weak
JD Skills ──────┤
                ├── Layer 2: Skill Family    ──→ weak
                │
                └── Layer 3: Cosine (Blake2b) ─→ weak/missing
```

## 3. WGT Algorithm
```
Gap Skills → P-Score → Kahn's Toposort → Difficulty Ramp → Modules → Roadmap
                ↑              ↑
           demand weights   prereq graph (43 edges)
```

## 4. Database (Single Table)
```
┌──────────────────────────────────────┐
│           analysis_jobs              │
├──────────────────────────────────────┤
│ id (PK, UUID)                        │
│ status (enum)                        │
│ progress (int 0-100)                 │
│ resume_skills (JSON)                 │
│ jd_skills (JSON)                     │
│ gap_report (JSON)                    │
│ pathway (JSON)                       │
│ summary (JSON)                       │
│ created_at, updated_at               │
└──────────────────────────────────────┘
```

---

# 28. 60-Second Emergency Revision

```
PROJECT:     SkillBridge — AI-Adaptive Onboarding Engine
PROBLEM:     One-size-fits-all onboarding wastes time
USERS:       HR teams, L&D managers, new hires
STACK:       FastAPI, React 19, SQLite, Docker, Groq LLM
ARCHITECTURE: 6-stage async pipeline with HTTP polling
DATABASE:    SQLite, single table, JSON columns
KEY APIs:    POST /analyze, GET /status, GET /results
AI:          Hybrid LLM + alias extraction, NOT semantic embeddings
             Blake2b feature hashing (deterministic, lexical similarity)
KEY ALGORITHM: Kahn's topological sort + P-score priority (WGT)
AUTH:        NONE — open API
SECURITY:    CORS configured, file size limit, SQL injection safe
DEPLOYMENT:  Docker Compose (3 services), Render + Vercel
BIGGEST CHALLENGE:    Balancing LLM accuracy vs latency (8s timeout)
BIGGEST DECISION:     Blake2b hashing over Sentence-BERT
BIGGEST PERFORMANCE:  asyncio.gather for concurrent resume+JD parsing
BIGGEST FAILURE CASE: LLM timeout → falls back to alias-only extraction
BIGGEST LIMITATION:   No auth, no tests, embeddings are lexical not semantic
WHAT I WOULD IMPROVE: Add SBERT embeddings, JWT auth, Celery queue, tests
```

---

# 29. 10-Minute Pre-Interview Revision

## Minute 0–1: Project Story
"SkillBridge analyzes resumes vs JDs to generate personalized learning roadmaps. FastAPI + React. 6-stage async pipeline. 71-skill taxonomy enriched from 2,484 resumes and 2,277 JDs."

## Minute 1–2: Architecture
"React → REST → FastAPI → BackgroundTasks → 6 stages → SQLite. Groq LLM for skill extraction. ReactFlow for DAG visualization. Docker Compose with nginx."

## Minute 2–3: Backend/API
"POST /analyze uploads files, returns job_id. Polling via GET /status. Background pipeline: extract text → parse skills → gap analysis → WGT pathway → traces → save. Pydantic schemas. httpx for LLM calls."

## Minute 3–4: Database
"SQLite, single table `analysis_jobs`, JSON columns for results. SQLAlchemy ORM. No auth, no indexes beyond PK. UUIDs for job IDs."

## Minute 4–6: AI/Algorithm
"**Embedding WARNING**: Blake2b feature hashing, NOT semantic. Character n-grams, 384-dim, cosine similarity, threshold 0.62. LLM only called when <3 alias matches. 3-layer gap: exact → family → cosine. WGT: P-score = 0.4×gap + 0.3×weight + 0.2×dependency + 0.1×experience. Kahn's toposort with heapq. Difficulty ramp ≤1.5. Implied prereq BFS."

## Minute 6–7: Security
"No auth. CORS configured. File size validation. SQLAlchemy prevents injection. IDOR risk — no ownership check. No rate limiting. SECRET_KEY has default."

## Minute 7–8: Performance
"LLM is the bottleneck — 8s timeout. asyncio.gather for concurrent parsing. lru_cache for taxonomy. Could add: Celery, PostgreSQL, Redis caching."

## Minute 8–9: Deployment
"Docker Compose: api + frontend + redis. Frontend: multi-stage build → nginx. Backend: Render free tier. Frontend: Vercel. GitHub Actions cron pings /health every 10min."

## Minute 9–10: Hardest Questions
"Blake2b is NOT semantic — own it. Redis is unused — explain planned vs implemented. No tests — acknowledge, explain what you'd test first. WGT is 'original' in assembly, not in individual components."

---

# 30. Final Defense Score

| Area | Score | Notes |
|------|-------|-------|
| Project understanding | 90/100 | Can explain end-to-end clearly |
| Code understanding | 85/100 | Should practice walking through edge cases |
| Architecture | 75/100 | Simple but defensible; unused Redis is a gap |
| Backend | 80/100 | Solid async pipeline; missing auth/rate-limiting |
| Database | 65/100 | Minimal — single table, no indexes, no auth |
| AI/ML | 70/100 | Hybrid approach is smart; must be honest about embeddings |
| DSA | 85/100 | Kahn's + heapq well-implemented; can explain complexity |
| Security | 40/100 | Almost nothing; must frame as "prototype limitation" |
| Cloud/DevOps | 70/100 | Docker + Render is solid; no CI/CD for testing |
| Performance | 65/100 | Reasonable for demo; no benchmarks |
| Testing | 20/100 | Zero tests; major weakness |
| Resume defensibility | 70/100 | "Semantic" embedding claim is the main risk |
| Communication readiness | 80/100 | Practice the 30s/90s answers out loud |

## TOP 10 WEAKNESSES TO FIX

1. **Change "semantic" to "lexical" on resume for embeddings**
2. Prepare honest answer for "why no tests?"
3. Prepare answer for "why is Redis unused?"
4. Know exactly what `_embed_one()` does line by line
5. Prepare answer for "how would you add authentication?"
6. Practice the P-score formula from memory
7. Understand why trace generator doesn't call LLM
8. Have a clear scaling story (PostgreSQL + Celery + Redis)
9. Know the difference between BackgroundTasks and Celery
10. Practice drawing the architecture on a whiteboard

## TOP 10 THINGS YOU'RE MOST LIKELY TO BE ASKED

1. "Tell me about this project" (30s and 90s versions)
2. "Walk me through what happens when a user uploads a resume"
3. "Is this a semantic embedding?" / "What kind of embedding is this?"
4. "Explain the WGT algorithm"
5. "Why FastAPI?"
6. "How do you handle LLM failures?"
7. "Why no authentication?"
8. "What would you change if you rebuilt this?"
9. "How would you scale this?"
10. "What's your testing strategy?"

## TOP 10 THINGS TO MEMORIZE

1. P-score formula: `0.4 × gap + 0.3 × weight + 0.2 × dependency + 0.1 × experience`
2. 71 skills, 43 prerequisites, 58 modules, 2277 JDs, 2484 resumes
3. 3 layers: exact match → skill family → cosine similarity (threshold 0.62)
4. 384 dimensions, Blake2b, character n-grams (3,4)
5. 6 stages: extract → parse → gap → pathway → traces → save
6. API endpoints: POST /analyze, GET /status, GET /results, GET /trace, GET /stats, GET /health
7. Kahn's = zero-in-degree nodes first, heapq for P-score priority
8. Fast path: if ≥3 alias matches, skip LLM
9. Coverage thresholds: same/higher=1.0, one below=0.65, two below=0.30
10. Docker: 3 services (api, frontend, redis), frontend is multi-stage nginx

## TOP 10 THINGS YOU MUST ACTUALLY UNDERSTAND

1. How Blake2b hashing works and WHY it's not semantic
2. How Kahn's topological sort works step by step
3. Why the background task creates its own DB session
4. How asyncio.gather provides concurrency
5. The full lifecycle from upload to DAG render
6. What happens when LLM times out (fallback path)
7. Why JSON columns vs normalized tables (access pattern)
8. How the skill family matching works with concrete examples
9. How implied prerequisite discovery uses BFS
10. The difference between BackgroundTasks (in-process) and Celery (distributed)

---

## IF YOU ONLY HAVE 30 MINUTES, STUDY THESE 10 THINGS:

1. **30-second and 90-second project answers** — practice out loud
2. **Blake2b is NOT semantic** — memorize the honest explanation
3. **End-to-end flow** from upload to DAG — trace through actual files
4. **P-score formula** — write it from memory
5. **Kahn's algorithm** — explain with heap modification
6. **3-layer gap analysis** — walk through with an example
7. **"Why no auth/tests?"** — have a prepared, honest answer
8. **Scaling story** — PostgreSQL + Celery + rate limiting
9. **Architecture diagram** — draw it from memory
10. **What you'd improve** — lead with adding SBERT, auth, tests
