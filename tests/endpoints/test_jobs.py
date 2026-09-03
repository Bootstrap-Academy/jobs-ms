from typing import Any, AsyncIterator
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from api import models
from api.endpoints.jobs import _include_contact, get_job, list_all_jobs
from api.models.jobs import JobType, ProfessionalLevel, SalaryPer
from api.schemas.user import User
from api.services.skills import Skill
from api.utils.utc import utcnow


CONTACT = "https://www.example.com/in/some-person/"

ANONYMOUS = None
UNVERIFIED = User(id="user42", email_verified=False, admin=False)
VERIFIED = User(id="user42", email_verified=True, admin=False)
ADMIN = User(id="admin42", email_verified=False, admin=True)


def make_job(**skill_requirements: int) -> models.Job:
    job = models.Job(
        id="job42",
        company_id="company42",
        title="Job",
        description="Description",
        location="Munich",
        remote=True,
        type=JobType.FULL_TIME,
        professional_level=ProfessionalLevel.ENTRY,
        salary_min=1,
        salary_max=2,
        salary_unit="€",
        salary_per=SalaryPer.MONTH,
        contact=CONTACT,
        last_update=utcnow(),
        skill_requirements=[
            models.SkillRequirement(job_id="job42", skill_id=skill_id, level=level)
            for skill_id, level in skill_requirements.items()
        ],
    )
    job.responsibilities = []
    job.company = models.Company(id="company42", name="Company")
    return job


@pytest.fixture(autouse=True)
def skills(mocker: MockerFixture) -> None:
    mocker.patch(
        "api.models.jobs.get_skills", AsyncMock(return_value={"skill42": Skill(id="skill42", parent_id="parent42")})
    )


def mock_job(mocker: MockerFixture, job: models.Job, **levels: int) -> None:
    async def stream(_: Any) -> AsyncIterator[models.Job]:
        yield job

    mocker.patch("api.endpoints.jobs.get_skill_levels", AsyncMock(return_value=levels))
    mocker.patch("api.endpoints.jobs.db.get", AsyncMock(return_value=job))
    mocker.patch("api.endpoints.jobs.db.stream", AsyncMock(side_effect=stream))


async def call_list_all_jobs(user: User | None) -> Any:
    return await list_all_jobs(
        search_term=None,
        location=None,
        remote=None,
        type=None,
        professional_level=None,
        salary_min=None,
        salary_max=None,
        salary_unit=None,
        salary_per=None,
        requirements_met=None,
        user=user,
    )


@pytest.mark.parametrize(
    "user,requirements_met,expected",
    [
        (ANONYMOUS, True, False),
        (ANONYMOUS, False, False),
        (UNVERIFIED, True, False),
        (UNVERIFIED, False, False),
        (VERIFIED, True, True),
        (VERIFIED, False, False),
        (ADMIN, True, True),
        (ADMIN, False, True),
    ],
)
def test___include_contact(user: User | None, requirements_met: bool, expected: bool) -> None:
    assert _include_contact(user, requirements_met) is expected


@pytest.mark.parametrize(
    "user,expected", [(ANONYMOUS, None), (UNVERIFIED, None), (VERIFIED, CONTACT), (ADMIN, CONTACT)]
)
async def test__list_all_jobs__job_without_skill_requirements(
    mocker: MockerFixture, user: User | None, expected: str | None
) -> None:
    mock_job(mocker, make_job())

    [result] = await call_list_all_jobs(user)

    assert result["skill_requirements"] == set()
    assert result["contact"] == expected


@pytest.mark.parametrize(
    "user,expected", [(ANONYMOUS, None), (UNVERIFIED, None), (VERIFIED, CONTACT), (ADMIN, CONTACT)]
)
async def test__get_job__job_without_skill_requirements(
    mocker: MockerFixture, user: User | None, expected: str | None
) -> None:
    mock_job(mocker, make_job())

    result = await get_job("job42", user)

    assert result["skill_requirements"] == set()
    assert result["contact"] == expected


@pytest.mark.parametrize("level,expected", [(0, None), (1, None), (2, CONTACT), (3, CONTACT)])
async def test__get_job__job_with_skill_requirements(mocker: MockerFixture, level: int, expected: str | None) -> None:
    mock_job(mocker, make_job(skill42=2), skill42=level)

    result = await get_job("job42", VERIFIED)

    assert result["contact"] == expected


async def test__get_job__admins_see_the_contact_of_jobs_they_do_not_qualify_for(mocker: MockerFixture) -> None:
    mock_job(mocker, make_job(skill42=2), skill42=0)

    result = await get_job("job42", ADMIN)

    assert result["contact"] == CONTACT
