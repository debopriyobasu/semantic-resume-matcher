import uuid

from sqlalchemy.orm import Session

from src.models.match_result import MatchResult


def get_pending_matches(db: Session, candidate_id: uuid.UUID) -> list[MatchResult]:
    return (
        db.query(MatchResult)
        .filter(MatchResult.candidate_id == candidate_id, MatchResult.match_category == "PENDING")
        .all()
    )


def update_match_result(db: Session, match_id: uuid.UUID, evaluation_data: dict) -> None:
    db.query(MatchResult).filter(MatchResult.match_id == match_id).update(evaluation_data)
    db.commit()
