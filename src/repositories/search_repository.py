import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.candidate_embedding import CandidateEmbedding
from src.models.job_embedding import JobEmbedding
from src.models.job_posting import JobPosting


def find_similar_jobs(
    db: Session, candidate_id: uuid.UUID, limit: int = 10
) -> list[tuple[JobPosting, float]]:
    """Retrieve similar jobs for a given candidate using pgvector cosine distance."""
    candidate_emb = db.scalar(
        select(CandidateEmbedding).where(CandidateEmbedding.candidate_id == candidate_id)
    )
    if not candidate_emb:
        return []

    # pgvector provides cosine_distance, similarity is 1 - distance
    distance_col = JobEmbedding.embedding.cosine_distance(candidate_emb.embedding).label("distance")

    query = (
        select(JobPosting, distance_col)
        .join(JobEmbedding, JobPosting.job_id == JobEmbedding.job_id)
        .order_by(distance_col)
        .limit(limit)
    )

    results = db.execute(query).all()
    # Returns (JobPosting, vector_score)
    return [(row.JobPosting, 1.0 - float(row.distance)) for row in results]
