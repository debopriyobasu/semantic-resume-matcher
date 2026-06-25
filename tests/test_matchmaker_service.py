import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.services.matchmaker_service import MatchmakerService


@pytest.fixture
def matchmaker_service():
    return MatchmakerService()


def test_evaluate_matches_happy_path(matchmaker_service):
    db_mock = MagicMock()

    mock_candidate = MagicMock()
    mock_candidate.skills = ["Python"]
    mock_candidate.experience_years = 5
    mock_candidate.education = "BSc"

    mock_match = MagicMock()
    mock_match.job_id = uuid.uuid4()
    mock_match.match_id = uuid.uuid4()

    mock_job = MagicMock()
    mock_job.title = "Software Engineer"
    mock_job.company = "Tech Corp"
    mock_job.required_skills = ["Python"]
    mock_job.description = "Job desc"

    db_mock.query.return_value.filter.return_value.first.side_effect = [mock_candidate, mock_job]

    with (
        patch("src.services.matchmaker_service.match_result_repository") as mock_repo,
        patch("httpx.post") as mock_post,
    ):
        mock_repo.get_pending_matches.return_value = [mock_match]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '{"confidence": 0.9, "match_category": "STRONG_MATCH", "reasoning": "Good fit", "skill_gaps": [], "standout_strengths": ["Python"]}'
            }
        }
        mock_post.return_value = mock_response

        matchmaker_service.evaluate_matches(db_mock, uuid.uuid4())

        mock_repo.update_match_result.assert_called_once()
        args, kwargs = mock_repo.update_match_result.call_args
        assert args[2]["confidence"] == 0.9
        assert args[2]["match_category"] == "STRONG_MATCH"


def test_evaluate_matches_json_decode_error(matchmaker_service):
    db_mock = MagicMock()
    mock_candidate = MagicMock()
    mock_candidate.skills = ["Python"]
    mock_candidate.experience_years = 5
    mock_candidate.education = "BSc"

    mock_match = MagicMock()
    mock_match.job_id = uuid.uuid4()
    mock_match.match_id = uuid.uuid4()

    mock_job = MagicMock()
    mock_job.title = "Software Engineer"
    mock_job.company = "Tech Corp"
    mock_job.required_skills = ["Python"]
    mock_job.description = "Job desc"

    db_mock.query.return_value.filter.return_value.first.side_effect = [mock_candidate, mock_job]

    with (
        patch("src.services.matchmaker_service.match_result_repository") as mock_repo,
        patch("httpx.post") as mock_post,
        patch("src.services.matchmaker_service.time.sleep"),
    ):
        mock_repo.get_pending_matches.return_value = [mock_match]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '{"broken_json'
            }
        }
        mock_post.return_value = mock_response

        matchmaker_service.evaluate_matches(db_mock, uuid.uuid4())

        assert mock_repo.update_match_result.call_count == 0
        assert mock_post.call_count == 4


def test_evaluate_matches_validation_error(matchmaker_service):
    db_mock = MagicMock()
    mock_candidate = MagicMock()
    mock_candidate.skills = ["Python"]
    mock_candidate.experience_years = 5
    mock_candidate.education = "BSc"

    mock_match = MagicMock()
    mock_match.job_id = uuid.uuid4()
    mock_match.match_id = uuid.uuid4()

    mock_job = MagicMock()
    mock_job.title = "Software Engineer"
    mock_job.company = "Tech Corp"
    mock_job.required_skills = ["Python"]
    mock_job.description = "Job desc"

    db_mock.query.return_value.filter.return_value.first.side_effect = [mock_candidate, mock_job]

    with (
        patch("src.services.matchmaker_service.match_result_repository") as mock_repo,
        patch("httpx.post") as mock_post,
        patch("src.services.matchmaker_service.time.sleep"),
    ):
        mock_repo.get_pending_matches.return_value = [mock_match]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '{"confidence": "not a float", "match_category": "INVALID"}'
            }
        }
        mock_post.return_value = mock_response

        matchmaker_service.evaluate_matches(db_mock, uuid.uuid4())

        assert mock_repo.update_match_result.call_count == 0
        assert mock_post.call_count == 1
