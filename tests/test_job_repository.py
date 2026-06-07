from unittest.mock import Mock

from sqlalchemy import Select

from src.models.job_posting import JobPosting
from src.repositories.job_repository import bulk_create_jobs, count_jobs, create_job


def test_create_job_persists_and_returns_job_posting() -> None:
    db = Mock()
    job_data = {
        "title": "Backend Engineer",
        "company": "Acme",
        "location": "Remote",
        "remote_ok": True,
        "visa_sponsorship": False,
        "min_salary": 120000,
        "max_salary": 160000,
        "required_skills": ["Python", "FastAPI"],
        "description": "Build APIs.",
    }

    job = create_job(db, job_data)

    assert isinstance(job, JobPosting)
    assert job.title == "Backend Engineer"
    db.add.assert_called_once_with(job)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(job)


def test_bulk_create_jobs_persists_all_jobs() -> None:
    db = Mock()
    jobs_data = [
        {
            "title": "Data Engineer",
            "company": "Acme",
            "location": "New York, NY",
            "remote_ok": False,
            "visa_sponsorship": True,
            "min_salary": 110000,
            "max_salary": 150000,
            "required_skills": ["SQL", "Python"],
            "description": "Build data pipelines.",
        },
        {
            "title": "ML Engineer",
            "company": "Beta",
            "location": "Remote",
            "remote_ok": True,
            "visa_sponsorship": True,
            "min_salary": 130000,
            "max_salary": 180000,
            "required_skills": ["Python", "ML"],
            "description": "Ship model features.",
        },
    ]

    jobs = bulk_create_jobs(db, jobs_data)

    assert len(jobs) == 2
    assert all(isinstance(job, JobPosting) for job in jobs)
    db.add_all.assert_called_once_with(jobs)
    db.commit.assert_called_once_with()
    assert db.refresh.call_count == 2


def test_count_jobs_queries_job_postings() -> None:
    db = Mock()
    db.scalar.return_value = 12

    total = count_jobs(db)

    assert total == 12
    statement = db.scalar.call_args.args[0]
    assert isinstance(statement, Select)
