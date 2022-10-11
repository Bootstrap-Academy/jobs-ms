"""Endpoints related to jobs."""

from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, or_

from api import models
from api.auth import admin_auth, public_auth
from api.database import db, select
from api.exceptions.auth import admin_responses
from api.exceptions.companies import CompanyNotFoundError
from api.exceptions.jobs import JobNotFoundError, SkillNotFoundError
from api.models.jobs import JobType
from api.schemas.jobs import CreateJob, Job, UpdateJob
from api.schemas.user import User
from api.services.skills import get_completed_skills, get_skills
from api.utils.docs import responses


router = APIRouter()


@router.get("/jobs", responses=responses(list[Job]))
async def list_all_jobs(
    search_term: str | None = Query(None, description="A search term to filter jobs by"),
    location: str | None = Query(None, description="The location to search for"),
    remote: bool = Query(False, description="Whether to search for remote jobs"),
    type: JobType | None = Query(None, description="The type of job to search for"),
    user: User | None = public_auth,
) -> Any:
    """
    Return a list of all jobs.

    Contact details are included iff the **VERIFIED** requirement is met and the user has completed the required skills.
    """

    completed: set[str] = set()
    if user and user.email_verified and not user.admin:
        completed = await get_completed_skills(user.id)

    query = select(models.Job)
    if search_term:
        query = query.where(
            or_(
                func.lower(models.Job.title).contains(search_term.lower(), autoescape=True),
                func.lower(models.Job.description).contains(search_term.lower(), autoescape=True),
            )
        )
    if location:
        query = query.where(func.lower(models.Job.location).contains(location.lower(), autoescape=True))
    if remote:
        query = query.filter_by(remote=True)
    if type:
        query = query.filter_by(type=type)

    return [
        job.serialize(
            include_contact=(user and user.admin)
            or completed < {requirement.skill_id for requirement in job.skill_requirements}
        )
        async for job in await db.stream(query)
    ]


@router.post(
    "/jobs", dependencies=[admin_auth], responses=admin_responses(Job, CompanyNotFoundError, SkillNotFoundError)
)
async def create_job(data: CreateJob) -> Any:
    """
    Create a new job.

    *Requirements:* **ADMIN**
    """

    company = await db.get(models.Company, id=data.company_id)
    if not company:
        raise CompanyNotFoundError

    if not data.skill_requirements < await get_skills():
        raise SkillNotFoundError

    job = await models.Job.create(
        data.company_id,
        data.title,
        data.description,
        data.location,
        data.remote,
        data.type,
        data.contact,
        data.skill_requirements,
    )
    job.company = company
    return job.serialize(include_contact=True)


@router.patch(
    "/jobs/{job_id}",
    dependencies=[admin_auth],
    responses=admin_responses(Job, JobNotFoundError, CompanyNotFoundError, SkillNotFoundError),
)
async def update_job(job_id: str, data: UpdateJob) -> Any:
    """
    Update an existing job.

    *Requirements:* **ADMIN**
    """

    job = await db.get(models.Job, id=job_id)
    if not job:
        raise JobNotFoundError

    if data.company_id is not None and data.company_id != job.company_id:
        company = await db.get(models.Company, id=data.company_id)
        if not company:
            raise CompanyNotFoundError
        job.company_id = data.company_id

    if data.title is not None and data.title != job.title:
        job.title = data.title

    if data.description is not None and data.description != job.description:
        job.description = data.description

    if data.location is not None and data.location != job.location:
        job.location = data.location

    if data.remote is not None and data.remote != job.remote:
        job.remote = data.remote

    if data.type is not None and data.type != job.type:
        job.type = data.type

    if data.contact is not None and data.contact != job.contact:
        job.contact = data.contact

    requirement_ids = {requirement.skill_id for requirement in job.skill_requirements}
    if data.skill_requirements is not None and data.skill_requirements != requirement_ids:
        if not data.skill_requirements < await get_skills():
            raise SkillNotFoundError
        job.skill_requirements = [
            models.SkillRequirement(job_id=job.id, skill_id=skill_id) for skill_id in data.skill_requirements
        ]

    return job.serialize(include_contact=True)


@router.delete("/jobs/{job_id}", dependencies=[admin_auth], responses=admin_responses(bool, JobNotFoundError))
async def delete_job(job_id: str) -> Any:
    """
    Delete an existing job.

    *Requirements:* **ADMIN**
    """

    job = await db.get(models.Job, id=job_id)
    if not job:
        raise JobNotFoundError

    await db.delete(job)
    return True
