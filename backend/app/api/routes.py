import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.database import get_db
from app.models.db_models import AnalysisJob, JobStatus
from app.models.schemas import (
    AnalysisStatusResponse, AnalysisResultResponse,
    PathwaySummary, SkillEntity, GapItem, LearningStep
)
from app.services.parser import extract_text_from_file, parse_resume, parse_jd
from app.services.gap_analyzer import compute_gap, compute_summary_stats
from app.services.wgt_engine import generate_pathway
from app.services.trace_generator import generate_all_traces

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# ─── Upload & Trigger Analysis ────────────────────────────────────────────────

@router.post("/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    jd: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file sizes
    resume_bytes = await resume.read()
    jd_bytes     = await jd.read()

    if len(resume_bytes) > MAX_FILE_SIZE or len(jd_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 5MB per file.")

    # Create job record
    job = AnalysisJob(
        status=JobStatus.QUEUED,
        progress=0,
        status_message="Job queued, starting analysis...",
        resume_filename=resume.filename,
        jd_filename=jd.filename,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        job_id=job.id,
        resume_bytes=resume_bytes,
        resume_filename=resume.filename,
        jd_bytes=jd_bytes,
        jd_filename=jd.filename
    )

    return {"job_id": job.id, "status": "queued", "message": "Analysis started"}


# ─── Poll Status ──────────────────────────────────────────────────────────────

@router.get("/status/{job_id}", response_model=AnalysisStatusResponse)
async def get_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return AnalysisStatusResponse(
        job_id=job.id,
        status=job.status.value,
        progress=job.progress or 0,
        message=job.status_message or ""
    )


# ─── Get Full Results ─────────────────────────────────────────────────────────

@router.get("/results/{job_id}")
async def get_results(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.FAILED:
        raise HTTPException(status_code=500, detail=job.error_message or "Analysis failed")

    if job.status != JobStatus.COMPLETE:
        raise HTTPException(status_code=202, detail=f"Job not complete yet. Status: {job.status.value}")

    # Parse stored JSON back to objects
    resume_skills = [SkillEntity(**s) for s in (job.resume_skills or [])]
    jd_skills     = [SkillEntity(**s) for s in (job.jd_skills or [])]
    gap_report    = [GapItem(**g) for g in (job.gap_report or [])]
    pathway       = [LearningStep(**s) for s in (job.pathway or [])]
    summary       = PathwaySummary(**job.summary) if job.summary else None

    return {
        "job_id": job.id,
        "status": job.status.value,
        "resume_filename": job.resume_filename,
        "jd_filename": job.jd_filename,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "gap_report": gap_report,
        "pathway": pathway,
        "summary": summary,
        "created_at": job.created_at
    }


# ─── Get Single Step Trace ────────────────────────────────────────────────────

@router.get("/trace/{job_id}/{skill_id}")
async def get_trace(job_id: str, skill_id: str, db: Session = Depends(get_db)):
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job or job.status != JobStatus.COMPLETE:
        raise HTTPException(status_code=404, detail="Job not found or not complete")

    pathway = job.pathway or []
    for step in pathway:
        if step.get("skill_id") == skill_id:
            return {
                "skill_id": skill_id,
                "skill_name": step.get("skill_name"),
                "reasoning_trace": step.get("reasoning_trace", ""),
                "gap_type": step.get("gap_type"),
                "coverage_score": step.get("coverage_score"),
                "modules": step.get("modules", [])
            }

    raise HTTPException(status_code=404, detail=f"Skill {skill_id} not in pathway")


# ─── Health + Stats ───────────────────────────────────────────────────────────

@router.get("/stats")
async def stats(db: Session = Depends(get_db)):
    from app.services.data_loader import get_all_skills, load_catalog
    total_jobs     = db.query(AnalysisJob).count()
    complete_jobs  = db.query(AnalysisJob).filter(AnalysisJob.status == JobStatus.COMPLETE).count()
    return {
        "total_analyses": total_jobs,
        "completed": complete_jobs,
        "skill_taxonomy_size": len(get_all_skills()),
        "course_catalog_size": len(load_catalog()["modules"])
    }


# ─── Background Analysis Task ─────────────────────────────────────────────────

async def run_analysis(
    job_id: str,
    resume_bytes: bytes,
    resume_filename: str,
    jd_bytes: bytes,
    jd_filename: str
):
    """Full async pipeline: parse → gap → pathway → traces → save."""
    from app.core.database import SessionLocal
    db = SessionLocal()

    def update_job(status: JobStatus, progress: int, message: str,  **kwargs):
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = status
            job.progress = progress
            job.status_message = message
            for k, v in kwargs.items():
                setattr(job, k, v)
            db.commit()

    try:
        # ── Stage 1: Extract text ────────────────────────────────────────
        update_job(JobStatus.PARSING, 10, "Extracting text from documents...")

        resume_text = extract_text_from_file(resume_bytes, resume_filename)
        jd_text     = extract_text_from_file(jd_bytes, jd_filename)

        if not resume_text.strip():
            raise ValueError("Could not extract text from resume. Try a different format.")
        if not jd_text.strip():
            raise ValueError("Could not extract text from job description.")

        update_job(JobStatus.PARSING, 25, "Parsing skills with AI...",
                   resume_text=resume_text[:5000], jd_text=jd_text[:5000])

        # ── Stage 2: Parse skills ────────────────────────────────────────
        resume_skills, exp_years, r_domain = await parse_resume(resume_text)
        jd_skills, role_title, seniority   = await parse_jd(jd_text)

        update_job(JobStatus.ANALYZING, 50, f"Computing skill gaps for {role_title}...")

        # ── Stage 3: Gap analysis ────────────────────────────────────────
        gap_items = compute_gap(resume_skills, jd_skills)
        summary   = compute_summary_stats(resume_skills, jd_skills, gap_items)

        update_job(JobStatus.GENERATING, 65, "Generating personalized learning pathway...")

        # ── Stage 4: WGT Pathway ─────────────────────────────────────────
        pathway = generate_pathway(
            gap_items=gap_items,
            resume_skills=resume_skills,
            experience_years=exp_years,
            seniority=seniority
        )

        update_job(JobStatus.GENERATING, 80, "Generating reasoning traces...")

        # ── Stage 5: Reasoning traces ────────────────────────────────────
        gap_lookup = {g.skill_id: g for g in gap_items}
        pathway = await generate_all_traces(pathway, gap_lookup)

        # Update summary totals
        summary["total_modules"] = sum(len(s.modules) for s in pathway)
        summary["total_hours"]   = round(sum(s.estimated_hours for s in pathway), 1)

        update_job(JobStatus.GENERATING, 95, "Saving results...")

        # ── Stage 6: Persist results ─────────────────────────────────────
        update_job(
            JobStatus.COMPLETE, 100,
            f"Analysis complete! {len(pathway)} learning steps generated.",
            resume_skills=[s.model_dump() for s in resume_skills],
            jd_skills=[s.model_dump() for s in jd_skills],
            gap_report=[g.model_dump() for g in gap_items],
            pathway=[s.model_dump() for s in pathway],
            summary=summary
        )

        print(f"[Job {job_id}] Complete — {len(pathway)} steps, {summary['total_hours']}h")

    except Exception as e:
        print(f"[Job {job_id}] FAILED: {e}")
        update_job(JobStatus.FAILED, 0, f"Analysis failed: {str(e)}", error_message=str(e))

    finally:
        db.close()