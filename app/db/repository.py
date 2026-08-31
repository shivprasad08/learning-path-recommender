"""
Repository layer — the ONLY bridge between the Pydantic schemas used
everywhere else in the codebase (app/models/schemas.py) and the SQLAlchemy
ORM records used only inside app/db/ (models.py).

Mirrors the two operations the old `_STORE` dict supported:
    _STORE[learner_id] = (profile, path)   -> save_profile_and_path(...)
    _STORE[learner_id]                     -> get_profile_and_path(...)

routes.py should call these functions and never import app.db.models
directly.
"""

from sqlalchemy.orm import Session

from app.db.models import LearnerProfileRecord, LearningPathRecord
from app.models.schemas import LearnerProfile, LearningPath


def save_profile_and_path(
    session: Session, profile: LearnerProfile, path: LearningPath
) -> None:
    """Upsert both records for this learner_id in a single transaction."""
    profile_data = profile.model_dump(mode="json")
    path_data = path.model_dump(mode="json")

    profile_record = session.get(LearnerProfileRecord, profile.learner_id)
    if profile_record is None:
        profile_record = LearnerProfileRecord(learner_id=profile.learner_id)
        session.add(profile_record)

    profile_record.target_skills = profile_data["target_skills"]
    profile_record.known_skills = profile_data["known_skills"]
    profile_record.weekly_hours_available = profile_data["weekly_hours_available"]
    profile_record.raw_goal_text = profile_data["raw_goal_text"]

    path_record = session.get(LearningPathRecord, path.learner_id)
    if path_record is None:
        path_record = LearningPathRecord(learner_id=path.learner_id)
        session.add(path_record)

    path_record.steps = path_data["steps"]
    path_record.total_estimated_hours = path_data["total_estimated_hours"]
    path_record.generated_at = path_data["generated_at"]

    session.commit()


def get_profile_and_path(
    session: Session, learner_id: str
) -> tuple[LearnerProfile, LearningPath] | None:
    """Returns None if no profile exists for learner_id (mirrors dict.get)."""
    profile_record = session.get(LearnerProfileRecord, learner_id)
    path_record = session.get(LearningPathRecord, learner_id)

    if profile_record is None or path_record is None:
        return None

    profile = LearnerProfile(
        learner_id=profile_record.learner_id,
        target_skills=profile_record.target_skills,
        known_skills=profile_record.known_skills,
        weekly_hours_available=profile_record.weekly_hours_available,
        raw_goal_text=profile_record.raw_goal_text,
    )
    path = LearningPath(
        learner_id=path_record.learner_id,
        steps=path_record.steps,
        total_estimated_hours=path_record.total_estimated_hours,
        generated_at=path_record.generated_at,
    )
    return profile, path