import sys
import os
import uuid
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from src.db.session import get_db
from src.services.search_service import SearchService
from src.repositories.search_repository import find_similar_jobs as repo_find_similar_jobs
from src.models.candidate import Candidate
from src.models.match_result import MatchResult

def run():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('postgresql+psycopg://resume_matcher:resume_matcher@localhost:5432/resume_matcher')
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    candidate_id = uuid.UUID("b7061fcc-48f6-43cf-97ae-e3b97d466c6f")
    
    # Update candidate with some constraints to trigger filtering
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    candidate.visa_required = False
    candidate.desired_salary = 100000
    candidate.preferred_remote = False
    candidate.preferred_location = None
    
    # Clear previous MatchResults for this candidate so persistence verify is clean
    db.query(MatchResult).filter(MatchResult.candidate_id == candidate_id).delete()
    db.commit()

    print("=========================================================")
    print("Candidate Preferences Loaded:")
    print(f" - Visa Required: {candidate.visa_required}")
    print(f" - Desired Salary: {candidate.desired_salary}")
    print(f" - Preferred Remote: {candidate.preferred_remote}")
    print(f" - Preferred Location: {candidate.preferred_location}")
    print("=========================================================\n")

    print("Executing Vector Search (Before Filtering)...")
    raw_results = repo_find_similar_jobs(db, candidate_id, limit=10)
    for idx, (job, score) in enumerate(raw_results, 1):
        print(f"{idx}. Score: {score:.4f} | Job ID: {job.job_id} | Title: {job.title}")
        print(f"   [Job Specs: Visa={job.visa_sponsorship}, Max Salary={job.max_salary}, Remote={job.remote_ok}]")

    print("\n=========================================================\n")

    print("Executing Pipeline (After Filtering)...")
    search_service = SearchService(db)
    filtered_results = search_service.find_similar_jobs(candidate_id, limit=10)
    
    passed_jobs = [r for r in filtered_results if r['category'] == 'PENDING']
    rejected_jobs = [r for r in filtered_results if r['category'] == 'REJECTED']

    print(f"\nPassed Jobs ({len(passed_jobs)}):")
    for idx, r in enumerate(passed_jobs, 1):
        job = r['job']
        score = r['score']
        print(f"{idx}. Score: {score:.4f} | Job ID: {job.job_id} | Title: {job.title}")
        print(f"   [Job Specs: Visa={job.visa_sponsorship}, Max Salary={job.max_salary}, Remote={job.remote_ok}]")

    print(f"\nRejected Jobs ({len(rejected_jobs)}):")
    for idx, r in enumerate(rejected_jobs, 1):
        job = r['job']
        reason = r['reasoning']
        print(f"{idx}. Rejected Reason: {reason} | Title: {job.title}")
        print(f"   [Job Specs: Visa={job.visa_sponsorship}, Max Salary={job.max_salary}, Remote={job.remote_ok}]")

    print("\nVerify persistence in MatchResult table:")
    match_results = db.scalars(select(MatchResult).where(MatchResult.candidate_id == candidate_id)).all()
    print(f"Persisted MatchResults for candidate: {len(match_results)}")
    for mr in match_results:
        print(f" - Job: {mr.job_id} | Category: {mr.match_category} | Reason: {mr.reasoning}")
    
if __name__ == "__main__":
    run()
