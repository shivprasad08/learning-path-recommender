"""
Skill-gap detection.

Baseline implementation compares the learner's self-reported/parsed skill
levels against what each target skill requires, using an ordinal distance.
This is intentionally simple and fully explainable — swap in embedding-based
similarity (e.g. sentence-transformers on skill descriptions) only if you
need to match *free-text* skills to taxonomy nodes; once skills are already
mapped to node IDs, ordinal comparison is the right tool, not overkill ML.
"""

from app.models.schemas import LearnerProfile, SkillGap, SkillLevel
from app.graph.skill_graph import SkillGraph

_LEVEL_ORDER = {
    SkillLevel.NONE: 0,
    SkillLevel.BEGINNER: 1,
    SkillLevel.INTERMEDIATE: 2,
    SkillLevel.ADVANCED: 3,
}

# A target skill is assumed to require at least INTERMEDIATE proficiency
# to be considered "achieved" for path-planning purposes.
_REQUIRED_LEVEL_FOR_TARGET = SkillLevel.INTERMEDIATE


def detect_gaps(profile: LearnerProfile, graph: SkillGraph) -> list[SkillGap]:
    gaps: list[SkillGap] = []

    # Every skill that feeds into a target (the target itself + all its
    # ancestors) is in scope for gap analysis, not just the target itself.
    relevant_skill_ids: set[str] = set()
    for target_id in profile.target_skills:
        relevant_skill_ids.add(target_id)
        relevant_skill_ids |= graph.all_ancestors(target_id)

    for skill_id in relevant_skill_ids:
        node = graph.get_node(skill_id)
        current_level = profile.known_skills.get(skill_id, SkillLevel.NONE)
        required_level = _REQUIRED_LEVEL_FOR_TARGET

        current_rank = _LEVEL_ORDER[current_level]
        required_rank = _LEVEL_ORDER[required_level]
        max_rank = _LEVEL_ORDER[SkillLevel.ADVANCED]

        gap_score = max(0.0, (required_rank - current_rank) / max_rank)

        if gap_score > 0:
            gaps.append(
                SkillGap(
                    skill_id=skill_id,
                    skill_name=node.name,
                    current_level=current_level,
                    required_level=required_level,
                    gap_score=round(gap_score, 2),
                )
            )

    # Largest gaps first — feeds naturally into path prioritization.
    gaps.sort(key=lambda g: g.gap_score, reverse=True)
    return gaps
