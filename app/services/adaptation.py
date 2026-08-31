"""
Adaptation loop.

After a post-milestone assessment, update the learner's demonstrated skill
level and regenerate the remaining path. This is what should visibly
reshape the DAG in the demo video — a skill scored highly enough gets
marked mastered and drops out of the remaining path; the rest re-flows.
"""

from app.models.schemas import (
    AssessmentResult,
    AdaptationResponse,
    LearnerProfile,
    SkillLevel,
)
from app.graph.skill_graph import SkillGraph
from app.services.path_generator import generate_learning_path

# Score thresholds for converting an assessment result into a skill level.
# Kept simple and explainable on purpose.
_MASTERY_THRESHOLD = 0.8
_PARTIAL_THRESHOLD = 0.5


def apply_assessment(
    profile: LearnerProfile,
    result: AssessmentResult,
    graph: SkillGraph,
) -> AdaptationResponse:
    changes: list[str] = []

    if result.score >= _MASTERY_THRESHOLD:
        new_level = SkillLevel.ADVANCED
        changes.append(
            f"'{graph.get_node(result.skill_id).name}' marked ADVANCED "
            f"(assessment score {result.score:.0%}) — removed from remaining path."
        )
    elif result.score >= _PARTIAL_THRESHOLD:
        new_level = SkillLevel.INTERMEDIATE
        changes.append(
            f"'{graph.get_node(result.skill_id).name}' marked INTERMEDIATE "
            f"(assessment score {result.score:.0%}) — may still need reinforcement."
        )
    else:
        new_level = profile.known_skills.get(result.skill_id, SkillLevel.NONE)
        changes.append(
            f"'{graph.get_node(result.skill_id).name}' assessment score "
            f"({result.score:.0%}) was low — kept in the path, not yet mastered."
        )

    updated_profile = profile.model_copy(
        update={
            "known_skills": {**profile.known_skills, result.skill_id: new_level},
        }
    )

    updated_path = generate_learning_path(updated_profile, graph)

    return AdaptationResponse(updated_path=updated_path, changes=changes)
