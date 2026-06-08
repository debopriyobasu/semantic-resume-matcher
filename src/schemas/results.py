import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CandidateStatusResponse(BaseModel):
    candidate_id: uuid.UUID
    pipeline_status: str


class MatchJobResponse(BaseModel):
    job_id: uuid.UUID
    title: str
    company: str
    location: Optional[str] = None
    remote_ok: bool
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class MatchResultItem(BaseModel):
    match_id: uuid.UUID
    job: MatchJobResponse
    vector_score: float
    confidence: Optional[float] = None
    match_category: str
    reasoning: Optional[str] = None
    skill_gaps: List[str]
    standout_strengths: List[str]

    model_config = ConfigDict(from_attributes=True)


class MatchResultsResponse(BaseModel):
    candidate_id: uuid.UUID
    matches: List[MatchResultItem]
