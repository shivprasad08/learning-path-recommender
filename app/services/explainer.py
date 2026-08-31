"""
Explainability.

Generates a "why this step" explanation grounded in facts pulled from the
graph and gap scores. Explanations are now LLM-phrased to provide a warm, 
encouraging tone, but fact-gathering and grounding remain fully deterministic 
and unchanged from Module 5. A bad LLM response degrades fluency, never 
correctness, because the fallback produces the same grounded-but-plainer 
template text as before.

Note: Ensure the GROQ_API_KEY environment variable is set before running.
"""

import os
import logging
from app.models.schemas import ExplanationResponse, LearningPath
from app.services.gap_detection import detect_gaps
from app.graph.skill_graph import SkillGraph
from app.models.schemas import LearnerProfile

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


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

    prereq_names_str = "None"
    if prereqs:
        prereq_names = [graph.get_node(p).name for p in prereqs]
        prereq_names_str = ", ".join(prereq_names)
        grounded_on.append(f"prerequisite_edges={prereqs}")
        sentences.append(
            f"This comes after {', '.join(prereq_names)}, which the graph "
            f"marks as required foundations for {node.name}."
        )
    else:
        sentences.append(f"{node.name} has no prerequisites in your path, so it's a good starting point.")

    gap_info_str = "None"
    if gap:
        gap_info_str = f"gap_score={gap.gap_score}, current_level={gap.current_level.value}, required_level={gap.required_level.value}"
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

    template_explanation = " ".join(sentences)
    final_explanation = template_explanation

    api_key = os.environ.get("GROQ_API_KEY")
    if Groq and api_key:
        try:
            client = Groq(api_key=api_key)
            prompt = f"""Rewrite these facts into a warm, concise 2-3 sentence explanation for a learner, in an encouraging tone. 
Facts:
- Prerequisites: {prereq_names_str}
- Gap info: {gap_info_str}
- Learner goal: '{profile.raw_goal_text}'

Do not mention any prerequisite, skill, or score not listed above. Do not invent any new facts or reasons.
"""
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()
            if response_text:
                final_explanation = response_text
        except Exception as e:
            logger.warning(f"LLM rewrite failed: {e}. Falling back to template explanation.")

    # Confidence is lower when we have no gap-score evidence at all —
    # surfaces honestly rather than sounding equally sure every time.
    confidence = 0.9 if gap else 0.6

    return ExplanationResponse(
        skill_id=skill_id,
        explanation=final_explanation,
        grounded_on=grounded_on,
        confidence=confidence,
    )
