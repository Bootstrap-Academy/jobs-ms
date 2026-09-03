import secrets
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    root_path: str = ""

    debug: bool = False
    reload: bool = False

    cache_ttl: int = 300

    jwt_secret: str = secrets.token_urlsafe(64)

    # Secrets for the internal service tokens, one per audience. An empty value
    # falls back to `jwt_secret`, so a deployment which has not rolled out the
    # per-audience secrets yet keeps working.
    internal_jwt_secret_auth: str = ""
    internal_jwt_secret_skills: str = ""
    internal_jwt_secret_jobs: str = ""

    auth_url: str = ""
    skills_url: str = ""

    internal_jwt_ttl: int = 10

    database_url: str = Field(
        "mysql+aiomysql://fastapi:fastapi@mariadb:3306/fastapi",
        regex=r"^(mysql\+aiomysql|postgresql\+asyncpg|sqlite\+aiosqlite)://.*$",
    )
    pool_recycle: int = 300
    pool_size: int = 20
    max_overflow: int = 20
    sql_show_statements: bool = False

    redis_url: str = Field("redis://redis:6379/3", regex=r"^redis://.*$")
    auth_redis_url: str = Field("redis://redis:6379/0", regex=r"^redis://.*$")

    sentry_dsn: str | None = None
    sentry_environment: str = "test"

    def internal_jwt_secret(self, audience: str) -> str:
        """Return the secret with which internal tokens for `audience` are signed and verified."""

        secrets_by_audience = {
            "auth": self.internal_jwt_secret_auth,
            "skills": self.internal_jwt_secret_skills,
            "jobs": self.internal_jwt_secret_jobs,
        }
        return secrets_by_audience.get(audience, "") or self.jwt_secret


settings = Settings()  # type: ignore
