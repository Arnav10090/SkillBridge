# ⚡ SkillBridge — AI-Adaptive Onboarding Engine

> **ARTPARK CodeForge Hackathon Submission**  
> An AI-driven system that analyzes a candidate's resume against a job description, identifies precise skill gaps, and generates a personalized, prioritized learning roadmap.

---

## 🎯 Problem Statement

Corporate onboarding suffers from a one-size-fits-all problem:
- Experienced hires waste time on concepts they already know
- Beginners get overwhelmed by advanced modules
- No one measures the actual gap between hire capabilities and role requirements

**SkillBridge solves this** by generating a personalized learning pathway in under 30 seconds using AI.

---

## 🚀 Live Demo

Upload a resume (PDF/DOCX) + job description (PDF/TXT) → get a fully personalized roadmap with reasoning traces.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 Intelligent Parsing | Hybrid LLM + NER + alias extraction from resume & JD |
| 📊 Skill Gap Analysis | 3-layer comparison: exact match → skill family → cosine similarity |
| 🗺️ Adaptive Pathway | Original WGT (Weighted Graph Traversal) algorithm |
| 🔍 Reasoning Traces | Every recommendation explained with evidence from your resume |
| 🎨 Interactive Roadmap | react-flow DAG with color-coded nodes and filter controls |
| 🚫 Zero Hallucinations | All course recommendations from curated closed catalog only |
| ⚡ Real-time Progress | Live 6-stage processing pipeline with WebSocket-style polling |

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (React 18 + Vite)                 │
│   Upload → Processing → Dashboard → Roadmap (DAG)       │
└──────────────────────────┬──────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────┐
│               BACKEND (FastAPI + Python 3.11)           │
│  /analyze  /status  /results  /trace  /health           │
└──────┬──────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│                    AI / ML LAYER                        │
│  Parser (LLM + spaCy)  →  Gap Analyzer (FAISS)         │
│  WGT Algorithm (NetworkX)  →  Trace Generator (LLM)    │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Skill Gap Analysis Logic

### 3-Layer Matching Pipeline
```
For each JD skill requirement:

Layer 1 — Exact ID Match
  Resume has exact skill? → compute level coverage score
  coverage ≥ 0.85 → fully covered (skip)
  coverage < 0.85 → weak gap

Layer 2 — Skill Family Match  
  e.g. Resume has PostgreSQL + MySQL → covers SQL requirement (0.84 coverage)
  e.g. Resume has React → partial credit for Next.js
  Prevents false gaps from skill variant naming

Layer 3 — Semantic Similarity (cosine)
  Embed all skill names with all-MiniLM-L6-v2 (384-dim)
  FAISS IndexFlatIP similarity search
  score ≥ 0.62 → weak gap
  score < 0.62 → missing gap
```

### WGT Priority Score Formula (Original Algorithm)
```
P(skill) = 0.40 × gap_severity
         + 0.30 × requirement_weight  
         + 0.20 × dependency_urgency
         + 0.10 × experience_penalty

Where:
  gap_severity       = 1.0 - coverage_score
  requirement_weight = 1.5 (required) or 1.0 (preferred), normalized
  dependency_urgency = blocked_gap_skills / total_gap_skills
  experience_penalty = reduced for trivial skills on senior hires
```

Skills are then ordered via **Kahn's topological sort** with P-score tie-breaking, ensuring prerequisites always appear before dependent skills.

---

## 🛠️ Tech Stack

### Frontend
| Library | Version | Purpose |
|---|---|---|
| React | 18.3 | UI framework |
| Vite | 5.x | Build tool |
| @xyflow/react | 11.x | DAG roadmap visualization |
| recharts | 2.x | Skill gap charts |
| react-dropzone | 14.x | File uploads |
| zustand | 4.x | State management |

### Backend
| Library | Version | Purpose |
|---|---|---|
| FastAPI | 0.111 | REST API framework |
| SQLAlchemy | 2.0 | ORM + SQLite storage |
| pdfplumber | 0.11 | PDF text extraction |
| python-docx | 1.1 | DOCX text extraction |

### AI / ML
| Model / Library | Purpose |
|---|---|
| Mistral-7B-Instruct (Ollama) or GPT-4o-mini | Skill extraction + reasoning traces |
| all-MiniLM-L6-v2 (sentence-transformers) | 384-dim skill embeddings |
| FAISS (faiss-cpu) | Vector similarity search |
| spaCy en_core_web_lg | NER validation |
| NetworkX | Skill dependency DAG |

### Datasets & Ontologies
| Dataset | Source | Rows Processed | Usage |
|---|---|---|---|
| Kaggle Resume Dataset | [snehaanbhawal](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset/data) | **2,484 resumes** | Enriched 11 skill aliases in taxonomy |
| Kaggle JD Dataset | [kshitizregmi](https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description) | **2,277 JDs** | Computed demand weights for WGT P-Score |
| O*NET Database 28.1 | [onetcenter.org](https://www.onetcenter.org/db_releases.html) | Full database | Canonical skill IDs + prerequisite graph |

---

## ⚙️ Setup Instructions

### Option A — Docker (Recommended for Judges)
```bash
# 1. Clone the repository
git clone https://github.com/your-team/skillbridge.git
cd skillbridge

# 2. Add your OpenAI API key
# Edit skillbridge/backend/.env.docker
# Set: OPENAI_API_KEY=sk-your-key-here

# 3. Start everything
docker compose up --build

# 4. Open the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option B — Local Development

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama (for local LLM) OR OpenAI API key

#### Backend Setup
```bash
cd skillbridge/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Configure environment
cp .env.example .env
# Edit .env — set LLM_PROVIDER and API key

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd skillbridge/frontend

# Install dependencies
npm install

# Configure environment
# Edit .env — set VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev
# Opens at http://localhost:5173
```

#### LLM Setup (Local — Free)
```bash
# Install Ollama from https://ollama.ai
ollama pull mistral

# Update backend/.env:
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=mistral
```

---

## 📁 Project Structure
```
skillbridge/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # All API endpoints
│   │   ├── core/
│   │   │   ├── config.py          # Settings management
│   │   │   ├── database.py        # SQLite/PostgreSQL setup
│   │   │   └── llm.py             # Unified LLM caller
│   │   ├── data/
│   │   │   ├── skill_taxonomy.json    # 71 skills + prerequisites
│   │   │   └── course_catalog.json   # 58 curated modules
│   │   ├── models/
│   │   │   ├── db_models.py       # SQLAlchemy ORM models
│   │   │   └── schemas.py         # Pydantic schemas
│   │   ├── services/
│   │   │   ├── parser.py          # Resume + JD extraction
│   │   │   ├── embeddings.py      # Sentence transformer service
│   │   │   ├── gap_analyzer.py    # 3-layer gap analysis
│   │   │   ├── wgt_engine.py      # Adaptive pathing algorithm
│   │   │   ├── trace_generator.py # LLM reasoning traces
│   │   │   └── data_loader.py     # Taxonomy + catalog loader
│   │   └── main.py                # FastAPI app entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadScreen.jsx
│   │   │   ├── ProcessingScreen.jsx
│   │   │   ├── ResultsDashboard.jsx
│   │   │   └── RoadmapView.jsx
│   │   ├── store/
│   │   │   └── useAppStore.js     # Zustand + localStorage persist
│   │   └── api/
│   │       └── client.js          # Axios API client
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `POST /api/v1/analyze` | POST | Upload resume + JD, returns job_id |
| `GET /api/v1/status/{job_id}` | GET | Poll job progress (0-100%) |
| `GET /api/v1/results/{job_id}` | GET | Get full pathway + gap report |
| `GET /api/v1/trace/{job_id}/{skill_id}` | GET | Get reasoning trace for a skill |
| `GET /api/v1/stats` | GET | System stats |
| `GET /health` | GET | Health check |
| `GET /docs` | GET | Interactive Swagger UI |

---

## 📊 Evaluation Metrics

| Metric | Target | Approach |
|---|---|---|
| Skill Extraction F1 | > 0.82 | Hybrid LLM + alias + NER |
| Gap Detection Recall | > 85% | 3-layer matching pipeline |
| Pathway Validity | 100% | Topological sort guarantee |
| Hallucination Rate | < 1% | Closed course catalog |
| E2E Latency (p95) | < 30s | Async background tasks |

---

## 👥 Team

**AI Apex - ARTPARK CodeForge Hackathon — 2024**

---

## 📄 License

MIT License — built for ARTPARK CodeForge Hackathon