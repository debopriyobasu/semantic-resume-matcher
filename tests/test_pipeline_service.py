import uuid
from unittest.mock import Mock, patch

import pytest

from src.models.candidate import Candidate
from src.services.pipeline_service import PipelineService


@pytest.fixture
def mock_db():
    db = Mock()
    candidate = Mock(spec=Candidate)
    candidate.candidate_id = uuid.uuid4()
    candidate.resume_path = "dummy_path.pdf"

    mock_query = Mock()
    mock_filter = Mock()
    mock_first = Mock(return_value=candidate)

    db.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first = mock_first

    return db, candidate


@patch("builtins.open")
@patch("src.services.pipeline_service.update_candidate_profile")
@patch("src.services.pipeline_service.create_candidate_embedding")
@patch("src.services.pipeline_service.ResumeParserService")
@patch("src.services.pipeline_service.EmbeddingService")
@patch("src.services.pipeline_service.SearchService")
@patch("src.services.pipeline_service.MatchmakerService")
def test_pipeline_happy_path(
    mock_matchmaker_cls,
    mock_search_cls,
    mock_embed_cls,
    mock_parser_cls,
    mock_create_embedding,
    mock_update_profile,
    mock_open,
    mock_db,
):
    db, candidate = mock_db

    mock_parser = mock_parser_cls.return_value
    mock_parser.extract_text.return_value = "extracted text"
    mock_parser.extract_profile.return_value = Mock()

    mock_embed = mock_embed_cls.return_value
    mock_embed.generate_candidate_embedding.return_value = [0.1, 0.2, 0.3]

    mock_open.return_value.__enter__.return_value.read.return_value = b"pdf content"

    service = PipelineService(db)
    service.process_candidate(candidate.candidate_id)

    assert candidate.pipeline_status == "COMPLETE"
    assert db.commit.call_count >= 5


@patch("src.services.pipeline_service.ResumeParserService")
def test_pipeline_failure_path(mock_parser_cls, mock_db):
    db, candidate = mock_db

    mock_parser = mock_parser_cls.return_value
    mock_parser.extract_text.side_effect = Exception("Parse failed")

    service = PipelineService(db)
    with patch("builtins.open") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b"pdf content"
        service.process_candidate(candidate.candidate_id)

    assert candidate.pipeline_status == "FAILED"
    db.commit.assert_called()
