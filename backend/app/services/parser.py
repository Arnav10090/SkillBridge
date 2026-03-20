import re
import json
import pdfplumber
import docx as python_docx
from typing import Tuple
from app.core.llm import call_llm
from app.models.schemas import SkillEntity
from app.services.data_loader import get_skill_aliases_map, get_all_skills

# ─── Text Extraction ────────────────────────────────────────────────────────

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from PDF or DOCX bytes."""
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(file_bytes: bytes) -> str:
    import io
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n".join(text_parts)


def _extract_docx(file_bytes: bytes) -> str:
    import io
    doc = python_docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])


# ─── LLM Skill Extraction ────────────────────────────────────────────────────

RESUME_SYSTEM_PROMPT = """You are a precision skill extraction engine for HR analytics.
Extract ONLY verifiable skills from the provided resume text.
Return STRICT JSON only. No prose. No markdown. No extra text.
If a skill is ambiguous, include it with low confidence.
NEVER invent skills not present in the text."""

RESUME_USER_PROMPT = """Extract all skills from this resume. Return ONLY this JSON structure:

{{
  "skills": [
    {{
      "name": "skill name in plain English",
      "category": "technical" or "soft" or "domain" or "tool",
      "level": "beginner" or "intermediate" or "expert",
      "evidence": "short quote or phrase from text that proves this skill",
      "confidence": 0.0 to 1.0
    }}
  ],
  "total_experience_years": integer,
  "primary_domain": "e.g. software_engineering or data_science or marketing"
}}

Resume text:
{text}"""


JD_SYSTEM_PROMPT = """You are a job requirements extraction engine.
Extract all required and preferred skills from the job description.
Return STRICT JSON only. No prose. No markdown. No extra text."""

JD_USER_PROMPT = """Extract all skills from this job description. Return ONLY this JSON structure:

{{
  "skills": [
    {{
      "name": "skill name in plain English",
      "category": "technical" or "soft" or "domain" or "tool",
      "level": "beginner" or "intermediate" or "expert",
      "requirement_type": "required" or "preferred",
      "evidence": "exact phrase from JD",
      "confidence": 0.0 to 1.0
    }}
  ],
  "role_title": "job title",
  "seniority_level": "junior" or "mid" or "senior" or "lead",
  "primary_domain": "e.g. software_engineering or data_science"
}}

Job Description text:
{text}"""


# ─── Alias-Based Fallback Extraction ────────────────────────────────────────

def alias_based_extraction(text: str) -> list[dict]:
    alias_map = get_skill_aliases_map()
    all_skills = {s["id"]: s for s in get_all_skills()}
    text_lower = text.lower()
    found = {}

    # ── Explicit evidence patterns for soft skills ───────────────
    EVIDENCE_PATTERNS = {
        "SOFT_PROB": [
            r"leetcode", r"solved \d+", r"problem.{0,10}solv",
            r"algorithms?", r"data structures?", r"dsa", r"competitive"
        ],
        "SOFT_LEAD": [
            r"led\b", r"managed\b", r"mentored?", r"tech lead", r"team lead"
        ],
        "ALGO_DS": [
            r"leetcode", r"solved \d+.*problem", r"\d+\+?\s*problems",
            r"dynamic programming", r"graph algorithm"
        ],
    }

    for skill_id, patterns in EVIDENCE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                skill_data = all_skills.get(skill_id)
                if skill_data and skill_id not in found:
                    found[skill_id] = {
                        "name": skill_data["name"],
                        "category": skill_data["category"],
                        "level": "intermediate",
                        "evidence": f"Pattern '{pattern}' matched in document",
                        "confidence": 0.80
                    }
                break
    """
    Fallback: scan text for known skill aliases.
    Used when LLM fails or as a cross-check.
    """
    alias_map = get_skill_aliases_map()
    all_skills = {s["id"]: s for s in get_all_skills()}
    text_lower = text.lower()
    found = {}

    for alias, skill_id in alias_map.items():
        # Word boundary match to avoid partial matches
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            if skill_id not in found:
                skill_data = all_skills[skill_id]
                found[skill_id] = {
                    "name": skill_data["name"],
                    "category": skill_data["category"],
                    "level": "intermediate",
                    "evidence": f"Found '{alias}' in document",
                    "confidence": 0.75
                }

    return list(found.values())


# ─── Normalize LLM Output → SkillEntity ─────────────────────────────────────

def normalize_skills(
    raw_skills: list[dict],
    doc_type: str = "resume",
    experience_years: int = 0
) -> list[SkillEntity]:
    """
    Map LLM-extracted skill names to our taxonomy IDs.
    Falls back to fuzzy matching if exact alias not found.
    """
    alias_map = get_skill_aliases_map()
    all_skills = {s["id"]: s for s in get_all_skills()}
    normalized = []

    for raw in raw_skills:
        raw_name = raw.get("name", "").strip().lower()
        if not raw_name:
            continue

        # 1. Exact alias lookup
        skill_id = alias_map.get(raw_name)

        # 2. Partial match — check if any alias is a substring
        if not skill_id:
            for alias, sid in alias_map.items():
                if alias in raw_name or raw_name in alias:
                    skill_id = sid
                    break

        # 3. If still not found, create a generic entry
        if not skill_id:
            skill_id = "CUSTOM_" + raw_name.upper().replace(" ", "_")[:20]

        taxonomy_skill = all_skills.get(skill_id, {})

        # Determine weight based on requirement type
        req_type = raw.get("requirement_type", "preferred")
        weight = 1.5 if req_type == "required" else 1.0

        # Determine level based on experience years if not set
        level = raw.get("level", "intermediate")
        if experience_years > 7:
            if level == "beginner":
                level = "intermediate"
        elif experience_years < 2:
            if level == "expert":
                level = "intermediate"

        entity = SkillEntity(
            skill_id=skill_id,
            name=raw.get("name", skill_id),
            category=raw.get("category", taxonomy_skill.get("category", "technical")),
            level=level,
            evidence=raw.get("evidence", ""),
            confidence=float(raw.get("confidence", 0.8)),
            weight=weight,
            requirement_type=req_type
        )
        normalized.append(entity)

    # Deduplicate by skill_id (keep highest confidence)
    seen = {}
    for skill in normalized:
        if skill.skill_id not in seen or skill.confidence > seen[skill.skill_id].confidence:
            seen[skill.skill_id] = skill

    return list(seen.values())


# ─── Safe JSON Parser ────────────────────────────────────────────────────────

def safe_parse_json(text: str) -> dict:
    """Robustly extract JSON from LLM output even with extra text."""
    # Strip markdown code fences
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find JSON object within text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"skills": [], "total_experience_years": 0, "primary_domain": "unknown"}


# ─── Main Parse Functions ─────────────────────────────────────────────────────

async def parse_resume(text: str) -> Tuple[list[SkillEntity], int, str]:
    """
    Returns: (skills, experience_years, primary_domain)
    """
    try:
        prompt = RESUME_USER_PROMPT.format(text=text[:4000])  # Trim to token limit
        raw_response = await call_llm(prompt, system=RESUME_SYSTEM_PROMPT, temperature=0.1)
        parsed = safe_parse_json(raw_response)

        experience_years = int(parsed.get("total_experience_years", 0))
        primary_domain = parsed.get("primary_domain", "general")
        raw_skills = parsed.get("skills", [])

        # If LLM returned nothing, fall back to alias scan
        if not raw_skills:
            raw_skills = alias_based_extraction(text)

        skills = normalize_skills(raw_skills, doc_type="resume", experience_years=experience_years)

        # Enrich with alias fallback (adds any skills LLM missed)
        alias_skills_raw = alias_based_extraction(text)
        alias_skills = normalize_skills(alias_skills_raw, doc_type="resume", experience_years=experience_years)

        # Merge: prefer LLM results, add alias-found skills not already present
        existing_ids = {s.skill_id for s in skills}
        for alias_skill in alias_skills:
            if alias_skill.skill_id not in existing_ids:
                alias_skill.confidence = 0.70  # Lower confidence for alias-only finds
                skills.append(alias_skill)
                existing_ids.add(alias_skill.skill_id)

        return skills, experience_years, primary_domain

    except Exception as e:
        print(f"[Parser] LLM parse failed, using alias fallback: {e}")
        raw_skills = alias_based_extraction(text)
        skills = normalize_skills(raw_skills, doc_type="resume")
        return skills, 0, "general"


async def parse_jd(text: str) -> Tuple[list[SkillEntity], str, str]:
    """
    Returns: (skills, role_title, seniority_level)
    """
    try:
        prompt = JD_USER_PROMPT.format(text=text[:4000])
        raw_response = await call_llm(prompt, system=JD_SYSTEM_PROMPT, temperature=0.1)
        parsed = safe_parse_json(raw_response)

        role_title = parsed.get("role_title", "Unknown Role")
        seniority = parsed.get("seniority_level", "mid")
        raw_skills = parsed.get("skills", [])

        if not raw_skills:
            raw_skills = alias_based_extraction(text)
            for s in raw_skills:
                s["requirement_type"] = "required"

        skills = normalize_skills(raw_skills, doc_type="jd")

        # Alias fallback enrichment
        alias_skills_raw = alias_based_extraction(text)
        for s in alias_skills_raw:
            s["requirement_type"] = "preferred"
        alias_skills = normalize_skills(alias_skills_raw, doc_type="jd")

        existing_ids = {s.skill_id for s in skills}
        for alias_skill in alias_skills:
            if alias_skill.skill_id not in existing_ids:
                alias_skill.confidence = 0.70
                skills.append(alias_skill)
                existing_ids.add(alias_skill.skill_id)

        return skills, role_title, seniority

    except Exception as e:
        print(f"[Parser] JD LLM parse failed, using alias fallback: {e}")
        raw_skills = alias_based_extraction(text)
        for s in raw_skills:
            s["requirement_type"] = "required"
        skills = normalize_skills(raw_skills, doc_type="jd")
        return skills, "Unknown Role", "mid"