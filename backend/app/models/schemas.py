from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# ── Skill Entities ──────────────────────────────────────────
class SkillEntity(BaseModel):
    skill_id:         str
    name:             str
    category:         Literal["technical", "soft", "domain", "tool"]
    level:            Literal["beginner", "intermediate", "expert"]
    evidence:         str = ""         # quote from source doc
    confidence:       float = 1.0
    weight:           float = 1.0      # 1.5 if required, 1.0 if preferred
    requirement_type: str  = "preferred"  # "required" | "preferred"

# ── Gap Analysis ─────────────────────────────────────────────
class GapItem(BaseModel):
    skill_id:         str
    skill_name:       str
    category:         str
    gap_type:         Literal["missing", "weak", "overqualified"]
    coverage_score:   float             # 0.0 = totally missing, 1.0 = fully covered
    requirement_type: str  = "preferred"
    weight:           float = 1.0
    closest_match:    str  = ""         # best resume skill that partially covers
    p_score:          float = 0.0       # WGT priority score

# ── Course Module ─────────────────────────────────────────────
class CourseModule(BaseModel):
    id:               str
    title:            str
    provider:         str
    difficulty:       float
    duration_hours:   float
    url:              str
    description:      str

# ── Learning Step (one node in the pathway) ──────────────────
class LearningStep(BaseModel):
    step_number:      int
    skill_id:         str
    skill_name:       str
    skill_category:   str
    gap_type:         str
    coverage_score:   float
    p_score:          float
    difficulty:       float
    modules:          List[CourseModule]
    estimated_hours:  float
    reasoning_trace:  str = ""
    is_implied_prereq: bool = False     # auto-added dependency

# ── Summary Stats ─────────────────────────────────────────────
class PathwaySummary(BaseModel):
    readiness_score:      float          # 0-100
    total_gap_skills:     int
    missing_skills:       int
    weak_skills:          int
    overqualified_skills: int
    total_modules:        int
    total_hours:          float
    domain_breakdown:     dict           # domain → gap count

# ── API Request/Response ──────────────────────────────────────
class AnalysisStatusResponse(BaseModel):
    job_id:       str
    status:       str
    progress:     int
    message:      str

class AnalysisResultResponse(BaseModel):
    job_id:       str
    status:       str
    resume_skills: List[SkillEntity]
    jd_skills:    List[SkillEntity]
    gap_report:   List[GapItem]
    pathway:      List[LearningStep]
    summary:      PathwaySummary
    created_at:   Optional[datetime] = None