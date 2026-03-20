from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import Base, engine
import structlog

log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting SkillBridge API", version=settings.APP_VERSION)
    Base.metadata.create_all(bind=engine)
    log.info("Database tables created/verified")

    from app.services.embeddings import get_embedding_service
    get_embedding_service()
    log.info("Embedding model loaded", model=settings.EMBEDDING_MODEL)

    yield

    log.info("Shutting down SkillBridge API")


app = FastAPI(
    title="SkillBridge API",
    version=settings.APP_VERSION,
    description="AI-Adaptive Onboarding Engine",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API routes ──────────────────────────────────────────────────────
from app.api.routes import router
app.include_router(router, prefix="/api/v1")

# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }

# ── Dev test endpoints (remove before production) ────────────────────────────
@app.get("/test-data")
async def test_data():
    from app.services.data_loader import get_all_skills, load_catalog
    skills  = get_all_skills()
    modules = load_catalog()["modules"]
    return {"total_skills": len(skills), "total_modules": len(modules)}

@app.get("/test-parser")
async def test_parser(text: str = "Python developer with 3 years experience in React, SQL, Docker and machine learning using scikit-learn"):
    from app.services.parser import alias_based_extraction, normalize_skills
    raw    = alias_based_extraction(text)
    skills = normalize_skills(raw)
    return {"found_skills": len(skills), "skills": [{"id": s.skill_id, "name": s.name} for s in skills]}

@app.get("/test-gap")
async def test_gap():
    from app.services.parser import alias_based_extraction, normalize_skills
    from app.services.gap_analyzer import compute_gap, compute_summary_stats
    resume_skills = normalize_skills(alias_based_extraction("Python, SQL, Git, scikit-learn"))
    jd_raw        = alias_based_extraction("Python, TensorFlow, Docker, Kubernetes, MLOps, AWS, Spark")
    for s in jd_raw[:4]: s["requirement_type"] = "required"; s["weight"] = 1.5
    jd_skills     = normalize_skills(jd_raw)
    gap           = compute_gap(resume_skills, jd_skills)
    summary       = compute_summary_stats(resume_skills, jd_skills, gap)
    return {"summary": summary, "gaps": [{"skill": g.skill_name, "type": g.gap_type, "coverage": round(g.coverage_score,2)} for g in gap]}

@app.get("/test-pathway")
async def test_pathway():
    from app.services.parser import alias_based_extraction, normalize_skills
    from app.services.gap_analyzer import compute_gap, compute_summary_stats
    from app.services.wgt_engine import generate_pathway
    resume_skills = normalize_skills(alias_based_extraction("Python, SQL, Git, scikit-learn"))
    jd_raw        = alias_based_extraction("Python, TensorFlow, Docker, Kubernetes, MLOps, AWS, Spark")
    for s in jd_raw[:4]: s["requirement_type"] = "required"; s["weight"] = 1.5
    jd_skills     = normalize_skills(jd_raw)
    gap_items     = compute_gap(resume_skills, jd_skills)
    pathway       = generate_pathway(gap_items, resume_skills, experience_years=2, seniority="mid")
    summary       = compute_summary_stats(resume_skills, jd_skills, gap_items)
    summary["total_modules"] = sum(len(s.modules) for s in pathway)
    summary["total_hours"]   = round(sum(s.estimated_hours for s in pathway), 1)
    return {
        "total_steps": len(pathway),
        "summary": summary,
        "pathway": [{"step": s.step_number, "skill": s.skill_name, "gap_type": s.gap_type, "p_score": s.p_score, "modules": [m.title for m in s.modules], "hours": s.estimated_hours, "is_implied": s.is_implied_prereq} for s in pathway]
    }