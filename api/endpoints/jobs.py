"""Endpoints related to the job platform."""
from typing import Any

from fastapi import APIRouter

from api.utils.docs import responses


router = APIRouter()


@router.get("/test", responses=responses(str))
async def test() -> Any:
    return "test"
