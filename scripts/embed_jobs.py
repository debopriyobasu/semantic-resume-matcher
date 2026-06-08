import logging
import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.session import SessionLocal
from src.models.job_embedding import JobEmbedding
from src.models.job_posting import JobPosting
from src.repositories.job_embedding_repository import create_job_embedding
from src.services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_job_text(job: JobPosting) -> str:
    """Build a text representation of the job posting for embedding."""
    parts = [
        f"Title: {job.title}",
        f"Company: {job.company}",
        f"Location: {job.location or 'Not specified'}",
        f"Remote: {'Yes' if job.remote_ok else 'No'}",
        f"Visa Sponsorship: {'Yes' if job.visa_sponsorship else 'No'}",
    ]
    if job.min_salary and job.max_salary:
        parts.append(f"Salary Range: ${job.min_salary} - ${job.max_salary}")

    if job.required_skills:
        parts.append(f"Skills: {', '.join(job.required_skills)}")

    parts.append(f"Description: {job.description}")

    return "\n".join(parts)


def main() -> None:
    db: Session = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        # Get jobs without embeddings
        stmt = select(JobPosting).outerjoin(JobEmbedding).where(JobEmbedding.embedding_id.is_(None))
        jobs_to_embed = db.scalars(stmt).all()

        logger.info("Found %d jobs without embeddings.", len(jobs_to_embed))

        for job in jobs_to_embed:
            logger.info("Embedding job: %s", job.job_id)
            text = build_job_text(job)
            try:
                embedding = embedding_service.generate_embedding(text)
                create_job_embedding(db, job.job_id, embedding)
                logger.info("Successfully embedded job: %s", job.job_id)
            except Exception as e:
                logger.error("Failed to embed job %s: %s", job.job_id, e)

    finally:
        db.close()


if __name__ == "__main__":
    main()
