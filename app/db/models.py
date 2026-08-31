"""
SQLAlchemy ORM models.

These mirror the shape of the Pydantic LearnerProfile / LearningPath
schemas closely enough to round-trip through repository.py, but they are
NOT the same objects — nothing outside app/db/ should import from this
module. Go through repository.py instead, which is the only place that
knows both the ORM and Pydantic shapes.

Hackathon-speed choice: nested structures (target_skills, known_skills,
steps — including each step's full SkillNode/Resource data) are stored as
JSON columns rather than normalized into separate tables. That's fine for
this timeline; normalizing skill nodes/resources/gaps into their own
tables with proper FKs is the natural next step if this goes past the
hackathon.
"""

from sqlalchemy import Column, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class LearnerProfileRecord(Base):
    __tablename__ = "learner_profiles"

    learner_id = Column(String, primary_key=True, index=True)
    target_skills = Column(JSON, nullable=False, default=list)
    known_skills = Column(JSON, nullable=False, default=dict)
    weekly_hours_available = Column(Float, nullable=False)
    raw_goal_text = Column(String, nullable=False)

    path = relationship(
        "LearningPathRecord",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
    )


class LearningPathRecord(Base):
    __tablename__ = "learning_paths"

    # One path per learner (mirrors the old dict's 1:1 learner_id -> path),
    # so learner_id doubles as PK and FK rather than a separate surrogate id.
    learner_id = Column(
        String, ForeignKey("learner_profiles.learner_id"), primary_key=True
    )
    steps = Column(JSON, nullable=False, default=list)
    total_estimated_hours = Column(Float, nullable=False)
    generated_at = Column(String, nullable=False)

    profile = relationship("LearnerProfileRecord", back_populates="path")