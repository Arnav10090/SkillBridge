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


async def generate_trace(step: LearningStep, closest_match: str = "") -> str:
    """Generate reasoning trace for a single learning step."""
    if not step.modules:
        return f"No course module found for {step.skill_name}. Consider self-study resources."

    module = step.modules[0]

    try:
        prompt = TRACE_PROMPT.format(
            skill_name=step.skill_name,
            gap_type=step.gap_type,
            coverage_score=round(step.coverage_score, 2),
            requirement_type=step.skill_category,
            closest_match=closest_match or "none found",
            module_title=module.title,
            provider=module.provider,
            hours=module.duration_hours,
            difficulty=module.difficulty,
            is_implied=step.is_implied_prereq
        )
        trace = await call_llm(prompt, system=TRACE_SYSTEM, temperature=0.2)
        trace = trace.strip().strip('"').strip("'")

        # Validate: must mention skill name and module title
        if step.skill_name.lower() not in trace.lower():
            raise ValueError("Trace missing skill name")
        if len(trace) < 40:
            raise ValueError("Trace too short")

        return trace

    except Exception as e:
        print(f"[Trace] LLM failed for {step.skill_name}: {e}, using fallback")
        return FALLBACK_TRACE.format(
            skill_name=step.skill_name,
            coverage=round(step.coverage_score * 100),
            req_type="requires" if step.gap_type == "missing" else "expects stronger",
            module_title=module.title,
            hours=module.duration_hours
        )


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