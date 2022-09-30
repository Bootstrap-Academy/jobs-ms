"""Endpoints related to companies."""

from typing import Any

from fastapi import APIRouter

from api import models
from api.auth import admin_auth
from api.database import db, filter_by, select
from api.exceptions.auth import admin_responses
from api.exceptions.companies import CompanyAlreadyExistsError, CompanyNotFoundError
from api.schemas.companies import Company, CreateCompany, UpdateCompany


router = APIRouter()


@router.get("/companies", dependencies=[admin_auth], responses=admin_responses(list[Company]))
async def list_all_companies() -> Any:
    """
    List all companies.

    *Requirements:* **ADMIN**
    """

    return [company.serialize async for company in await db.stream(select(models.Company))]


@router.post("/companies", dependencies=[admin_auth], responses=admin_responses(Company, CompanyAlreadyExistsError))
async def create_company(data: CreateCompany) -> Any:
    """
    Create a company.

    *Requirements:* **ADMIN**
    """

    if await db.exists(filter_by(models.Company, name=data.name)):
        raise CompanyAlreadyExistsError

    company = await models.Company.create(
        data.name,
        data.description,
        data.website,
        data.youtube_video,
        data.twitter_handle,
        data.instagram_handle,
        data.logo_url,
    )
    return company.serialize


@router.patch(
    "/companies/{company_id}",
    dependencies=[admin_auth],
    responses=admin_responses(Company, CompanyNotFoundError, CompanyAlreadyExistsError),
)
async def update_company(company_id: str, data: UpdateCompany) -> Any:
    """
    Update a company.

    *Requirements:* **ADMIN**
    """

    company = await db.get(models.Company, id=company_id)
    if not company:
        raise CompanyNotFoundError

    if data.name is not None and data.name != company.name:
        if await db.exists(filter_by(models.Company, name=data.name)):
            raise CompanyAlreadyExistsError
        company.name = data.name

    if data.description is not None and data.description != company.description:
        company.description = data.description

    if data.website is not None and data.website != company.website:
        company.website = data.website

    if data.youtube_video is not None and data.youtube_video != company.youtube_video:
        company.youtube_video = data.youtube_video

    if data.twitter_handle is not None and data.twitter_handle != company.twitter_handle:
        company.twitter_handle = data.twitter_handle

    if data.instagram_handle is not None and data.instagram_handle != company.instagram_handle:
        company.instagram_handle = data.instagram_handle

    if data.logo_url is not None and data.logo_url != company.logo_url:
        company.logo_url = data.logo_url

    await db.add(company)
    return company.serialize


@router.delete(
    "/companies/{company_id}", dependencies=[admin_auth], responses=admin_responses(bool, CompanyNotFoundError)
)
async def delete_company(company_id: str) -> Any:
    """
    Delete a company.

    *Requirements:* **ADMIN**
    """

    company = await db.get(models.Company, id=company_id)
    if not company:
        raise CompanyNotFoundError

    await db.delete(company)
    return True
