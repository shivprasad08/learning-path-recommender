"""
Path generation.

Takes the learner's gaps + target skills, builds the minimal subgraph of
prerequisites needed, and orders it topologically (prereqs before
dependents) with difficulty tier as the tiebreak so the ramp feels sensible
rather than arbitrary. This is the module everything else in Stage 3/4
depends on — keep its output (LearningPath) stable.
"""

from datetime import datetime, timezone

from app.models.schemas import LearnerProfile, LearningPath, PathStep, SkillLevel
from app.graph.skill_graph import SkillGraph
from app.services.gap_detection import detect_gaps


def generate_learning_path(profile: LearnerProfile, graph: SkillGraph) -> LearningPath:
    gaps = detect_gaps(profile, graph)
    gap_by_skill = {g.skill_id: g for g in gaps}

    # Skills the learner already knows well enough don't need to be
    # re-taught — exclude anything with zero gap from the walkable subgraph.
    skills_needing_work = list(gap_by_skill.keys())

    if not skills_needing_work:
        # Learner already meets every target skill.
        return LearningPath(
            learner_id=profile.learner_id,
            steps=[],
            total_estimated_hours=0.0,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    subgraph = graph.subgraph_for_targets(profile.target_skills)
    # Only keep nodes that are actually part of the gap (drop already-known
    # ancestors so the path doesn't re-teach mastered material).
    subgraph = subgraph.subgraph(
        [n for n in subgraph.nodes if n in gap_by_skill]
    ).copy()

    ordered_ids = graph.topological_order(subgraph)

    # Stable secondary sort by difficulty tier within topologically-valid
    # positions, so e.g. two independent foundational skills present in a
    # sensible easy-to-hard order rather than insertion order.
    ordered_ids = _stable_difficulty_sort(ordered_ids, subgraph, graph)

    steps: list[PathStep] = []
    total_hours = 0.0
    for i, skill_id in enumerate(ordered_ids):
        node = graph.get_node(skill_id)
        step_hours = sum(r.est_hours for r in node.resources)
        total_hours += step_hours
        steps.append(
            PathStep(
                order=i + 1,
                skill=node,
                reason=None,  # filled in by the explainer (Stage 3)
                mastery_score=0.0,
                is_unlocked=(i == 0),  # only the first step starts unlocked
            )
        )

    return LearningPath(
        learner_id=profile.learner_id,
        steps=steps,
        total_estimated_hours=round(total_hours, 1),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def _stable_difficulty_sort(ordered_ids, subgraph, graph: SkillGraph) -> list[str]:
    """
    Within the constraint that every prerequisite must still precede its
    dependents, nudge same-depth nodes into easy-to-hard order. Computed by
    a simple pass: for each node, if swapping with the next same-eligible
    node would still respect all edges, prefer the lower difficulty_tier.
    Kept intentionally simple (bubble-style single pass) — this is a
    presentation nicety, not the core correctness guarantee.
    """
    ids = list(ordered_ids)
    for i in range(len(ids) - 1):
        a, b = ids[i], ids[i + 1]
        # Only swap if it doesn't break topological validity, i.e. `a` is
        # not a prerequisite of `b`.
        if not subgraph.has_edge(a, b):
            if graph.get_node(a).difficulty_tier > graph.get_node(b).difficulty_tier:
                ids[i], ids[i + 1] = b, a
    return ids
