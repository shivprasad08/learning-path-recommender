"""
API routes.

Module 11: storage backend is now Postgres via SQLAlchemy (app/db/), swapped
in for the old in-memory `_STORE` dict. Only this storage mechanism changed
-- every service-layer function (profiler.py, gap_detection.py,
path_generator.py, explainer.py, adaptation.py) is untouched, since none of
them depend on how data is stored. The request/response shapes (Pydantic
schemas) and the API contract are unchanged too.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
from app.db.database import get_db
from app.db import repository

router = APIRouter()


@router.post("/profile/{learner_id}", response_model=LearnerProfile)
def create_profile(
    learner_id: str, raw: LearnerProfileInput, db: Session = Depends(get_db)
):
    profile = build_profile(learner_id, raw, skill_graph)
    path = generate_learning_path(profile, skill_graph)
    repository.save_profile_and_path(db, profile, path)
    return profile


@router.get("/path/{learner_id}", response_model=LearningPath)
def get_path(learner_id: str, db: Session = Depends(get_db)):
    _, path = _get_or_404(db, learner_id)
    return path


@router.post("/path/{learner_id}/explain", response_model=ExplanationResponse)
def explain(
    learner_id: str, req: ExplanationRequest, db: Session = Depends(get_db)
):
    profile, path = _get_or_404(db, learner_id)
    try:
        return explain_step(profile, path, req.skill_id, skill_graph)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/path/{learner_id}/assess", response_model=AdaptationResponse)
def assess(learner_id: str, result: AssessmentResult, db: Session = Depends(get_db)):
    profile, _ = _get_or_404(db, learner_id)
    response = apply_assessment(profile, result, skill_graph)
    repository.save_profile_and_path(
        db,
        profile.model_copy(update={"known_skills": {**profile.known_skills}}),
        response.updated_path,
    )
    return response


def _get_or_404(db: Session, learner_id: str) -> tuple[LearnerProfile, LearningPath]:
    record = repository.get_profile_and_path(db, learner_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail=f"No profile found for learner_id={learner_id}"
        )
    return record