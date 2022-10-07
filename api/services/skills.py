from typing import cast

from api.services.internal import InternalService


async def get_skills() -> set[str]:
    async with InternalService.SKILLS.client as client:
        response = await client.get("/skills")
        return {cast(str, skill["id"]) for skill in response.json()}


async def get_completed_skills(user_id: str) -> set[str]:
    async with InternalService.SKILLS.client as client:
        response = await client.get(f"/skills/{user_id}")
        return set(response.json())
