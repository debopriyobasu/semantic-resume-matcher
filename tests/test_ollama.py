import json
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import Settings
from src.core.exceptions import ResumeParseError
from src.schemas.candidate import CandidateProfile
from src.schemas.matchmaker import MatchEvaluation
from src.services.embedding_service import EmbeddingError, EmbeddingService
from src.services.matchmaker_service import MatchmakerService
from src.services.resume_parser import ResumeParserService


@pytest.fixture
def ollama_settings():
    import os
    os.environ["USE_OLLAMA"] = "true"
    settings = Settings(
        use_ollama=True,
        ollama_base_url="http://localhost:11434",
        ollama_llm_model="llama3.2",
        ollama_embed_model="nomic-embed-text",
    )
    os.environ["USE_OLLAMA"] = "false"
    return settings


@patch("src.services.resume_parser.get_settings")
@patch("httpx.post")
def test_ollama_parser_success(mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings) -> None:
    mock_get_settings.return_value = ollama_settings

    # Mock Ollama HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "content": json.dumps({
                "name": "Jane Doe",
                "email": "jane@example.com",
                "skills": ["Python", "Docker"],
                "experience_years": 3,
                "education": "MS",
                "location": "Boston",
            })
        }
    }
    mock_post.return_value = mock_response

    parser = ResumeParserService()
    profile = parser.extract_profile("some resume text")

    assert isinstance(profile, CandidateProfile)
    assert profile.name == "Jane Doe"
    assert profile.skills == ["Python", "Docker"]
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["json"]["model"] == ollama_settings.ollama_llm_model


@patch("src.services.resume_parser.get_settings")
@patch("httpx.post")
def test_ollama_parser_failure(mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings) -> None:
    mock_get_settings.return_value = ollama_settings

    # Mock Ollama failing response
    mock_post.side_effect = Exception("Ollama connection failed")

    parser = ResumeParserService()
    with pytest.raises(ResumeParseError):
        parser.extract_profile("some resume text")


@patch("src.services.embedding_service.get_settings")
@patch("httpx.post")
def test_ollama_embedding_success_dimensions_padding(
    mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings
) -> None:
    mock_get_settings.return_value = ollama_settings

    # Return a 3-dimensional embedding (should be padded to 768)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embedding": [0.5, 1.0, 1.5]}
    mock_post.return_value = mock_response

    service = EmbeddingService()
    embedding = service.generate_embedding("some text")

    assert len(embedding) == 768
    assert embedding[0] == 0.5
    assert embedding[1] == 1.0
    assert embedding[2] == 1.5
    assert all(val == 0.0 for val in embedding[3:])


@patch("src.services.embedding_service.get_settings")
@patch("httpx.post")
def test_ollama_embedding_success_dimensions_truncating(
    mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings
) -> None:
    mock_get_settings.return_value = ollama_settings

    # Return a 770-dimensional embedding (should be truncated to 768)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embedding": [0.2] * 770}
    mock_post.return_value = mock_response

    service = EmbeddingService()
    embedding = service.generate_embedding("some text")

    assert len(embedding) == 768
    assert all(val == 0.2 for val in embedding)


@patch("src.services.embedding_service.get_settings")
@patch("httpx.post")
def test_ollama_embedding_failure(mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings) -> None:
    mock_get_settings.return_value = ollama_settings
    mock_post.side_effect = Exception("Ollama embedding endpoint error")

    service = EmbeddingService()
    with pytest.raises(EmbeddingError):
        service.generate_embedding("some text")


@patch("src.services.matchmaker_service.get_settings")
@patch("httpx.post")
def test_ollama_matchmaker_success(mock_post: MagicMock, mock_get_settings: MagicMock, ollama_settings: Settings) -> None:
    mock_get_settings.return_value = ollama_settings

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "content": json.dumps({
                "confidence": 0.85,
                "match_category": "STRONG_MATCH",
                "reasoning": "Fits the criteria.",
                "skill_gaps": [],
                "standout_strengths": ["Python"],
            })
        }
    }
    mock_post.return_value = mock_response

    service = MatchmakerService()
    evaluation = service._call_model_with_retries(client=None, prompt="some prompt")

    assert isinstance(evaluation, MatchEvaluation)
    assert evaluation.confidence == 0.85
    assert evaluation.match_category == "STRONG_MATCH"
    mock_post.assert_called_once()
