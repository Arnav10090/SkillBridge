from typing import List
from app.models.schemas import LearningStep, GapItem
from app.core.llm import call_llm

TRACE_SYSTEM = """You are an expert learning advisor inside an onboarding system.
Generate a concise, factual explanation for why a specific course is recommended.
Cite ONLY the data provided. No invented information. Max 3 sentences."""

TRACE_PROMPT = """Generate a recommendation explanation using ONLY this data:

Skill: {skill_name}
Gap Type: {gap_type} (missing = not in resume, weak = present but below required level)
Coverage Score: {coverage_score} (0.0 = completely missing, 1.0 = fully covered)
Requirement: {requirement_type}
Closest resume match: "{closest_match}"
Module: "{module_title}" by {provider} — {hours}h — Difficulty {difficulty}/5
Is implied prerequisite: {is_implied}

Write 2-3 sentences. Start with the gap, cite evidence, end with why this module helps.
Do NOT mention any course not listed above. Be specific and direct."""

FALLBACK_TRACE = (
    "Your resume does not demonstrate {skill_name} at the required level "
    "(coverage: {coverage}%). The role {req_type} this skill. "
    '"{module_title}" ({hours}h) directly addresses this gap.'
)


async def generate_trace(step, closest_match: str = "") -> str:
    """
    Generate reasoning trace using smart template.
    LLM traces are skipped to keep analysis under 60 seconds.
    """
    if not step.modules:
        return f"No course module found for {step.skill_name}. Consider self-study resources."

    module = step.modules[0]

    gap_desc = "is not present" if step.gap_type == "missing" else "needs strengthening"
    prereq_note = " This is a prerequisite skill needed before advancing." if step.is_implied_prereq else ""
    coverage_pct = round(step.coverage_score * 100)
    demand = "requires" if step.gap_type == "missing" else "expects stronger proficiency in"

    trace = (
        f"Your resume shows {coverage_pct}% coverage of {step.skill_name} "
        f"— this skill {gap_desc} at the required level. "
        f"The target role {demand} this skill"
        f"{' (auto-added as a prerequisite)' if step.is_implied_prereq else ''}. "
        f'"{module.title}" ({module.duration_hours}h, {module.provider}) '
        f"directly addresses this gap with difficulty level {module.difficulty}/5.{prereq_note}"
    )

    return trace


async def generate_all_traces(
    pathway: List[LearningStep],
    gap_lookup: dict
) -> List[LearningStep]:
    """Add reasoning traces to all steps in the pathway."""
    for step in pathway:
        gap = gap_lookup.get(step.skill_id)
        closest = gap.closest_match if gap else ""
        step.reasoning_trace = await generate_trace(step, closest_match=closest)
    return pathway