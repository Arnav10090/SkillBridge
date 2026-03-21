import heapq
from typing import List, Dict, Tuple, Set
from app.models.schemas import GapItem, LearningStep, CourseModule, SkillEntity
from app.services.data_loader import (
    get_all_skills, get_prerequisites, get_modules_for_skill,
    get_skill_by_id, build_prerequisite_graph, get_reverse_prerequisite_graph
)
import json as _json
import os as _os

def _load_demand_weights() -> dict:
    """Load data-driven skill demand weights computed from Kaggle datasets."""
    path = _os.path.join(_os.path.dirname(__file__), "..", "data", "skill_frequency_stats.json")
    try:
        with open(path, "r") as f:
            stats = _json.load(f)
        weights = stats.get("skill_demand_weights", {})
        print(f"[WGT] Loaded dataset demand weights for {len(weights)} skills")
        return weights
    except FileNotFoundError:
        print("[WGT] No demand weights found, using defaults")
        return {}

DEMAND_WEIGHTS = _load_demand_weights()

# ─── P-Score Formula ─────────────────────────────────────────────────────────

def compute_p_score(
    gap: GapItem,
    all_gaps: List[GapItem],
    dependency_urgency: float,
    experience_years: int = 0
) -> float:
    """
    Original WGT Priority Score formula:
    P = 0.40 * gap_severity
      + 0.30 * requirement_weight  (boosted by Kaggle JD demand data)
      + 0.20 * dependency_urgency
      + 0.10 * experience_penalty

    Higher P-score = teach this skill sooner.

    Dataset integration:
    - requirement_weight is boosted by data-driven demand weights
      computed from 2277 real job descriptions (Kaggle JD Dataset)
    - High JD frequency skills (e.g. JavaScript, SQL) get priority boost
    """

    # ── Gap severity: how missing is this skill ───────────────────────────────
    # 0.0 = fully covered, 1.0 = completely missing
    gap_severity = 1.0 - gap.coverage_score

    # ── Requirement weight: required > preferred ──────────────────────────────
    # gap.weight = 1.5 if required, 1.0 if preferred
    # Normalize to 0-1 range (max weight is 1.5)
    requirement_weight = min(gap.weight / 1.5, 1.0)

    # ── Dataset demand boost (Kaggle JD Dataset) ──────────────────────────────
    # Skills that appear frequently in real JDs are more valuable to learn
    # demand_boost is a ratio (0.0-1.0) from skill_frequency_stats.json
    demand_boost   = DEMAND_WEIGHTS.get(gap.skill_id, 0.0)
    dataset_factor = min(demand_boost * 0.5, 0.15)  # max +0.15 boost
    requirement_weight = min(requirement_weight + dataset_factor, 1.0)

    # ── Experience penalty: reduce priority of trivial skills ─────────────────
    # Senior hires should skip beginner-level skill recommendations
    experience_penalty = 1.0
    skill_data = get_skill_by_id(gap.skill_id)
    if skill_data:
        skill_difficulty = skill_data.get("difficulty", 2.0)
        if experience_years > 5 and skill_difficulty <= 1.5:
            experience_penalty = 0.2   # senior hire, basic skill → low priority
        elif experience_years > 3 and skill_difficulty <= 1.0:
            experience_penalty = 0.1   # mid hire, intro skill → very low priority

    # ── Final P-Score ─────────────────────────────────────────────────────────
    p_score = (
        0.40 * gap_severity        +   # how missing is it?
        0.30 * requirement_weight  +   # how important is it? (JD + dataset)
        0.20 * dependency_urgency  +   # do other skills depend on it?
        0.10 * experience_penalty      # is it appropriate for this hire's level?
    )

    return round(min(p_score, 1.0), 4)


# ─── Dependency Urgency ───────────────────────────────────────────────────────

def compute_dependency_urgency(
    skill_id: str,
    gap_skill_ids: Set[str]
) -> float:
    """
    How many OTHER gap skills depend on this skill as a prerequisite?
    Higher = teach this first because others depend on it.
    """
    prereq_graph = build_prerequisite_graph()  # {skill_id: [skills that need it]}
    dependents = prereq_graph.get(skill_id, [])

    # Count how many of its dependents are also in our gap list
    blocking_count = sum(1 for d in dependents if d in gap_skill_ids)

    if not gap_skill_ids:
        return 0.0

    return min(blocking_count / len(gap_skill_ids), 1.0)


# ─── Implied Prerequisite Discovery ──────────────────────────────────────────

def discover_implied_prerequisites(
    gap_skill_ids: Set[str],
    resume_skill_ids: Set[str],
    experience_years: int = 0
) -> Set[str]:
    """
    Auto-add missing prerequisites — but only when genuinely needed.
    Senior hires skip easy implied prereqs to avoid 3x hour inflation.
    """
    reverse_graph = get_reverse_prerequisite_graph()
    implied = set()
    visited = set()
    queue = list(gap_skill_ids)

    # Experience floor: skip implied prereqs below this difficulty
    difficulty_floor = 0.0
    if experience_years >= 5:
        difficulty_floor = 3.0   # seniors skip everything below advanced
    elif experience_years >= 2:
        difficulty_floor = 2.0   # mid-level skip beginner prereqs

    while queue:
        skill_id = queue.pop(0)
        if skill_id in visited:
            continue
        visited.add(skill_id)

        prerequisites = reverse_graph.get(skill_id, [])
        for prereq_id in prerequisites:
            if prereq_id in resume_skill_ids or prereq_id in gap_skill_ids:
                continue

            # Check difficulty before adding
            skill_data = get_skill_by_id(prereq_id)
            if skill_data:
                prereq_difficulty = skill_data.get("difficulty", 2.0)
                if prereq_difficulty <= difficulty_floor:
                    continue    # skip — hire already has this level implicitly

            implied.add(prereq_id)
            queue.append(prereq_id)

    return implied


# ─── Topological Sort with P-Score Priority ───────────────────────────────────

def topological_sort_by_p_score(
    skill_ids: List[str],
    p_scores: Dict[str, float]
) -> List[str]:
    """
    Kahn's algorithm + priority queue for P-score tie-breaking.
    Skills with no unlearned prerequisites come first.
    Among those, highest P-score comes first.
    """
    all_prereqs = get_prerequisites()

    # Build in-degree map restricted to our skill set
    skill_set = set(skill_ids)
    in_degree: Dict[str, int] = {sid: 0 for sid in skill_ids}
    adj: Dict[str, List[str]] = {sid: [] for sid in skill_ids}

    for prereq in all_prereqs:
        src = prereq["from"]
        dst = prereq["to"]
        if src in skill_set and dst in skill_set:
            in_degree[dst] += 1
            adj[src].append(dst)

    # Priority queue: (-p_score, skill_id) → highest p_score first
    heap = []
    for sid in skill_ids:
        if in_degree[sid] == 0:
            heapq.heappush(heap, (-p_scores.get(sid, 0.0), sid))

    ordered = []
    while heap:
        neg_p, skill_id = heapq.heappop(heap)
        ordered.append(skill_id)

        for neighbor in adj.get(skill_id, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, (-p_scores.get(neighbor, 0.0), neighbor))

    # Any remaining (cycles or disconnected) — add by p_score order
    remaining = [s for s in skill_ids if s not in ordered]
    remaining.sort(key=lambda s: -p_scores.get(s, 0.0))
    ordered.extend(remaining)

    return ordered


# ─── Difficulty Ramp Enforcement ─────────────────────────────────────────────

def apply_difficulty_ramp(ordered_skill_ids: List[str]) -> List[str]:
    """
    Ensures no two consecutive skills jump more than 1.5 difficulty points.
    Reorders gently to prevent cognitive overload.
    """
    skill_difficulties = {}
    for sid in ordered_skill_ids:
        data = get_skill_by_id(sid)
        skill_difficulties[sid] = data.get("difficulty", 2.0) if data else 2.0

    result = []
    remaining = list(ordered_skill_ids)

    while remaining:
        last_diff = skill_difficulties.get(result[-1], 2.0) if result else 0.0

        # Find the best next skill: highest p_score within acceptable difficulty jump
        best = None
        for sid in remaining:
            diff = skill_difficulties[sid]
            if diff <= last_diff + 1.5:
                best = sid
                break

        if best is None:
            best = remaining[0]  # Force next if no valid candidate

        result.append(best)
        remaining.remove(best)

    return result


# ─── Course Module Selector ───────────────────────────────────────────────────

def select_modules_for_skill(
    skill_id: str,
    coverage_score: float,
    experience_floor: float = 1.0,
    max_modules: int = 2
) -> List[CourseModule]:
    """
    Pick 1-2 best modules for a skill based on:
    - Coverage score (lower coverage → prefer introductory module)
    - Experience floor (senior hires skip beginner modules)
    """
    raw_modules = get_modules_for_skill(skill_id)

    if not raw_modules:
        return []

    # Filter by difficulty range
    min_difficulty = experience_floor if coverage_score > 0.3 else 1.0
    filtered = [
        m for m in raw_modules
        if m["difficulty"] >= min_difficulty
    ]

    if not filtered:
        filtered = raw_modules  # fallback: use all

    # Sort: lower coverage → prefer lower difficulty first
    if coverage_score < 0.4:
        filtered.sort(key=lambda m: m["difficulty"])
    else:
        filtered.sort(key=lambda m: abs(m["difficulty"] - 3.0))  # prefer mid-difficulty

    selected = filtered[:max_modules]

    return [
        CourseModule(
            id=m["id"],
            title=m["title"],
            provider=m["provider"],
            difficulty=m["difficulty"],
            duration_hours=m["duration_hours"],
            url=m["url"],
            description=m["description"]
        )
        for m in selected
    ]


# ─── Main WGT Algorithm ───────────────────────────────────────────────────────

def generate_pathway(
    gap_items: List[GapItem],
    resume_skills: List[SkillEntity],
    experience_years: int = 0,
    seniority: str = "mid"
) -> List[LearningStep]:
    """
    Full WGT pipeline:
    1. Score all gap skills with P-Score
    2. Discover implied prerequisites
    3. Topological sort respecting dependencies
    4. Apply difficulty ramp
    5. Map each skill to course modules
    6. Return ordered LearningStep list
    """

    # Only include actionable gaps (not overqualified)
    actionable_gaps = [g for g in gap_items if g.gap_type in ("missing", "weak")]

    if not actionable_gaps:
        return []

    resume_skill_ids = {s.skill_id for s in resume_skills}
    gap_skill_ids    = {g.skill_id for g in actionable_gaps}

    # ── Step 1: Discover implied prerequisites ────────────────────────────
    implied_ids = discover_implied_prerequisites(gap_skill_ids, resume_skill_ids, experience_years)

    # Build implied gap items for missing prerequisites
    implied_gaps: List[GapItem] = []
    for skill_id in implied_ids:
        skill_data = get_skill_by_id(skill_id)
        if skill_data:
            implied_gaps.append(GapItem(
                skill_id=skill_id,
                skill_name=skill_data["name"],
                category=skill_data.get("category", "technical"),
                gap_type="missing",
                coverage_score=0.0,
                requirement_type="implied",
                weight=1.0,
                closest_match="",
                p_score=0.0
            ))

    all_gaps = actionable_gaps + implied_gaps
    all_gap_ids = {g.skill_id for g in all_gaps}

    # ── Step 2: Compute P-Scores ──────────────────────────────────────────
    p_scores: Dict[str, float] = {}
    for gap in all_gaps:
        dep_urgency = compute_dependency_urgency(gap.skill_id, all_gap_ids)
        p = compute_p_score(gap, all_gaps, dep_urgency, experience_years)
        p_scores[gap.skill_id] = p
        gap.p_score = p

    # ── Step 3: Topological sort with P-Score priority ────────────────────
    ordered_ids = topological_sort_by_p_score(list(all_gap_ids), p_scores)

    # ── Step 4: Difficulty ramp ───────────────────────────────────────────
    ordered_ids = apply_difficulty_ramp(ordered_ids)

    # ── Step 5: Experience floor (skip trivial skills for senior hires) ───
    experience_floor = 1.0
    if seniority == "senior" or experience_years > 5:
        experience_floor = 2.0
    elif seniority == "lead" or experience_years > 8:
        experience_floor = 2.5

    # ── Step 6: Build LearningStep list ──────────────────────────────────
    gap_lookup = {g.skill_id: g for g in all_gaps}
    pathway: List[LearningStep] = []
    step_number = 1

    for skill_id in ordered_ids:
        gap = gap_lookup.get(skill_id)
        if not gap:
            continue

        skill_data = get_skill_by_id(skill_id)
        skill_difficulty = skill_data.get("difficulty", 2.0) if skill_data else 2.0

        # Skip trivially easy skills for experienced hires
        if experience_floor > 1.0 and skill_difficulty < experience_floor and gap.gap_type != "missing":
            continue

        modules = select_modules_for_skill(
            skill_id=skill_id,
            coverage_score=gap.coverage_score,
            experience_floor=experience_floor,
            max_modules=2
        )

        # Estimate hours: base hours × (1 + gap severity bonus)
        base_hours = sum(m.duration_hours for m in modules)
        gap_severity = 1.0 - gap.coverage_score
        estimated_hours = round(base_hours * (1.0 + 0.3 * gap_severity), 1)

        step = LearningStep(
            step_number=step_number,
            skill_id=skill_id,
            skill_name=gap.skill_name,
            skill_category=gap.category,
            gap_type=gap.gap_type,
            coverage_score=gap.coverage_score,
            p_score=p_scores.get(skill_id, 0.0),
            difficulty=skill_difficulty,
            modules=modules,
            estimated_hours=estimated_hours,
            reasoning_trace="",      # filled by trace generator in Step 7
            is_implied_prereq=(gap.requirement_type == "implied")
        )

        pathway.append(step)
        step_number += 1

    return pathway