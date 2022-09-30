from __future__ import annotations

import enum
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship

from api.database import Base, db
from api.models.companies import Company


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
    # todo: required skills

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
        }

    @classmethod
    async def create(
        cls, company_id: str, title: str, description: str, location: str, remote: bool, type: JobType, contact: str
    ) -> Job:
        job = cls(
            id=str(uuid4()),
            company_id=company_id,
            title=title,
            description=description,
            location=location,
            remote=remote,
            type=type,
            contact=contact,
        )
        await db.add(job)
        return job
