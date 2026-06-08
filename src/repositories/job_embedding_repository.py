import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.job_embedding import JobEmbedding


def create_job_embedding(db: Session, job_id: uuid.UUID, embedding: list[float]) -> JobEmbedding:
    """Create and persist a job embedding."""
    job_embedding = JobEmbedding(job_id=job_id, embedding=embedding)
    db.add(job_embedding)
    db.commit()
    db.refresh(job_embedding)
    return job_embedding


def get_job_embedding(db: Session, job_id: uuid.UUID) -> JobEmbedding | None:
    """Retrieve an embedding for a specific job."""
    return db.scalar(select(JobEmbedding).where(JobEmbedding.job_id == job_id))
