from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.models.job_posting import JobPosting


def create_job(db: Session, job_data: dict) -> JobPosting:
    job = JobPosting(**job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def bulk_create_jobs(db: Session, jobs_data: list[dict]) -> list[JobPosting]:
    jobs = [JobPosting(**job_data) for job_data in jobs_data]
    db.add_all(jobs)
    db.commit()
    for job in jobs:
        db.refresh(job)
    return jobs


def count_jobs(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(JobPosting)) or 0


def delete_all_jobs(db: Session) -> int:
    result = db.execute(delete(JobPosting))
    db.commit()
    return result.rowcount
