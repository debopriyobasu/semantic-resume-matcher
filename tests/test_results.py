import uuid
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.db.session import get_db
from src.main import app
from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.models.match_result import MatchResult

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_get_candidate_status_found() -> None:
    candidate_id = uuid.uuid4()
    mock_db = Mock()

    # Mock the Candidate return
    mock_candidate = Candidate(candidate_id=candidate_id, pipeline_status="COMPLETE")
    mock_db.scalar.return_value = mock_candidate

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get(f"/candidate/{candidate_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == str(candidate_id)
    assert data["pipeline_status"] == "COMPLETE"
    assert data["status"] == "COMPLETE"


def test_get_candidate_status_not_found() -> None:
    candidate_id = uuid.uuid4()
    mock_db = Mock()

    # Mock Candidate not found
    mock_db.scalar.return_value = None

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get(f"/candidate/{candidate_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"


def test_get_match_results_found() -> None:
    candidate_id = uuid.uuid4()
    mock_db = Mock()

    mock_candidate = Candidate(candidate_id=candidate_id, pipeline_status="COMPLETE")

    job_id = uuid.uuid4()
    mock_job = JobPosting(
        job_id=job_id,
        title="Software Engineer",
        company="Tech Corp",
        location="Remote",
        remote_ok=True,
        min_salary=100000,
        max_salary=150000,
    )

    match_id = uuid.uuid4()
    mock_match = MatchResult(
        match_id=match_id,
        candidate_id=candidate_id,
        job_id=job_id,
        vector_score=0.95,
        confidence=0.9,
        match_category="STRONG_MATCH",
        reasoning="Good fit",
        skill_gaps=[],
        standout_strengths=["Python"],
        job=mock_job,
    )

    def scalar_mock(stmt):
        # We assume the first query is for candidate
        # The query to MatchResult is handled by scalars
        return mock_candidate

    mock_db.scalar.side_effect = scalar_mock

    # Mock the matches return
    mock_matches = Mock()
    mock_matches.all.return_value = [mock_match]
    mock_db.scalars.return_value = mock_matches

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get(f"/candidate/{candidate_id}/matches")
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_id"] == str(candidate_id)
    assert len(data["matches"]) == 1
    match_data = data["matches"][0]
    assert match_data["match_id"] == str(match_id)
    assert match_data["vector_score"] == 0.95
    assert match_data["match_category"] == "STRONG_MATCH"
    assert match_data["job"]["job_id"] == str(job_id)
    assert match_data["job"]["title"] == "Software Engineer"


def test_get_match_results_candidate_not_found() -> None:
    candidate_id = uuid.uuid4()
    mock_db = Mock()

    mock_db.scalar.return_value = None

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    response = client.get(f"/candidate/{candidate_id}/matches")
    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"
