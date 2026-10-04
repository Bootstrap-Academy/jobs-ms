from api.schemas.user import User
from api.services.internal import InternalService
from api.utils.cache import redis_cached


@redis_cached("user", "user_id")
async def exists_user(user_id: str) -> bool:
    async with InternalService.AUTH.client as client:
        response = await client.get(f"/users/{user_id}")
        return response.status_code == 200


async def ordinary_authority(access_token: str, expected_user_id: str) -> User | None:
    """Uncached authority check; internal identity/existence keeps its own semantics.

    A request authorized before a restriction commits may finish. New requests
    require a currently enabled account and the durable matching backend session.
    """
    from fastapi import HTTPException
    from httpx import HTTPError
    from pydantic import ValidationError

    try:
        async with InternalService.AUTH.client as client:
            # A 401 here describes the forwarded ordinary token, not our
            # internal transport credential. Do not use the generic error hook.
            client.event_hooks["response"] = []
            response = await client.post("/ordinary-authority", json={"access_token": access_token})
        if response.status_code in (401, 403):
            return None
        if response.status_code != 200:
            raise HTTPException(503, "Account authority temporarily unavailable")
        payload = response.json()
        user = User.parse_obj({key: payload[key] for key in ("id", "email_verified", "admin")})
        if user.id != expected_user_id:
            raise HTTPException(503, "Invalid authority response")
        return user
    except (HTTPError, ValidationError, ValueError, KeyError, TypeError) as exc:
        from api.logger import get_logger

        get_logger(__name__).warning("Ordinary authority response unavailable (%s)", type(exc).__name__)
        raise HTTPException(503, "Account authority temporarily unavailable") from None
