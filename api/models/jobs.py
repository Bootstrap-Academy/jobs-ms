from __future__ import annotations

import enum
import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship

from ..database.database import UTCDateTime
from ..utils.utc import utcnow
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


class ProfessionalLevel(enum.Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    SENIOR = "senior"
    MANAGER = "manager"


class SalaryPer(enum.Enum):
    ONCE = "once"
    TASK = "task"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"


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
    _responsibilities: Mapped[str] = Column(Text)
    professional_level: Mapped[ProfessionalLevel] = Column(Enum(ProfessionalLevel))
    salary_min: Mapped[int] = Column(BigInteger)
    salary_max: Mapped[int] = Column(BigInteger)
    salary_unit: Mapped[str] = Column(Text)
    salary_per: Mapped[SalaryPer] = Column(Enum(SalaryPer))
    contact: Mapped[str] = Column(Text)
    last_update: Mapped[datetime] = Column(UTCDateTime)
    skill_requirements: list[SkillRequirement] = relationship(
        "SkillRequirement", back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def responsibilities(self) -> list[str]:
        return cast(list[str], json.loads(self._responsibilities)) if self._responsibilities else []

    @responsibilities.setter
    def responsibilities(self, value: list[str]) -> None:
        self._responsibilities = json.dumps(value)

    def serialize(self, *, include_contact: bool) -> dict[str, Any]:
        return {
            "id": self.id,
            "company": self.company.serialize,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "remote": self.remote,
            "type": self.type,
            "responsibilities": self.responsibilities,
            "professional_level": self.professional_level,
            "salary": {
                "min": self.salary_min,
                "max": self.salary_max,
                "unit": self.salary_unit,
                "per": self.salary_per,
            },
            "contact": self.contact if include_contact else None,
            "last_update": self.last_update.timestamp(),
            "skill_requirements": {req.skill_id for req in self.skill_requirements},
        }

    @classmethod
    async def create(
        cls,
        *,
        company_id: str,
        title: str,
        description: str,
        location: str,
        remote: bool,
        type: JobType,
        responsibilities: list[str],
        professional_level: ProfessionalLevel,
        salary_min: int,
        salary_max: int,
        salary_unit: str,
        salary_per: SalaryPer,
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
            professional_level=professional_level,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_unit=salary_unit,
            salary_per=salary_per,
            contact=contact,
            skill_requirements=[SkillRequirement(job_id=job_id, skill_id=skill_id) for skill_id in skill_requirements],
            last_update=utcnow(),
        )
        job.responsibilities = responsibilities
        await db.add(job)
        return job
