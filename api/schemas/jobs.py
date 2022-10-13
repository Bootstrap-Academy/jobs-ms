from typing import Any, cast

from pydantic import BaseModel, Field, validator

from api.models import JobType
from api.models.jobs import ProfessionalLevel, SalaryPer
from api.schemas.companies import Company


class JobSalary(BaseModel):
    min: int = Field(ge=0, lt=1 << 31, description="Minimum salary")
    max: int = Field(ge=0, lt=1 << 31, description="Maximum salary")
    unit: str = Field(description="Currency unit")
    per: SalaryPer = Field(description="Period of time")

    @validator("max")
    def max_must_be_greater_than_min(cls, v: int, values: dict[str, Any]) -> int:  # noqa: N805
        if v < cast(int, values["min"]):
            raise ValueError("max must be greater than min")
        return v


class Job(BaseModel):
    id: str = Field(description="The job's unique identifier")
    company: Company = Field(description="The company that posted the job")
    title: str = Field(description="The job's title")
    description: str = Field(description="The job's description")
    location: str = Field(description="The job's location")
    remote: bool = Field(description="Whether the job is remote")
    type: JobType = Field(description="The job's type")
    responsibilities: list[str] = Field(description="The job's responsibilities")
    professional_level: ProfessionalLevel = Field(description="The job's professional level")
    salary: JobSalary = Field(description="The job's salary")
    contact: str | None = Field(description="The job's contact information")
    last_update: int = Field(description="The job's last update timestamp")
    skill_requirements: set[str] = Field(description="The job's skill requirements")


class CreateJob(BaseModel):
    company_id: str = Field(description="The company's unique identifier")
    title: str = Field(max_length=255, description="The job's title")
    description: str = Field(max_length=2000, description="The job's description")
    location: str = Field(max_length=255, description="The job's location")
    remote: bool = Field(description="Whether the job is remote")
    type: JobType = Field(description="The job's type")
    responsibilities: list[str] = Field(max_items=16, max_length=512, description="The job's responsibilities")
    professional_level: ProfessionalLevel = Field(description="The job's professional level")
    salary: JobSalary = Field(description="The job's salary")
    contact: str = Field(max_length=255, description="The job's contact information")
    skill_requirements: set[str] = Field(description="The job's skill requirements")


class UpdateJob(BaseModel):
    company_id: str | None = Field(description="The company's unique identifier")
    title: str | None = Field(max_length=255, description="The job's title")
    description: str | None = Field(max_length=2000, description="The job's description")
    location: str | None = Field(max_length=255, description="The job's location")
    remote: bool | None = Field(description="Whether the job is remote")
    type: JobType | None = Field(description="The job's type")
    responsibilities: list[str] | None = Field(max_items=16, max_length=512, description="The job's responsibilities")
    professional_level: ProfessionalLevel | None = Field(description="The job's professional level")
    salary: JobSalary | None = Field(description="The job's salary")
    contact: str | None = Field(max_length=255, description="The job's contact information")
    skill_requirements: set[str] | None = Field(description="The job's skill requirements")
