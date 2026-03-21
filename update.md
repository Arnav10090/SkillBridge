# SkillBridge — Complete Project Update & Context Document

> This document describes every feature, file, service, algorithm, and design decision implemented in the SkillBridge AI-Adaptive Onboarding Engine. Use this as full context for continuing development.

---

## 1. Project Overview

**SkillBridge** is a full-stack AI-powered onboarding engine built for the ARTPARK CodeForge Hackathon. It:
- Accepts a **resume** (PDF/DOCX/TXT) and a **job description** (PDF/DOCX/TXT)
- Extracts skills from both documents using a **hybrid LLM + alias + NER** pipeline
- Computes a **skill gap** using 3-layer matching (exact → family → cosine similarity)
- Generates a **personalized learning pathway** using the original **WGT (Weighted Graph Traversal)** algorithm
- Produces **reasoning traces** for every recommendation
- Displays everything in a **premium dark-themed React UI** with interactive DAG roadmap

---

## 2. Project Structure

```
artpark-hackathon/
└── skillbridge/
    ├── backend/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py                    # FastAPI entrypoint
    │   │   ├── api/
    │   │   │   ├── __init__.py
    │   │   │   └── routes.py              # All API endpoints
    │   │   ├── core/
    │   │   │   ├── __init__.py
    │   │   │   ├── config.py              # Pydantic settings
    │   │   │   ├── database.py            # SQLite/SQLAlchemy setup
    │   │   │   └── llm.py                 # Unified LLM caller (Ollama/OpenAI)
    │   │   ├── data/
    │   │   │   ├── skill_taxonomy.json    # 71 skills + prerequisites
    │   │   │   └── course_catalog.json    # 58 curated course modules
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   ├── db_models.py           # SQLAlchemy ORM models
    │   │   │   └── schemas.py             # Pydantic schemas
    │   │   └── services/
    │   │       ├── __init__.py
    │   │       ├── parser.py              # Resume + JD extraction
    │   │       ├── embeddings.py          # Sentence transformer service
    │   │       ├── gap_analyzer.py        # 3-layer gap analysis engine
    │   │       ├── wgt_engine.py          # WGT adaptive pathing algorithm
    │   │       ├── trace_generator.py     # LLM reasoning trace generation
    │   │       └── data_loader.py         # Taxonomy + catalog loader
    │   ├── .env                           # Local dev environment variables
    │   ├── .env.docker                    # Docker environment variables
    │   ├── .dockerignore
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/
    │   │   ├── main.jsx                   # React entrypoint
    │   │   ├── App.jsx                    # Root component + routing
    │   │   ├── index.css                  # Global styles + animations
    │   │   ├── components/
    │   │   │   ├── UploadScreen.jsx       # File upload UI
    │   │   │   ├── ProcessingScreen.jsx   # Live progress UI
    │   │   │   ├── ResultsDashboard.jsx   # Charts + skill comparison
    │   │   │   └── RoadmapView.jsx        # react-flow DAG roadmap
    │   │   ├── store/
    │   │   │   └── useAppStore.js         # Zustand + localStorage persist
    │   │   └── api/
    │   │       └── client.js              # Axios API client
    │   ├── index.html
    │   ├── tailwind.config.js
    │   ├── vite.config.js
    │   ├── nginx.conf
    │   ├── .env
    │   ├── .dockerignore
    │   └── Dockerfile
    ├── docker-compose.yml
    ├── README.md
    ├── UPDATE.md                          # This file
    └── .gitignore
```

---

## 3. Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime |
| FastAPI | 0.111.0 | REST API framework |
| Uvicorn | 0.30.1 | ASGI server |
| SQLAlchemy | 2.0.30 | ORM |
| SQLite | built-in | Database (via SQLAlchemy) |
| pdfplumber | 0.11.0 | PDF text extraction |
| python-docx | 1.1.2 | DOCX text extraction |
| sentence-transformers | 3.0.1 | Skill embeddings (all-MiniLM-L6-v2) |
| faiss-cpu | 1.8.0 | Vector similarity search |
| spaCy | 3.7.5 | NER validation |
| networkx | 3.3 | Skill dependency DAG |
| httpx | 0.27.0 | Async HTTP client for LLM calls |
| structlog | 24.2.0 | Structured logging |
| pydantic-settings | 2.3.4 | Settings management |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 18.3 | UI framework |
| Vite | 5.x | Build tool |
| @xyflow/react | 11.x | DAG roadmap visualization |
| recharts | 2.x | Radar + bar charts |
| react-dropzone | 14.x | File upload zones |
| zustand | 4.x | Global state + localStorage persistence |
| axios | latest | HTTP client |
| lucide-react | latest | Icons |
| framer-motion | 10.x | Animations |
| TailwindCSS | 3.x | Utility styling |

### AI/ML
| Model/Library | Purpose |
|---|---|
| Mistral-7B-Instruct (via Ollama) OR GPT-4o-mini (OpenAI) | Skill extraction + reasoning traces |
| all-MiniLM-L6-v2 (sentence-transformers) | 384-dim skill name embeddings |
| FAISS IndexFlatIP | Cosine similarity search |
| spaCy en_core_web_lg | NER validation cross-check |
| NetworkX | DAG operations for skill prerequisites |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Docker Compose | Containerized deployment |
| Redis 7 (Alpine) | Cache + task queue |
| nginx (Alpine) | Frontend static file serving + API proxy |
| SQLite | Zero-setup database for hackathon |

---

## 4. Environment Configuration

### `backend/.env` (local development)
```env
APP_NAME=SkillBridge
APP_VERSION=1.0.0
DEBUG=true
DATABASE_URL=sqlite:///./skillbridge.db
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=ollama          # or "openai"
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OPENAI_API_KEY=              # set if using OpenAI
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.62
SECRET_KEY=dev-secret-key
```

### `backend/.env.docker` (Docker deployment)
```env
DATABASE_URL=sqlite:///./skillbridge.db
REDIS_URL=redis://redis:6379/0
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.62
```

### `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SkillBridge
```

---

## 5. Database Design

### ORM: SQLAlchemy with SQLite
**File:** `backend/app/models/db_models.py`

### Table: `analysis_jobs`
| Column | Type | Description |
|---|---|---|
| id | String (UUID) | Primary key, auto-generated |
| status | Enum | queued / parsing / analyzing / generating / complete / failed |
| progress | Integer | 0-100 |
| status_message | String | Human-readable status |
| resume_filename | String | Original filename |
| jd_filename | String | Original filename |
| resume_text | Text | Extracted text (truncated to 5000 chars) |
| jd_text | Text | Extracted text |
| resume_skills | JSON | List of SkillEntity objects |
| jd_skills | JSON | List of SkillEntity objects |
| gap_report | JSON | List of GapItem objects |
| pathway | JSON | List of LearningStep objects |
| summary | JSON | PathwaySummary stats |
| error_message | Text | Error details if failed |
| created_at | DateTime | Auto timestamp |
| updated_at | DateTime | Auto on update |

### Key Design Decision
- Uses SQLite for zero-setup hackathon deployment
- `create_all()` is idempotent — safe on every restart
- All AI results stored as JSON columns for flexibility

---

## 6. Pydantic Schemas

**File:** `backend/app/models/schemas.py`

### SkillEntity
```python
class SkillEntity(BaseModel):
    skill_id: str           # O*NET-style canonical ID (e.g. "PROG_PY")
    name: str               # Display name (e.g. "Python")
    category: Literal["technical", "soft", "domain", "tool"]
    level: Literal["beginner", "intermediate", "expert"]
    evidence: str           # Quote from source document
    confidence: float       # 0.0-1.0
    weight: float           # 1.5 if required, 1.0 if preferred
    requirement_type: str   # "required" | "preferred" | "implied"
```

### GapItem
```python
class GapItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    gap_type: Literal["missing", "weak", "overqualified"]
    coverage_score: float   # 0.0 = totally missing, 1.0 = fully covered
    requirement_type: str
    weight: float
    closest_match: str      # Best resume skill that partially covers this
    p_score: float          # WGT priority score (computed later)
```

### LearningStep
```python
class LearningStep(BaseModel):
    step_number: int
    skill_id: str
    skill_name: str
    skill_category: str
    gap_type: str
    coverage_score: float
    p_score: float
    difficulty: float       # 1.0-5.0
    modules: List[CourseModule]
    estimated_hours: float
    reasoning_trace: str    # LLM-generated explanation
    is_implied_prereq: bool # Auto-added dependency
```

### CourseModule
```python
class CourseModule(BaseModel):
    id: str           # e.g. "M001"
    title: str
    provider: str     # e.g. "Coursera (Stanford)"
    difficulty: float
    duration_hours: float
    url: str
    description: str
```

### PathwaySummary
```python
class PathwaySummary(BaseModel):
    readiness_score: float       # 0-100
    total_gap_skills: int
    missing_skills: int
    weak_skills: int
    overqualified_skills: int
    total_modules: int
    total_hours: float
    domain_breakdown: dict       # domain → gap count
```

---

## 7. Data Layer

### Skill Taxonomy (`backend/app/data/skill_taxonomy.json`)
- **71 canonical skills** across 12+ domains
- Each skill has: `id`, `name`, `aliases[]`, `category`, `domain`, `difficulty`
- **Prerequisite relationships** defined as directed edges: `{from, to, weight}`
- Domains covered: software_engineering, web_development, machine_learning, data_science, data_engineering, devops, databases, cloud, security, management, soft_skills, finance, marketing, operations

### Course Catalog (`backend/app/data/course_catalog.json`)
- **58 curated course modules** from real providers (Coursera, Udemy, Kaggle, etc.)
- Each module has: `id`, `title`, `provider`, `skill_tags[]`, `difficulty`, `duration_hours`, `url`, `description`
- **Anti-hallucination anchor**: LLM never generates course names — all recommendations come strictly from this catalog

### Data Loader (`backend/app/services/data_loader.py`)
Key functions (all use `@lru_cache` for performance):
- `get_all_skills()` — returns all 71 skills
- `get_skill_by_id(id)` — lookup single skill
- `get_skill_aliases_map()` — returns `{alias_lowercase: skill_id}` for fast text matching
- `get_modules_for_skill(skill_id)` — returns catalog modules covering a skill
- `build_prerequisite_graph()` — returns `{skill_id: [dependents]}`
- `get_reverse_prerequisite_graph()` — returns `{skill_id: [prerequisites]}`

---

## 8. AI Services

### 8.1 LLM Caller (`backend/app/core/llm.py`)
- Unified interface supporting both **Ollama** (local, free) and **OpenAI**
- Selected via `LLM_PROVIDER` env var
- Async HTTP calls with 120s timeout
- Temperature defaults to 0.1 for deterministic extraction

### 8.2 Embedding Service (`backend/app/services/embeddings.py`)
- Model: `all-MiniLM-L6-v2` (384-dim, 80MB, CPU-only)
- Singleton via `@lru_cache(maxsize=1)` — loaded once at startup
- `embed(texts)` → normalized float32 numpy array
- `similarity(a, b)` → cosine similarity float

### 8.3 Parser Service (`backend/app/services/parser.py`)

**Text Extraction:**
- PDF: `pdfplumber` — handles multi-page, tables, columns
- DOCX: `python-docx` — extracts paragraph text
- TXT: raw UTF-8 decode

**LLM Extraction Prompts:**
- Resume prompt: strict JSON schema enforcement, extracts `{name, category, level, evidence, confidence}` per skill plus `total_experience_years`, `primary_domain`
- JD prompt: same schema plus `requirement_type` (required/preferred), `role_title`, `seniority_level`

**Alias-Based Fallback:**
- `alias_based_extraction(text)` — scans text for all 71 skill aliases using regex word boundaries
- Used when LLM fails AND as enrichment pass after LLM

**Evidence Patterns (soft skills):**
```python
EVIDENCE_PATTERNS = {
    "SOFT_PROB": [r"leetcode", r"solved \d+", r"algorithms?", r"dsa"],
    "SOFT_LEAD": [r"led\b", r"managed\b", r"tech lead"],
    "ALGO_DS":   [r"leetcode", r"\d+\+?\s*problems", r"dynamic programming"],
}
```

**Normalization:**
- `normalize_skills()` — maps LLM skill names → canonical taxonomy IDs
- 3-step: exact alias → partial match → custom ID fallback
- Deduplicates by `skill_id`, keeps highest confidence
- Level adjustment based on `experience_years`

### 8.4 Gap Analyzer (`backend/app/services/gap_analyzer.py`)

**3-Layer Matching Pipeline:**

**Layer 1 — Exact ID Match:**
- Checks if JD skill_id exists in resume skills
- Computes level coverage: `beginner→intermediate = 0.65`, `beginner→expert = 0.30`, match/exceed = `1.0`
- Coverage ≥ 0.85 → fully covered (skip)
- Coverage < 0.85 → weak gap

**Layer 1.5 — Skill Family Match:**
```python
SKILL_FAMILIES = {
    "PROG_SQL":    ["DB_PG", "DB_MYSQL"],     # PostgreSQL/MySQL covers SQL
    "ML_DL":       ["ML_TF", "ML_TORCH"],     # TF/PyTorch covers Deep Learning
    "CLOUD_AWS":   ["CLOUD_GCP", "CLOUD_AZURE"],
    "WEB_REST":    ["WEB_FASTAPI", "WEB_DJANGO", "WEB_FLASK", "WEB_NODE"],
    "PROG_TS":     ["PROG_JS"],               # JS covers TypeScript basics
    "WEB_NEXT":    ["WEB_REACT"],             # React covers Next.js basics
    # ... 15+ family mappings total
}
```
- Multiple family matches → bonus coverage: `base(0.78) + len(matches)*0.06`
- Coverage ≥ 0.85 → fully covered

**Layer 2 — Cosine Similarity:**
- Embeds all skill names with MiniLM
- FAISS dot product search (normalized = cosine)
- Threshold: `0.62` (tuned down from 0.72 for better recall)
- score ≥ 0.62 → weak gap
- score < 0.62 → missing gap

**Summary Stats:**
- `readiness_score = (1 - gap_weight/total_weight) × 100`
- `gap_weight` = sum of `weight × (1 - coverage_score)` for missing/weak gaps
- Required skills (weight=1.5) hurt score more than preferred (weight=1.0)

### 8.5 WGT Algorithm (`backend/app/services/wgt_engine.py`)

**Original Weighted Graph Traversal (WGT) — Core Innovation:**

**P-Score Formula:**
```
P(skill) = 0.40 × gap_severity
         + 0.30 × requirement_weight
         + 0.20 × dependency_urgency
         + 0.10 × experience_penalty

Where:
  gap_severity       = 1.0 - coverage_score
  requirement_weight = min(weight / 1.5, 1.0)
  dependency_urgency = blocked_gap_skills / total_gap_skills
  experience_penalty = 1.0 (reduced for trivial skills on senior hires)
```

**Implied Prerequisite Discovery:**
- `discover_implied_prerequisites()` traverses the reverse prerequisite graph
- If a gap skill needs skill B and hire lacks B → auto-add B
- Deep traversal (BFS) catches transitive prerequisites
- **Experience damping**: `difficulty_floor` based on experience years
  - 0-2 years: floor = 0.0 (add all prereqs)
  - 2-5 years: floor = 2.0 (skip beginner prereqs)
  - 5+ years: floor = 3.0 (skip beginner + intermediate prereqs)

**Topological Sort with P-Score Priority:**
- Kahn's algorithm (BFS-based)
- Priority queue: `(-p_score, skill_id)` for max-heap behavior
- Skills with no unlearned prerequisites come first
- Among tied in-degree=0 skills → highest P-score first
- Handles cycles gracefully (appends remaining by P-score)

**Difficulty Ramp:**
- `apply_difficulty_ramp()` ensures no two consecutive skills jump > 1.5 difficulty points
- Prevents cognitive overload for learners

**Module Selection:**
- `select_modules_for_skill()` filters catalog by `difficulty ≥ experience_floor`
- Low coverage (< 0.4) → prefer lower difficulty modules
- Higher coverage → prefer mid-difficulty (difficulty ≈ 3.0)
- Max 2 modules per skill

**Estimated Hours:**
```
estimated_hours = base_module_hours × (1.0 + 0.3 × gap_severity)
```

### 8.6 Trace Generator (`backend/app/services/trace_generator.py`)

**LLM Prompt Design:**
- Injects all factual data (scores, module names, evidence quotes) directly into prompt
- LLM has no freedom to invent course titles or scores
- Output validated: must contain skill name + minimum 40 chars

**Fallback Template (anti-hallucination):**
```
"Your resume does not demonstrate {skill_name} at the required level
(coverage: {coverage}%). The role {req_type} this skill.
'{module_title}' ({hours}h) directly addresses this gap."
```

**Validation:**
- Post-generation check: skill name must appear in trace
- Length check: > 40 characters
- On failure (2 attempts) → deterministic fallback template

---

## 9. API Routes

**File:** `backend/app/api/routes.py`
**Base prefix:** `/api/v1`

| Endpoint | Method | Description |
|---|---|---|
| `POST /analyze` | POST | Upload resume + JD files, returns `{job_id}` |
| `GET /status/{job_id}` | GET | Poll job: `{status, progress, message}` |
| `GET /results/{job_id}` | GET | Full results when complete |
| `GET /trace/{job_id}/{skill_id}` | GET | Single skill reasoning trace |
| `GET /stats` | GET | System stats (total jobs, catalog size) |

**Root endpoints:**
| Endpoint | Method | Description |
|---|---|---|
| `GET /health` | GET | Health check |
| `GET /docs` | GET | Auto-generated Swagger UI |

**Background Task Pipeline (`run_analysis`):**
```
Stage 1 (10-25%): Extract text from PDF/DOCX
Stage 2 (25-50%): Parse skills with LLM + alias fallback
Stage 3 (50-65%): Compute skill gaps (3-layer matching)
Stage 4 (65-80%): Generate WGT pathway
Stage 5 (80-95%): Generate LLM reasoning traces
Stage 6 (95-100%): Save results to SQLite
```

**File Validation:**
- Max size: 5MB per file
- Accepted MIME types: PDF, DOCX, TXT

---

## 10. Frontend Architecture

### State Management (`useAppStore.js`)
- **Zustand** with `persist` middleware
- Persisted to `localStorage` key: `skillbridge-state`
- Persisted fields: `step`, `results`, `jobId`
- Processing state resets to `upload` on page refresh (avoids stuck loading screen)

**State values:**
```
step: 'upload' | 'processing' | 'results' | 'roadmap'
jobId: string | null
progress: 0-100
statusMessage: string
results: full API response | null
error: string | null
```

### API Client (`client.js`)
- Axios instance with `baseURL = VITE_API_URL/api/v1`
- 120s timeout for long AI processing
- Functions: `analyzeDocuments()`, `pollStatus()`, `getResults()`, `getStats()`

### Upload Screen (`UploadScreen.jsx`)
- Two `react-dropzone` zones (resume + JD)
- Accepted: PDF, DOCX, TXT, max 5MB
- Polling loop: 2s interval, max 120 attempts (4 min timeout)
- Corner accent decorations on drop zones
- Gradient CTA button with hover glow effect

### Processing Screen (`ProcessingScreen.jsx`)
- 6-stage progress tracker with animated dots
- Shimmer progress bar (CSS gradient animation)
- Animated orbital rings in background
- Live `statusMessage` from API polling
- Stage marked `done` when `progress >= stage.max`

### Results Dashboard (`ResultsDashboard.jsx`)
- **Readiness Gauge**: SVG circular progress with color coding (red < 40, amber 40-70, green > 70)
- **4 Stat Cards**: Missing Skills, Weak Skills, Modules Assigned, Estimated Hours
- **Radar Chart**: Skill coverage by category (recharts RadarChart)
- **Bar Chart**: Gap count by domain, horizontal layout (recharts BarChart)
- **3-Column Comparison**: Your Skills | Role Requirements | Identified Gaps
- **Pathway Preview**: First 5 steps with P-scores and module names
- Show/hide toggles for all expandable lists
- Sticky header with breadcrumb navigation

### Roadmap View (`RoadmapView.jsx`)
- **react-flow** (`@xyflow/react`) DAG canvas
- Custom `SkillNode` component with:
  - Color-coded borders: red (missing), amber (weak), purple (implied prereq), green (overqualified)
  - Coverage bar inside node
  - Step number badge
  - PREREQ label for implied prerequisites
  - Click handler → opens trace drawer
- **Edge styling**: color matches source node gap type, animated for missing skills
- **Filter buttons**: All / Missing / Weak / Prereqs
  - Missing: `gap_type === 'missing' && !is_implied_prereq`
  - Weak: `gap_type === 'weak' && !is_implied_prereq`
  - Prereqs: `is_implied_prereq === true`
  - `key={filter}` on ReactFlow forces full remount on filter change
- **MiniMap**: node colors match gap type
- **Legend**: bottom-left, shows all 4 gap types
- **Trace Drawer** (right panel, 380px wide):
  - 3 metric cards: P-Score, Coverage %, Difficulty
  - Coverage progress bar
  - LLM reasoning trace text
  - Module cards with title, provider, hours, difficulty, external link
  - Estimated time card

### Design System
- **Colors**: Dark background `#050508`, indigo `#6366f1`, purple `#8b5cf6`, cyan `#06b6d4`
- **Fonts**: Syne (display/headings), DM Sans (body), JetBrains Mono (numbers/code)
- **Effects**: mesh background, gradient text, glassmorphism cards, glow shadows
- **Animations**: fadeUp, float, shimmer progress bar, orbital rings, pulse dots
- **CSS Variables**: `--glass`, `--glass-border`, `--glass-hover` for consistent glassmorphism

---

## 11. Docker Setup

### `docker-compose.yml`
Three services:
1. **api** — FastAPI backend (port 8000), depends on redis
2. **frontend** — React + nginx (port 3000), depends on api
3. **redis** — Redis 7 Alpine (port 6379)

### `backend/Dockerfile`
- Base: `python:3.11-slim`
- Installs `build-essential` + `curl`
- Installs Python deps from `requirements.txt`
- Downloads `en_core_web_lg` spaCy model
- Runs `uvicorn` on port 8000

### `frontend/Dockerfile`
- Stage 1: `node:20-alpine` → `npm install` → `npm run build`
- Stage 2: `nginx:alpine` → copies `/app/dist` → serves on port 80
- **Important**: Must use Node 20+ (Vite 5+ requires Node ≥ 20.19)

### `nginx.conf`
- Serves React build from `/usr/share/nginx/html`
- `try_files` for React Router support
- Proxies `/api` requests to `http://api:8000`
- gzip enabled for performance

---

## 12. Known Issues & Fixes Applied

### Fixed Issues
1. **SQL showing 69% for PostgreSQL+MySQL resume** → Fixed by adding `SKILL_FAMILIES` mapping in `gap_analyzer.py`
2. **Problem Solving marked as missing** → Fixed by adding `EVIDENCE_PATTERNS` regex detection in `parser.py`
3. **Total hours 3x overestimated** → Fixed by adding `difficulty_floor` damping in `wgt_engine.py`
4. **Filter not working in roadmap** → Fixed by adding `key={filter}` to ReactFlow component
5. **Missing filter showing implied prereqs** → Fixed by adding `&& !is_implied_prereq` to filter logic
6. **Page resetting on refresh** → Fixed with Zustand `persist` middleware
7. **JD +22 more button not working** → Fixed by adding `showAllJD` state
8. **Processing stage "done" bug** → Fixed by changing `progress > stage.max` to `progress >= stage.max`
9. **Docker build failing** → Fixed by upgrading from `node:18-alpine` to `node:20-alpine`
10. **venv tracked by git** → Fixed with `.gitignore` + `git rm -r --cached backend/venv`

### Current Configuration
- `SIMILARITY_THRESHOLD = 0.62` (tuned down from 0.72 for better recall)
- Experience floor: 2+ years → skip difficulty ≤ 2.0 implied prereqs; 5+ years → skip ≤ 3.0
- Max 2 modules per skill in pathway
- Max file size: 5MB
- Polling interval: 2 seconds
- Max poll attempts: 120 (4 minute timeout)

---

## 13. Running the Project Locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- Ollama (for local LLM) OR OpenAI API key

### Backend
```bash
cd skillbridge/backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_lg
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd skillbridge/frontend
npm install
npm run dev                    # Opens at http://localhost:5173
```

### With Docker
```bash
cd skillbridge
docker compose up --build
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

---

## 14. Test Endpoints (Dev Only)

All available at `http://localhost:8000`:

| Endpoint | Tests |
|---|---|
| `GET /test-data` | Verifies taxonomy (71 skills) + catalog (58 modules) load correctly |
| `GET /test-parser?text=...` | Tests alias extraction on custom text |
| `GET /test-gap` | Runs full gap analysis on hardcoded resume vs JD |
| `GET /test-pathway` | Runs full WGT pipeline, shows ordered learning steps |
| `GET /health` | App status + LLM provider info |
| `GET /api/v1/stats` | Total analyses, catalog size |
| `GET /docs` | Full Swagger UI |

---

## 15. Evaluation Criteria Coverage

| Criterion | Weight | Implementation |
|---|---|---|
| Technical Sophistication | 20% | Hybrid LLM+NER+alias extraction, original WGT P-score formula, 3-layer gap matching |
| Grounding & Reliability | 15% | Closed course catalog, trace validation, deterministic fallback template |
| Reasoning Trace | 10% | Per-step LLM traces with evidence anchoring, `/trace` API endpoint, drawer in UI |
| Product Impact | 10% | Experience floor skipping, overqualified detection, readiness score, estimated hours |
| User Experience | 15% | 4-screen premium dark UI, DAG roadmap, filter controls, persistent state |
| Cross-Domain Scalability | 10% | 12+ domains, 71 skills, non-technical roles (finance, HR, marketing, ops) |
| Communication & Docs | 20% | README.md, Docker setup, Swagger UI, this UPDATE.md |

---

## 16. Dataset Integration (Completed)

### Kaggle Resume Dataset (Resume.csv)
- 2,484 resumes processed across 24 job categories
- Top categories: INFORMATION-TECHNOLOGY (120), BUSINESS-DEVELOPMENT (120)
- Mined real-world skill surface forms → 11 new aliases added to skill_taxonomy.json
- Script: `backend/scripts/process_datasets.py`

### Kaggle JD Dataset (job_title_des.csv)
- 2,277 job descriptions processed
- Top demanded skills: JavaScript (979 JDs), SQL (798), HTML (713), CSS (668), Git (628)
- Demand weights computed → stored in skill_frequency_stats.json
- Weights integrated into WGT P-Score via DEMAND_WEIGHTS in wgt_engine.py

### Generated Evidence Files (committed to git)
- backend/app/data/skill_frequency_stats.json
- backend/app/data/dataset_report.json
- backend/app/data/skill_taxonomy.json (enriched)

---

## 17. What Still Needs to Be Done

1. **Demo Video** — 2-3 minute screen recording of full user journey (upload → processing → dashboard → roadmap → trace drawer)
2. **GitHub Push** — Push to public repository with clean commit history
3. **5-Slide Presentation** — Content is prepared in blueprint document, needs to be made in PowerPoint/Google Slides

---

## 18. Key Design Decisions

1. **SQLite over PostgreSQL** — Zero setup, works anywhere, sufficient for hackathon scale
2. **Closed course catalog** — Prevents all LLM hallucination in recommendations
3. **Skill families over pure cosine** — PostgreSQL → SQL mapping prevents false gaps
4. **WGT over Knowledge Tracing** — KT needs interaction history; WGT works at intake time only
5. **FastAPI BackgroundTasks** — No Celery dependency; simpler setup, sufficient for demo
6. **Zustand persist** — Page refresh doesn't lose analysis results
7. **Node 20 in Docker** — Vite 5+ requires Node ≥ 20.19; Node 18 causes build failure
8. **`key={filter}` on ReactFlow** — Forces full remount to clear stale node cache on filter change
9. **`difficulty_floor` in WGT** — Prevents 3x hour inflation from unnecessary implied prereqs
10. **`SIMILARITY_THRESHOLD=0.62`** — Tuned for better recall without too many false positives