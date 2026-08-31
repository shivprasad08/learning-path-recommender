"""
Explainability.

Generates a "why this step" explanation grounded in facts pulled from the
graph and gap scores — never invented. The template-based version below
works standalone (no API key needed) so the team can demo end-to-end
immediately. To upgrade: pass the `grounded_on` facts into an LLM prompt
that rewrites them fluently — the important part (grounding in real edges,
not hallucinated reasoning) is already handled by the time it reaches the
LLM, so a bad LLM call degrades style, not correctness.

    # TODO (upgrade path):
    # explanation = llm_rewrite(grounded_facts, tone="encouraging, concise")
"""

from app.models.schemas import ExplanationResponse, LearningPath
from app.services.gap_detection import detect_gaps
from app.graph.skill_graph import SkillGraph
from app.models.schemas import LearnerProfile


def explain_step(
    profile: LearnerProfile,
    path: LearningPath,
    skill_id: str,
    graph: SkillGraph,
) -> ExplanationResponse:
    step = next((s for s in path.steps if s.skill.id == skill_id), None)
    if step is None:
        raise ValueError(f"Skill '{skill_id}' is not part of this learner's path")

    node = step.skill
    prereqs = graph.prerequisites_of(skill_id)
    gaps = {g.skill_id: g for g in detect_gaps(profile, graph)}
    gap = gaps.get(skill_id)

    grounded_on: list[str] = []
    sentences: list[str] = []

    if prereqs:
        prereq_names = [graph.get_node(p).name for p in prereqs]
        grounded_on.append(f"prerequisite_edges={prereqs}")
        sentences.append(
            f"This comes after {', '.join(prereq_names)}, which the graph "
            f"marks as required foundations for {node.name}."
        )
    else:
        sentences.append(f"{node.name} has no prerequisites in your path, so it's a good starting point.")

    if gap:
        grounded_on.append(f"gap_score={gap.gap_score}")
        sentences.append(
            f"Your current level is '{gap.current_level.value}' against a target of "
            f"'{gap.required_level.value}' — a gap score of {gap.gap_score}, "
            f"which is why it's prioritized in your path."
        )

    sentences.append(
        f"It targets your stated goal ({profile.raw_goal_text[:80]}...)"
        if len(profile.raw_goal_text) > 80
        else f"It targets your stated goal ({profile.raw_goal_text})."
    )

    # Confidence is lower when we have no gap-score evidence at all —
    # surfaces honestly rather than sounding equally sure every time.
    confidence = 0.9 if gap else 0.6

    return ExplanationResponse(
        skill_id=skill_id,
        explanation=" ".join(sentences),
        grounded_on=grounded_on,
        confidence=confidence,
    )
