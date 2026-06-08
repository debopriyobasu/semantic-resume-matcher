import uuid
from sqlalchemy.orm import Session

from src.repositories import search_repository
from src.models.match_result import MatchResult
from src.models.job_posting import JobPosting
from src.models.candidate import Candidate
from src.core.metrics import metrics_store


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def find_similar_jobs(self, candidate_id: uuid.UUID, limit: int = 10) -> list[dict]:
        """
        Find similar jobs for a candidate, apply deterministic filtering, and persist the match result.
        """
        candidate = self.db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if not candidate:
            return []

        # 1. Execute vector similarity search
        similar_jobs = search_repository.find_similar_jobs(self.db, candidate_id, limit)

        results = []
        # 2. Apply deterministic filtering before persistence
        for job, score in similar_jobs:
            category = "PENDING"
            reason = ""

            if candidate.visa_required and not job.visa_sponsorship:
                category = "REJECTED"
                reason = "VISA_MISMATCH"
            elif candidate.desired_salary is not None and (job.max_salary is None or job.max_salary < candidate.desired_salary):
                category = "REJECTED"
                reason = "SALARY_MISMATCH"
            elif candidate.preferred_location is not None and job.location != candidate.preferred_location:
                category = "REJECTED"
                reason = "LOCATION_MISMATCH"
            elif candidate.preferred_remote and not job.remote_ok:
                category = "REJECTED"
                reason = "REMOTE_MISMATCH"

            if category == "REJECTED":
                metrics_store.increment_match_category("REJECTED")

            # Create a MatchResult with placeholder values for future milestones
            match_result = MatchResult(
                candidate_id=candidate_id,
                job_id=job.job_id,
                vector_score=score,
                confidence=None,
                match_category=category,
                reasoning=reason if reason else None,
                skill_gaps=[],
                standout_strengths=[]
            )
            self.db.add(match_result)
            
            results.append({
                "job": job,
                "score": score,
                "category": category,
                "reasoning": reason
            })
            
        self.db.commit()
        return results
