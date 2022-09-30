from pydantic import BaseModel, Field

from api.models import JobType
from api.schemas.companies import Company


class Job(BaseModel):
    id: str = Field(description="The job's unique identifier")
    company: Company = Field(description="The company that posted the job")
    title: str = Field(description="The job's title")
    description: str = Field(description="The job's description")
    location: str = Field(description="The job's location")
    remote: bool = Field(description="Whether the job is remote")
    type: JobType = Field(description="The job's type")
    contact: str | None = Field(description="The job's contact information")


class CreateJob(BaseModel):
    company_id: str = Field(description="The company's unique identifier")
    title: str = Field(max_length=255, description="The job's title")
    description: str = Field(max_length=2000, description="The job's description")
    location: str = Field(max_length=255, description="The job's location")
    remote: bool = Field(description="Whether the job is remote")
    type: JobType = Field(description="The job's type")
    contact: str = Field(max_length=255, description="The job's contact information")


class UpdateJob(BaseModel):
    company_id: str | None = Field(description="The company's unique identifier")
    title: str | None = Field(max_length=255, description="The job's title")
    description: str | None = Field(max_length=2000, description="The job's description")
    location: str | None = Field(max_length=255, description="The job's location")
    remote: bool | None = Field(description="Whether the job is remote")
    type: JobType | None = Field(description="The job's type")
    contact: str | None = Field(max_length=255, description="The job's contact information")
