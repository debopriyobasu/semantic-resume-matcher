from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    education: str | None = None
    location: str | None = None
