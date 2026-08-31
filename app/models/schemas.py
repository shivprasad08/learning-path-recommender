"""
Core data contracts for the Learning Path Recommender.

These schemas are the API contract between the backend (you) and the
frontend/data team members. Keep field names stable once shared — changing
them mid-build breaks whatever the frontend has already wired up.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SkillLevel(str, Enum):
    NONE = "none"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ResourceType(str, Enum):
    COURSE = "course"
    VIDEO = "video"
    ARTICLE = "article"
    PROJECT = "project"
    ASSESSMENT = "assessment"


# ---------------------------------------------------------------------------
# Skill graph primitives
# ---------------------------------------------------------------------------

class Resource(BaseModel):
    """A single learning resource attached to a skill node."""
    id: str
    title: str
    type: ResourceType
    url: Optional[str] = None
    est_hours: float = Field(default=2.0, description="Estimated hours to complete")


class SkillNode(BaseModel):
    """One node in the prerequisite DAG."""
    id: str
    name: str
    category: str
    difficulty_tier: int = Field(ge=1, le=5, description="1=foundational, 5=advanced")
    prerequisites: list[str] = Field(default_factory=list, description="IDs of prerequisite skill nodes")
    resources: list[Resource] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Learner profile (Stage 1 output -> Stage 2 input)
# ---------------------------------------------------------------------------

class LearnerProfileInput(BaseModel):
    """Raw input captured from the conversational/form intake."""
    raw_goal_text: str = Field(description="Free-text description of what the learner wants to achieve")
    known_skills: dict[str, SkillLevel] = Field(
        default_factory=dict,
        description="skill_id -> current level, if the learner self-reports or it's parsed from a resume",
    )
    weekly_hours_available: float = Field(default=5.0, gt=0)
    target_role: Optional[str] = None


class LearnerProfile(BaseModel):
    """Structured profile after LLM extraction — this is what Stage 2 consumes."""
    learner_id: str
    target_skills: list[str] = Field(description="Skill node IDs the learner needs for their goal")
    known_skills: dict[str, SkillLevel]
    weekly_hours_available: float
    raw_goal_text: str


# ---------------------------------------------------------------------------
# Stage 2: gap detection + path generation
# ---------------------------------------------------------------------------

class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    current_level: SkillLevel
    required_level: SkillLevel
    gap_score: float = Field(description="0.0 (no gap) to 1.0 (full gap)")


class PathStep(BaseModel):
    """One node placed into the learner's ordered roadmap."""
    order: int
    skill: SkillNode
    reason: Optional[str] = None  # filled in by the explainer, Stage 3
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0)
    is_unlocked: bool = True  # False if prerequisites aren't yet satisfied


class LearningPath(BaseModel):
    learner_id: str
    steps: list[PathStep]
    total_estimated_hours: float
    generated_at: str  # ISO timestamp, set by the service layer


class PathGenerationRequest(BaseModel):
    profile: LearnerProfile


# ---------------------------------------------------------------------------
# Stage 3: explainability
# ---------------------------------------------------------------------------

class ExplanationRequest(BaseModel):
    learner_id: str
    skill_id: str  # which step in the path they're asking about


class ExplanationResponse(BaseModel):
    skill_id: str
    explanation: str
    grounded_on: list[str] = Field(description="Prerequisite edges / gap scores this explanation was grounded in")
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Stage 4: adaptation loop
# ---------------------------------------------------------------------------

class AssessmentResult(BaseModel):
    learner_id: str
    skill_id: str
    score: float = Field(ge=0.0, le=1.0, description="Fraction correct on the post-milestone quiz")


class AdaptationResponse(BaseModel):
    updated_path: LearningPath
    changes: list[str] = Field(description="Human-readable summary of what changed and why")
