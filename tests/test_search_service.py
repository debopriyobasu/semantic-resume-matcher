import uuid
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.services.search_service import SearchService


def test_find_similar_jobs_candidate_not_found() -> None:
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None

    service = SearchService(db)
    results = service.find_similar_jobs(uuid.uuid4())
    assert results == []


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_no_similar_jobs(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=False,
        desired_salary=None,
        preferred_location=None,
        preferred_remote=False,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate
    mock_find_similar_jobs.return_value = []

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)
    assert results == []


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_happy_path_no_mismatches(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=False,
        desired_salary=100000,
        preferred_location="New York",
        preferred_remote=True,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        visa_sponsorship=True,
        max_salary=120000,
        location="New York",
        remote_ok=True,
    )
    mock_find_similar_jobs.return_value = [(job, 0.85)]

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)

    assert len(results) == 1
    assert results[0]["category"] == "PENDING"
    assert results[0]["reasoning"] == ""
    assert results[0]["score"] == 0.85
    assert results[0]["job"] == job
    db.add.assert_called_once()
    db.commit.assert_called_once()


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_visa_mismatch(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=True,
        desired_salary=None,
        preferred_location=None,
        preferred_remote=False,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        visa_sponsorship=False,
        max_salary=120000,
        location="New York",
        remote_ok=True,
    )
    mock_find_similar_jobs.return_value = [(job, 0.85)]

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)

    assert len(results) == 1
    assert results[0]["category"] == "REJECTED"
    assert results[0]["reasoning"] == "VISA_MISMATCH"


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_salary_mismatch(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=False,
        desired_salary=150000,
        preferred_location=None,
        preferred_remote=False,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        visa_sponsorship=True,
        max_salary=120000,
        location="New York",
        remote_ok=True,
    )
    mock_find_similar_jobs.return_value = [(job, 0.85)]

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)

    assert len(results) == 1
    assert results[0]["category"] == "REJECTED"
    assert results[0]["reasoning"] == "SALARY_MISMATCH"


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_location_mismatch(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=False,
        desired_salary=None,
        preferred_location="San Francisco",
        preferred_remote=False,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        visa_sponsorship=True,
        max_salary=120000,
        location="New York",
        remote_ok=True,
    )
    mock_find_similar_jobs.return_value = [(job, 0.85)]

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)

    assert len(results) == 1
    assert results[0]["category"] == "REJECTED"
    assert results[0]["reasoning"] == "LOCATION_MISMATCH"


@patch("src.services.search_service.search_repository.find_similar_jobs")
def test_find_similar_jobs_remote_mismatch(mock_find_similar_jobs: Mock) -> None:
    db = Mock(spec=Session)
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        visa_required=False,
        desired_salary=None,
        preferred_location=None,
        preferred_remote=True,
    )
    db.query.return_value.filter.return_value.first.return_value = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        visa_sponsorship=True,
        max_salary=120000,
        location="New York",
        remote_ok=False,
    )
    mock_find_similar_jobs.return_value = [(job, 0.85)]

    service = SearchService(db)
    results = service.find_similar_jobs(candidate.candidate_id)

    assert len(results) == 1
    assert results[0]["category"] == "REJECTED"
    assert results[0]["reasoning"] == "REMOTE_MISMATCH"
