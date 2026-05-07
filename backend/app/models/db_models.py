from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON, Enum
from sqlalchemy.sql import func
import uuid, enum
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id              = Column(String, primary_key=True, default=gen_uuid)
    status          = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    progress        = Column(Integer, default=0)           # 0-100
    status_message  = Column(String, default="Queued...")

    # Input metadata
    resume_filename = Column(String)
    jd_filename     = Column(String)
    resume_text     = Column(Text)
    jd_text         = Column(Text)

    # Results (stored as JSON)
    resume_skills   = Column(JSON)   # List[SkillEntity]
    jd_skills       = Column(JSON)   # List[SkillEntity]
    gap_report      = Column(JSON)   # List[GapItem]
    pathway         = Column(JSON)   # List[LearningStep]
    summary         = Column(JSON)   # readiness score, stats

    error_message   = Column(Text)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())