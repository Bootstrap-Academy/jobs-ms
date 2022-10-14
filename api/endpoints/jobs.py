"""Endpoints related to jobs."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, or_

from api import models
from api.auth import admin_auth, public_auth
from api.database import db, select
from api.exceptions.auth import admin_responses
from api.exceptions.companies import CompanyNotFoundError
from api.exceptions.jobs import JobNotFoundError, SkillNotFoundError
from api.models.jobs import JobType, ProfessionalLevel, SalaryPer
from api.schemas.jobs import CreateJob, Job, UpdateJob
from api.schemas.user import User
from api.services.skills import get_completed_skills, get_skills
from api.utils.docs import responses


router = APIRouter()


@router.get("/jobs", responses=responses(list[Job]))
async def list_all_jobs(
    search_term: str | None = Query(None, description="A search term to filter jobs by"),
    location: str | None = Query(None, description="The location to search for"),
    remote: bool | None = Query(None, description="Whether to search for remote jobs"),
    type: list[JobType] | None = Query(None, description="The type of job to search for"),
    professional_level: list[ProfessionalLevel]
    | None = Query(None, description="The professional level to search for"),
    salary_min: int | None = Query(None, description="The minimum salary to search for"),
    salary_max: int | None = Query(None, description="The maximum salary to search for"),
    salary_unit: str | None = Query(None, description="The salary unit to search for"),
    salary_per: SalaryPer | None = Query(None, description="The salary period to search for"),
    requirements_met: bool | None = Query(None, description="Whether to search for jobs with skill requirements met"),
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
                func.lower(models.Job._responsibilities).contains(search_term.lower(), autoescape=True),
            )
        )
    if location:
        query = query.where(func.lower(models.Job.location).contains(location.lower(), autoescape=True))
    if remote is not None:
        query = query.where(models.Job.remote == remote)
    if type:
        query = query.where(models.Job.type.in_(type))
    if professional_level:
        query = query.where(models.Job.professional_level.in_(professional_level))
    if salary_min:
        query = query.where(models.Job.salary_min >= salary_min)
    if salary_max:
        query = query.where(models.Job.salary_max <= salary_max)
    if salary_unit:
        query = query.where(func.lower(models.Job.salary_unit).contains(salary_unit.lower(), autoescape=True))
    if salary_per:
        query = query.where(models.Job.salary_per == salary_per)

    return [
        job.serialize(include_contact=(user and user.admin) or ok)
        async for job in await db.stream(query)
        if (ok := completed < {requirement.skill_id for requirement in job.skill_requirements}) is requirements_met
        or requirements_met is None
    ]


@router.get("/jobs/{job_id}", responses=responses(Job, JobNotFoundError))
async def get_job(job_id: str, user: User | None = public_auth) -> Any:
    """
    Return details about a specific job.

    Contact details are included iff the **VERIFIED** requirement is met and the user has completed the required skills.
    """

    job = await db.get(models.Job, id=job_id)
    if not job:
        raise JobNotFoundError

    completed: set[str] = set()
    if user and user.email_verified and not user.admin:
        completed = await get_completed_skills(user.id)

    return job.serialize(
        include_contact=(user and user.admin)
        or completed < {requirement.skill_id for requirement in job.skill_requirements}
    )


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
        company_id=data.company_id,
        title=data.title,
        description=data.description,
        location=data.location,
        remote=data.remote,
        type=data.type,
        responsibilities=data.responsibilities,
        professional_level=data.professional_level,
        salary_min=data.salary.min,
        salary_max=data.salary.max,
        salary_unit=data.salary.unit,
        salary_per=data.salary.per,
        contact=data.contact,
        skill_requirements=data.skill_requirements,
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

    if data.responsibilities is not None and data.responsibilities != job.responsibilities:
        job.responsibilities = data.responsibilities

    if data.professional_level is not None and data.professional_level != job.professional_level:
        job.professional_level = data.professional_level

    if data.salary is not None:
        job.salary_min = data.salary.min
        job.salary_max = data.salary.max
        job.salary_unit = data.salary.unit
        job.salary_per = data.salary.per

    if data.contact is not None and data.contact != job.contact:
        job.contact = data.contact

    requirement_ids = {requirement.skill_id for requirement in job.skill_requirements}
    if data.skill_requirements is not None and data.skill_requirements != requirement_ids:
        if not data.skill_requirements < await get_skills():
            raise SkillNotFoundError
        job.skill_requirements = [
            models.SkillRequirement(job_id=job.id, skill_id=skill_id) for skill_id in data.skill_requirements
        ]

    job.last_update = datetime.now()

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
