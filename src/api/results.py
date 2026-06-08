import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.db.session import get_db
from src.models.candidate import Candidate
from src.models.match_result import MatchResult
from src.schemas.results import (
    CandidateStatusResponse,
    MatchResultItem,
    MatchResultsResponse,
)

router = APIRouter(prefix="/candidate", tags=["results"])


@router.get("/{candidate_id}", response_model=CandidateStatusResponse)
def get_candidate_status(candidate_id: uuid.UUID, db: Session = Depends(get_db)):
    candidate = db.scalar(select(Candidate).where(Candidate.candidate_id == candidate_id))
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    return CandidateStatusResponse(
        candidate_id=candidate.candidate_id, pipeline_status=candidate.pipeline_status
    )


@router.get("/{candidate_id}/matches", response_model=MatchResultsResponse)
def get_match_results(candidate_id: uuid.UUID, db: Session = Depends(get_db)):
    candidate = db.scalar(select(Candidate).where(Candidate.candidate_id == candidate_id))
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    matches = db.scalars(
        select(MatchResult)
        .options(joinedload(MatchResult.job))
        .where(MatchResult.candidate_id == candidate_id)
        .order_by(MatchResult.confidence.desc().nulls_last(), MatchResult.vector_score.desc())
    ).all()

    # Convert to Pydantic models explicitly to handle potential nested attributes if needed,
    # though from_attributes=True handles it directly when returning MatchResultsResponse
    match_items = []
    for m in matches:
        match_items.append(MatchResultItem.model_validate(m))

    return MatchResultsResponse(candidate_id=candidate_id, matches=match_items)
