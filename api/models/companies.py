from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from api.database import Base, db


class Company(Base):
    __tablename__ = "jobs_companies"

    id: Mapped[str] = Column(String(36), primary_key=True, unique=True)
    name: Mapped[str] = Column(String(255), unique=True)
    description: Mapped[str | None] = Column(String(255), nullable=True)
    website: Mapped[str | None] = Column(String(255), nullable=True)
    youtube_video: Mapped[str | None] = Column(String(255), nullable=True)
    twitter_handle: Mapped[str | None] = Column(String(255), nullable=True)
    instagram_handle: Mapped[str | None] = Column(String(255), nullable=True)
    logo_url: Mapped[str | None] = Column(String(255), nullable=True)

    @property
    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "website": self.website,
            "youtube_video": self.youtube_video,
            "twitter_handle": self.twitter_handle,
            "instagram_handle": self.instagram_handle,
            "logo_url": self.logo_url,
        }

    @classmethod
    async def create(
        cls,
        name: str,
        description: str | None,
        website: str | None,
        youtube_video: str | None,
        twitter_handle: str | None,
        instagram_handle: str | None,
        logo_url: str | None,
    ) -> Company:
        company = cls(
            id=str(uuid4()),
            name=name,
            description=description,
            website=website,
            youtube_video=youtube_video,
            twitter_handle=twitter_handle,
            instagram_handle=instagram_handle,
            logo_url=logo_url,
        )
        await db.add(company)
        return company
