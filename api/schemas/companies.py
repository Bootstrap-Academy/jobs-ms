from pydantic import BaseModel, Field


class Company(BaseModel):
    id: str = Field(description="The unique identifier of the company")
    name: str = Field(description="The name of the company")
    description: str | None = Field(description="The description of the company")
    website: str | None = Field(description="The website of the company")
    youtube_video: str | None = Field(description="A link to a YouTube video of the company")
    twitter_handle: str | None = Field(description="The Twitter handle of the company")
    instagram_handle: str | None = Field(description="The Instagram handle of the company")
    logo_url: str | None = Field(description="The logo of the company")


class CreateCompany(BaseModel):
    name: str = Field(max_length=255, description="The name of the company")
    description: str | None = Field(max_length=255, description="The description of the company")
    website: str | None = Field(max_length=255, description="The website of the company")
    youtube_video: str | None = Field(max_length=255, description="A link to a YouTube video of the company")
    twitter_handle: str | None = Field(max_length=255, description="The Twitter handle of the company")
    instagram_handle: str | None = Field(max_length=255, description="The Instagram handle of the company")
    logo_url: str | None = Field(max_length=255, description="The logo of the company")


class UpdateCompany(BaseModel):
    name: str | None = Field(max_length=255, description="The name of the company")
    description: str | None = Field(max_length=255, description="The description of the company")
    website: str | None = Field(max_length=255, description="The website of the company")
    youtube_video: str | None = Field(max_length=255, description="A link to a YouTube video of the company")
    twitter_handle: str | None = Field(max_length=255, description="The Twitter handle of the company")
    instagram_handle: str | None = Field(max_length=255, description="The Instagram handle of the company")
    logo_url: str | None = Field(max_length=255, description="The logo of the company")
