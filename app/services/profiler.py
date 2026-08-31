"""
Learner profiling.

LLM extraction is now primary for extracting target skills from raw goal text,
using semantic understanding rather than exact keyword matches. The Module 3
keyword-matching logic serves as a fallback safety net for API failures.

Note: Ensure the GROQ_API_KEY environment variable is set before running.
"""

import os
import json
import logging
from pydantic import BaseModel, ValidationError
from app.models.schemas import LearnerProfileInput, LearnerProfile
from app.graph.skill_graph import SkillGraph

logger = logging.getLogger(__name__)

class ExtractedTargets(BaseModel):
    target_skill_ids: list[str]

def build_profile(learner_id: str, raw: LearnerProfileInput, graph: SkillGraph) -> LearnerProfile:
    matched_targets: list[str] = []
    
    api_key = os.environ.get("GROQ_API_KEY")
    llm_success = False

    if api_key:
        try:
            from groq import Groq 
            client = Groq(api_key=api_key)
            
            skills_context = "\n".join([f"- {skill_id}: {node.name}" for skill_id, node in graph.nodes_by_id.items()])
            
            sys_prompt = (
                "You are an expert learning path recommender. "
                "Your task is to extract which skills a learner is plausibly targeting based on their goal description. "
                "Rely on semantic understanding (e.g. 'build scalable systems' -> scalability, system_design_basics, microservices). "
                "Output MUST be valid JSON matching this schema: {\"target_skill_ids\": [\"skill_1\", \"skill_2\"]}. "
                "You must ONLY use skill IDs from the provided list."
            )
            
            user_prompt = f"Available Skills:\n{skills_context}\n\nLearner Goal: {raw.raw_goal_text}"
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama3-8b-8192",
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            content = chat_completion.choices[0].message.content
            extracted = ExtractedTargets.model_validate_json(content)
            
            # VALIDATE every returned skill_id
            for s_id in extracted.target_skill_ids:
                if s_id in graph.nodes_by_id:
                    matched_targets.append(s_id)
                else:
                    logger.warning(f"LLM returned invalid skill ID: {s_id}")
            
            if matched_targets:
                llm_success = True
                
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}. Falling back to keyword matching.")

    # Fallback to keyword matching
    if not llm_success:
        goal_text_lower = raw.raw_goal_text.lower()
        for skill_id, node in graph.nodes_by_id.items():
            if node.name.lower() in goal_text_lower or skill_id.replace("_", " ") in goal_text_lower:
                if skill_id not in matched_targets:
                    matched_targets.append(skill_id)

    # Secondary fallback if still empty
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
