from pydantic import BaseModel, Extra

from api.services.internal import InternalService
from api.utils.cache import redis_cached


class Skill(BaseModel):
    id: str
    parent_id: str

    class Config:
        extra = Extra.ignore


@redis_cached("skills")
async def get_skills() -> dict[str, Skill]:
    async with InternalService.SKILLS.client as client:
        response = await client.get("/skills")
        return {skill.id: skill for skill in map(Skill.parse_obj, response.json())}


@redis_cached("user_skills", "user_id")
async def get_completed_skills(user_id: str) -> set[str]:
    async with InternalService.SKILLS.client as client:
        response = await client.get(f"/skills/{user_id}")
        return set(response.json())
