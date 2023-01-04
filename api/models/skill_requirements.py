from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from api.database import Base
from api.models.jobs import Job


class SkillRequirement(Base):
    __tablename__ = "jobs_skill_requirements"

    job_id: Mapped[str] = Column(String(36), ForeignKey("jobs_jobs.id"), primary_key=True)
    job: Mapped[Job] = relationship("Job", back_populates="skill_requirements", lazy="selectin")
    skill_id: Mapped[str] = Column(String(36), primary_key=True)
    level: Mapped[int] = Column(Integer)
