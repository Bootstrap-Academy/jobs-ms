from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship

from api.database import Base, db
from api.models.companies import Company


if TYPE_CHECKING:
    from . import SkillRequirement


class JobType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"
    MINI_JOB = "mini_job"


class Job(Base):
    __tablename__ = "jobs_jobs"

    id: Mapped[str] = Column(String(36), primary_key=True, unique=True)
    company_id: Mapped[str] = Column(String(36), ForeignKey("jobs_companies.id"))
    company: Mapped[Company] = relationship("Company", back_populates="jobs", lazy="selectin")
    title: Mapped[str] = Column(Text)
    description: Mapped[str] = Column(Text)
    location: Mapped[str] = Column(Text)
    remote: Mapped[bool] = Column(Boolean)
    type: Mapped[JobType] = Column(Enum(JobType))
    contact: Mapped[str] = Column(Text)
    skill_requirements: list[SkillRequirement] = relationship(
        "SkillRequirement", back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )

    def serialize(self, *, include_contact: bool) -> dict[str, Any]:
        return {
            "id": self.id,
            "company": self.company.serialize,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "remote": self.remote,
            "type": self.type,
            "contact": self.contact if include_contact else None,
            "skill_requirements": {req.skill_id for req in self.skill_requirements},
        }

    @classmethod
    async def create(
        cls,
        company_id: str,
        title: str,
        description: str,
        location: str,
        remote: bool,
        type: JobType,
        contact: str,
        skill_requirements: set[str],
    ) -> Job:
        from . import SkillRequirement

        job_id = str(uuid4())
        job = cls(
            id=job_id,
            company_id=company_id,
            title=title,
            description=description,
            location=location,
            remote=remote,
            type=type,
            contact=contact,
            skill_requirements=[SkillRequirement(job_id=job_id, skill_id=skill_id) for skill_id in skill_requirements],
        )
        await db.add(job)
        return job
