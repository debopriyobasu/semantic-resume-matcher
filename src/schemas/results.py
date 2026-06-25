import uuid

from pydantic import BaseModel, ConfigDict


class CandidateStatusResponse(BaseModel):
    candidate_id: uuid.UUID
    pipeline_status: str
    status: str


class MatchJobResponse(BaseModel):
    job_id: uuid.UUID
    title: str
    company: str
    location: str | None = None
    remote_ok: bool
    min_salary: int | None = None
    max_salary: int | None = None

    model_config = ConfigDict(from_attributes=True)


class MatchResultItem(BaseModel):
    match_id: uuid.UUID
    job: MatchJobResponse
    vector_score: float
    confidence: float | None = None
    match_category: str
    reasoning: str | None = None
    skill_gaps: list[str]
    standout_strengths: list[str]

    model_config = ConfigDict(from_attributes=True)


class MatchResultsResponse(BaseModel):
    candidate_id: uuid.UUID
    matches: list[MatchResultItem]
