import logging
import time
from typing import TYPE_CHECKING

import httpx

from src.core.config import get_settings
from src.core.metrics import metrics_store
from src.models.candidate import Candidate
from src.models.job_posting import JobPosting

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Exception raised for errors in the embedding service."""

    pass


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding for the given text using Ollama, normalized to exactly 768 dimensions."""
        start_time = time.perf_counter()
        try:
            response = httpx.post(
                f"{self.settings.ollama_base_url}/api/embeddings",
                json={
                    "model": self.settings.ollama_embed_model,
                    "prompt": text,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            response_json = response.json()
            embedding = response_json["embedding"]
            # Validate/safe-pad/truncate to exactly 768 dimensions for pgvector compatibility
            if len(embedding) > 768:
                embedding = embedding[:768]
            elif len(embedding) < 768:
                embedding = embedding + [0.0] * (768 - len(embedding))
            duration = time.perf_counter() - start_time
            metrics_store.record_embedding_duration(duration)
            return embedding
        except Exception as e:
            logger.error("Failed to generate embedding: %s", e)
            raise EmbeddingError(f"Embedding failure: {e}") from e

    def build_candidate_text(self, candidate: Candidate) -> str:
        """Build embedding text representation for a candidate."""
        parts = []
        if candidate.skills:
            parts.append("Skills:\n" + "\n".join(candidate.skills))
        if candidate.experience_years is not None:
            parts.append(
                f"Experience:\n{candidate.experience_years} years backend engineering"
            )  # Note: The prompt example had "5 years backend engineering", maybe it just means "years" but let's just use "years" or what's given.
        if candidate.education:
            parts.append(f"Education:\n{candidate.education}")
        if candidate.location:
            parts.append(f"Location:\n{candidate.location}")
        return "\n\n".join(parts)

    def generate_candidate_embedding(self, candidate: Candidate) -> list[float]:
        """Generate an embedding for a candidate."""
        text = self.build_candidate_text(candidate)
        return self.generate_embedding(text)

    def build_job_text(self, job: JobPosting) -> str:
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

    def generate_job_embedding(self, db: "Session", job: JobPosting) -> list[float]:
        """Generate and save embedding for a job."""
        from src.repositories.job_embedding_repository import create_job_embedding

        text = self.build_job_text(job)
        embedding = self.generate_embedding(text)
        create_job_embedding(db, job.job_id, embedding)
        return embedding


def process_job_embeddings() -> None:
    """Background task to generate embeddings for any jobs that lack them."""
    import logging

    from sqlalchemy import select

    from src.db.session import SessionLocal
    from src.models.job_embedding import JobEmbedding
    from src.models.job_posting import JobPosting

    logger = logging.getLogger(__name__)
    db = SessionLocal()
    embedding_service = EmbeddingService()

    try:
        stmt = select(JobPosting).outerjoin(JobEmbedding).where(JobEmbedding.embedding_id.is_(None))
        jobs_to_embed = db.scalars(stmt).all()

        logger.info(
            "Found %d jobs without embeddings to process in the background.", len(jobs_to_embed)
        )

        for job in jobs_to_embed:
            logger.info("Embedding job: %s", job.job_id)
            try:
                # Double-check if embedding was generated in a concurrent run
                existing_emb = db.scalar(
                    select(JobEmbedding).where(JobEmbedding.job_id == job.job_id)
                )
                if not existing_emb:
                    embedding_service.generate_job_embedding(db, job)
                    logger.info("Successfully embedded job: %s", job.job_id)
            except Exception as e:
                logger.error("Failed to embed job %s: %s", job.job_id, e)
                db.rollback()
    finally:
        db.close()
