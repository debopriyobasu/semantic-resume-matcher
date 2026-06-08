import uuid
from sqlalchemy.orm import Session

from src.repositories import search_repository
from src.models.match_result import MatchResult
from src.models.job_posting import JobPosting


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def find_similar_jobs(self, candidate_id: uuid.UUID, limit: int = 10) -> list[tuple[JobPosting, float]]:
        """
        Find similar jobs for a candidate and persist the vector score.
        """
        # 1. Execute vector similarity search
        similar_jobs = search_repository.find_similar_jobs(self.db, candidate_id, limit)

        # 2. Persist similarity score (capture vector_score)
        for job, score in similar_jobs:
            # Create a MatchResult with placeholder values for future milestones
            match_result = MatchResult(
                candidate_id=candidate_id,
                job_id=job.job_id,
                vector_score=score,
                confidence=0.0,
                match_category="PENDING",
                reasoning="",
                skill_gaps=[],
                standout_strengths=[]
            )
            self.db.add(match_result)
            
        self.db.commit()
        return similar_jobs
