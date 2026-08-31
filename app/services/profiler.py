"""
Learner profiling.

Baseline version below does keyword matching against the skill taxonomy so
the API works end-to-end without any API key. Upgrade this to structured
LLM extraction before submission — it's the highest-visibility "AI/ML
Implementation" point in Stage 1, and the swap is contained to this one
function since everything downstream just consumes a LearnerProfile.

    # TODO (upgrade path):
    # Use function-calling / structured output (e.g. LangChain's
    # `.with_structured_output(LearnerProfile)` against a Pydantic schema)
    # to extract target_skills and known_skills directly from
    # `raw_goal_text`, instead of keyword matching.
"""

from app.models.schemas import LearnerProfileInput, LearnerProfile
from app.graph.skill_graph import SkillGraph


def build_profile(learner_id: str, raw: LearnerProfileInput, graph: SkillGraph) -> LearnerProfile:
    goal_text_lower = raw.raw_goal_text.lower()

    matched_targets: list[str] = []
    for skill_id, node in graph.nodes_by_id.items():
        if node.name.lower() in goal_text_lower or skill_id.replace("_", " ") in goal_text_lower:
            matched_targets.append(skill_id)

    # Fallback: if nothing matched, default to the most advanced node(s) in
    # the seed graph so the pipeline always has a target to plan toward
    # during a demo, rather than erroring out on an unrecognized goal.
    if not matched_targets:
        max_tier = max(n.difficulty_tier for n in graph.nodes_by_id.values())
        matched_targets = [
            n.id for n in graph.nodes_by_id.values() if n.difficulty_tier == max_tier
        ]

    return LearnerProfile(
        learner_id=learner_id,
        target_skills=matched_targets,
        known_skills=raw.known_skills,
        weekly_hours_available=raw.weekly_hours_available,
        raw_goal_text=raw.raw_goal_text,
    )
