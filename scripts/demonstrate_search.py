import sys
import os
import uuid
import logging

# Set up logging to show SQLAlchemy queries
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Ensure the root path is added to sys.path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from src.db.session import get_db
from src.services.search_service import SearchService
from src.models.match_result import MatchResult

def run():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('postgresql+psycopg://resume_matcher:resume_matcher@localhost:5432/resume_matcher')
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    candidate_id = uuid.UUID("b7061fcc-48f6-43cf-97ae-e3b97d466c6f")
    
    search_service = SearchService(db)
    
    print("Executing similarity search...\n")
    results = search_service.find_similar_jobs(candidate_id)
    
    print("\n---------------------------------------------------------")
    print(f"Top {len(results)} jobs for candidate {candidate_id}:")
    for idx, (job, score) in enumerate(results, 1):
        print(f"{idx}. Score: {score:.4f} | Job ID: {job.job_id} | Title: {job.title}")

    # Verify persistence
    match_results = db.scalars(select(MatchResult).where(MatchResult.candidate_id == candidate_id)).all()
    print(f"\nPersisted MatchResults for candidate {candidate_id}: {len(match_results)}")
    for mr in match_results:
        print(f" - MatchResult: Job={mr.job_id}, Score={mr.vector_score:.4f}")

if __name__ == "__main__":
    run()
