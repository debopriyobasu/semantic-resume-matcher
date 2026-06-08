from typing import Literal

from pydantic import BaseModel, Field


class MatchEvaluation(BaseModel):
    confidence: float
    match_category: Literal["WEAK_MATCH", "POTENTIAL_MATCH", "STRONG_MATCH"]
    reasoning: str
    skill_gaps: list[str] = Field(default_factory=list)
    standout_strengths: list[str] = Field(default_factory=list)
