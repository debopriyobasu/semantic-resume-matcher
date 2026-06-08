import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.candidate_embedding import CandidateEmbedding


def create_candidate_embedding(
    db: Session, candidate_id: uuid.UUID, embedding: list[float]
) -> CandidateEmbedding:
    """Persist a candidate embedding in the database."""
    candidate_embedding = CandidateEmbedding(
        candidate_id=candidate_id,
        embedding=embedding,
    )
    db.add(candidate_embedding)
    db.commit()
    db.refresh(candidate_embedding)
    return candidate_embedding


def get_candidate_embedding(db: Session, candidate_id: uuid.UUID) -> CandidateEmbedding | None:
    """Retrieve a candidate embedding from the database."""
    statement = select(CandidateEmbedding).where(CandidateEmbedding.candidate_id == candidate_id)
    return db.scalar(statement)
