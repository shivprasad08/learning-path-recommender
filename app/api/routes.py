"""
API routes.

In-memory store used here for hackathon speed (profiles/paths keyed by
learner_id). Swap for Postgres persistence when the data/deployment
teammate wires up the DB — the service-layer functions don't care where
the LearnerProfile/LearningPath came from, so this swap doesn't touch
Stage 2-4 logic at all.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    LearnerProfileInput,
    LearnerProfile,
    LearningPath,
    ExplanationRequest,
    ExplanationResponse,
    AssessmentResult,
    AdaptationResponse,
)
from app.graph.skill_graph import skill_graph
from app.services.profiler import build_profile
from app.services.path_generator import generate_learning_path
from app.services.explainer import explain_step
from app.services.adaptation import apply_assessment

router = APIRouter()

# learner_id -> (LearnerProfile, LearningPath)
_STORE: dict[str, tuple[LearnerProfile, LearningPath]] = {}


@router.post("/profile/{learner_id}", response_model=LearnerProfile)
def create_profile(learner_id: str, raw: LearnerProfileInput):
    profile = build_profile(learner_id, raw, skill_graph)
    path = generate_learning_path(profile, skill_graph)
    _STORE[learner_id] = (profile, path)
    return profile


@router.get("/path/{learner_id}", response_model=LearningPath)
def get_path(learner_id: str):
    _, path = _get_or_404(learner_id)
    return path


@router.post("/path/{learner_id}/explain", response_model=ExplanationResponse)
def explain(learner_id: str, req: ExplanationRequest):
    profile, path = _get_or_404(learner_id)
    try:
        return explain_step(profile, path, req.skill_id, skill_graph)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/path/{learner_id}/assess", response_model=AdaptationResponse)
def assess(learner_id: str, result: AssessmentResult):
    profile, _ = _get_or_404(learner_id)
    response = apply_assessment(profile, result, skill_graph)
    _STORE[learner_id] = (
        profile.model_copy(update={"known_skills": {**profile.known_skills}}),
        response.updated_path,
    )
    return response


def _get_or_404(learner_id: str) -> tuple[LearnerProfile, LearningPath]:
    if learner_id not in _STORE:
        raise HTTPException(status_code=404, detail=f"No profile found for learner_id={learner_id}")
    return _STORE[learner_id]
