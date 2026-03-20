import numpy as np
from typing import List
from app.models.schemas import SkillEntity, GapItem
from app.services.embeddings import get_embedding_service
from app.core.config import settings


# ── Skill family mappings ─────────────────────────────────────────────────────
# Variants that should count as coverage for a JD skill
SKILL_FAMILIES = {
    "PROG_SQL":    ["DB_PG", "DB_MYSQL"],
    "DB_PG":       ["PROG_SQL"],
    "DB_MYSQL":    ["PROG_SQL"],
    "ML_DL":       ["ML_TF", "ML_TORCH"],
    "ML_TF":       ["ML_DL", "ML_TORCH"],
    "ML_TORCH":    ["ML_DL", "ML_TF"],
    "CLOUD_AWS":   ["CLOUD_GCP", "CLOUD_AZURE"],
    "CLOUD_GCP":   ["CLOUD_AWS", "CLOUD_AZURE"],
    "CLOUD_AZURE": ["CLOUD_AWS", "CLOUD_GCP"],
    "WEB_REST":    ["WEB_FASTAPI", "WEB_DJANGO", "WEB_FLASK", "WEB_NODE"],
    "WEB_FASTAPI": ["WEB_REST"],
    "WEB_DJANGO":  ["WEB_REST"],
    "WEB_FLASK":   ["WEB_REST"],
    "ML_NLPBERT":  ["ML_NLP"],
    "ML_NLP":      ["ML_NLPBERT"],
    "DB_MONGO":    ["DB_REDIS"],
    "DEVOPS_K8S":  ["DEVOPS_DOCKER"],
    "WEB_NEXT":    ["WEB_REACT"],
    "WEB_REACT":   ["WEB_NEXT"],
    "ARCH_MICRO":  ["DEVOPS_DOCKER", "DEVOPS_K8S"],
    "DATA_ENG":    ["PROG_SQL", "DB_PG"],
    "PROG_TS":     ["PROG_JS"],
    "PROG_JS":     ["PROG_TS"],
}


def compute_gap(
    resume_skills: List[SkillEntity],
    jd_skills: List[SkillEntity]
) -> List[GapItem]:
    """
    Core gap analysis engine.
    Compares resume skills vs JD requirements using:
    1. Exact skill_id match
    2. Skill family match (e.g. PostgreSQL covers SQL)
    3. Cosine similarity on skill name embeddings
    Returns a GapItem for every JD skill that isn't fully covered.
    """
    emb_service = get_embedding_service()
    threshold = settings.SIMILARITY_THRESHOLD

    # Build resume lookup: skill_id → SkillEntity
    resume_by_id = {s.skill_id: s for s in resume_skills}

    # Embed all skill names for semantic matching
    resume_names = [s.name for s in resume_skills]
    jd_names     = [s.name for s in jd_skills]

    resume_vecs = emb_service.embed(resume_names) if resume_names else np.array([])
    jd_vecs     = emb_service.embed(jd_names)     if jd_names     else np.array([])

    gap_items: List[GapItem] = []

    for i, jd_skill in enumerate(jd_skills):

        # ── Step 1: Exact ID match ───────────────────────────────────────────
        if jd_skill.skill_id in resume_by_id:
            resume_match = resume_by_id[jd_skill.skill_id]
            coverage = _level_to_coverage(resume_match.level, jd_skill.level)

            if coverage >= 0.85:
                # Fully covered — mark overqualified if well above requirement
                if coverage > 0.95 and jd_skill.requirement_type == "preferred":
                    gap_items.append(GapItem(
                        skill_id=jd_skill.skill_id,
                        skill_name=jd_skill.name,
                        category=jd_skill.category,
                        gap_type="overqualified",
                        coverage_score=coverage,
                        requirement_type=jd_skill.requirement_type,
                        weight=jd_skill.weight,
                        closest_match=resume_match.name,
                        p_score=0.0
                    ))
                continue  # Fully covered — skip gap

            # Partial coverage (same skill, wrong level)
            gap_items.append(GapItem(
                skill_id=jd_skill.skill_id,
                skill_name=jd_skill.name,
                category=jd_skill.category,
                gap_type="weak",
                coverage_score=coverage,
                requirement_type=jd_skill.requirement_type,
                weight=jd_skill.weight,
                closest_match=resume_match.name,
                p_score=0.0
            ))
            continue

        # ── Step 1.5: Skill family match ─────────────────────────────────────
        # e.g. PostgreSQL + MySQL in resume → covers SQL requirement
        family_matches  = SKILL_FAMILIES.get(jd_skill.skill_id, [])
        matched_family  = [fid for fid in family_matches if fid in resume_by_id]

        if matched_family:
            # Multiple family matches = stronger coverage
            base_coverage  = 0.78
            family_bonus   = min(len(matched_family) * 0.06, 0.12)
            coverage       = min(base_coverage + family_bonus, 0.90)

            best_match_name = resume_by_id[matched_family[0]].name

            if coverage >= 0.85:
                # Strong enough — treat as fully covered
                continue

            gap_items.append(GapItem(
                skill_id=jd_skill.skill_id,
                skill_name=jd_skill.name,
                category=jd_skill.category,
                gap_type="weak",
                coverage_score=coverage,
                requirement_type=jd_skill.requirement_type,
                weight=jd_skill.weight,
                closest_match=best_match_name,
                p_score=0.0
            ))
            continue

        # ── Step 2: Semantic similarity match ────────────────────────────────
        best_score      = 0.0
        best_match_name = ""

        if len(resume_vecs) > 0 and len(jd_vecs) > 0:
            jd_vec    = jd_vecs[i]
            scores    = np.dot(resume_vecs, jd_vec)
            best_idx  = int(np.argmax(scores))
            best_score = float(scores[best_idx])
            best_match_name = resume_names[best_idx] if best_score > 0.3 else ""

        if best_score >= threshold:
            gap_items.append(GapItem(
                skill_id=jd_skill.skill_id,
                skill_name=jd_skill.name,
                category=jd_skill.category,
                gap_type="weak",
                coverage_score=best_score,
                requirement_type=jd_skill.requirement_type,
                weight=jd_skill.weight,
                closest_match=best_match_name,
                p_score=0.0
            ))
        else:
            # Truly missing
            gap_items.append(GapItem(
                skill_id=jd_skill.skill_id,
                skill_name=jd_skill.name,
                category=jd_skill.category,
                gap_type="missing",
                coverage_score=max(best_score, 0.0),
                requirement_type=jd_skill.requirement_type,
                weight=jd_skill.weight,
                closest_match=best_match_name,
                p_score=0.0
            ))

    return gap_items


def _level_to_coverage(resume_level: str, required_level: str) -> float:
    """
    Convert skill levels to a numeric coverage score.
    e.g. resume=intermediate, required=expert → 0.65 (partial)
    """
    level_map = {"beginner": 1, "intermediate": 2, "expert": 3}
    r   = level_map.get(resume_level, 2)
    req = level_map.get(required_level, 2)

    if r >= req:
        return 1.0       # meets or exceeds requirement
    elif r == req - 1:
        return 0.65      # one level below
    else:
        return 0.30      # two levels below (beginner vs expert)


def compute_summary_stats(
    resume_skills: List[SkillEntity],
    jd_skills: List[SkillEntity],
    gap_items: List[GapItem]
) -> dict:
    """Compute readiness score and domain breakdown."""

    total_jd = len(jd_skills)
    if total_jd == 0:
        return {
            "readiness_score": 100.0,
            "total_gap_skills": 0,
            "missing_skills": 0,
            "weak_skills": 0,
            "overqualified_skills": 0,
            "total_modules": 0,
            "total_hours": 0.0,
            "domain_breakdown": {}
        }

    missing       = [g for g in gap_items if g.gap_type == "missing"]
    weak          = [g for g in gap_items if g.gap_type == "weak"]
    overqualified = [g for g in gap_items if g.gap_type == "overqualified"]

    # Weighted readiness: required gaps hurt more than preferred
    total_weight = sum(s.weight for s in jd_skills)
    gap_weight   = sum(
        g.weight * (1.0 - g.coverage_score)
        for g in gap_items
        if g.gap_type in ("missing", "weak")
    )
    readiness = max(0.0, min(100.0, (1.0 - gap_weight / total_weight) * 100))

    # Domain breakdown
    domain_breakdown: dict = {}
    for g in gap_items:
        if g.gap_type in ("missing", "weak"):
            from app.services.data_loader import get_skill_by_id
            skill_data = get_skill_by_id(g.skill_id)
            domain = skill_data["domain"] if skill_data else "other"
            domain_breakdown[domain] = domain_breakdown.get(domain, 0) + 1

    return {
        "readiness_score":     round(readiness, 1),
        "total_gap_skills":    len(missing) + len(weak),
        "missing_skills":      len(missing),
        "weak_skills":         len(weak),
        "overqualified_skills":len(overqualified),
        "total_modules":       0,   # filled after pathway generation
        "total_hours":         0.0, # filled after pathway generation
        "domain_breakdown":    domain_breakdown
    }