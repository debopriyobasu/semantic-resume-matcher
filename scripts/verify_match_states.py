import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.models.match_result import MatchResult


def run():
    engine = create_engine(
        "postgresql+psycopg://resume_matcher:resume_matcher@localhost:5432/resume_matcher"
    )
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Get a candidate and job to use for the demo
    candidate = db.query(Candidate).first()
    job = db.query(JobPosting).first()

    if not candidate or not job:
        print("Need at least one candidate and one job in the database.")
        return

    # 1. Clean up old test data for this specific demo candidate to keep output clean
    db.query(MatchResult).filter(MatchResult.candidate_id == candidate.candidate_id).delete()

    # Create states
    pending = MatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        vector_score=0.85,
        confidence=None,
        match_category="PENDING",
        reasoning=None,
    )

    rejected = MatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        vector_score=0.82,
        confidence=None,
        match_category="REJECTED",
        reasoning="SALARY_MISMATCH",
    )

    strong_match = MatchResult(
        candidate_id=candidate.candidate_id,
        job_id=job.job_id,
        vector_score=0.88,
        confidence=0.95,
        match_category="STRONG_MATCH",
        reasoning="Excellent fit for backend technologies and years of experience.",
    )

    db.add_all([pending, rejected, strong_match])
    db.commit()

    # Verify by reading back
    results = db.query(MatchResult).filter(MatchResult.candidate_id == candidate.candidate_id).all()

    print("Verification of MatchResult states in Database:\n")
    for r in results:
        print(f"[{r.match_category}]")
        print(f" - confidence: {r.confidence}")
        print(f" - reasoning: {r.reasoning}")
        print()


if __name__ == "__main__":
    run()
