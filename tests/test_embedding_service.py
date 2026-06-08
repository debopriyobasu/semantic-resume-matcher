from unittest.mock import MagicMock, patch

import pytest

from src.services.embedding_service import EmbeddingError, EmbeddingService


@patch("src.services.embedding_service.genai.Client")
def test_generate_embedding_success(mock_client_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1, 0.2, 0.3])]
    mock_client.models.embed_content.return_value = mock_response

    service = EmbeddingService()
    embedding = service.generate_embedding("test text")

    assert embedding == [0.1, 0.2, 0.3]
    from google.genai import types
    mock_client.models.embed_content.assert_called_once_with(
        model="gemini-embedding-2",
        contents="test text",
        config=types.EmbedContentConfig(output_dimensionality=768),
    )


@patch("src.services.embedding_service.genai.Client")
def test_generate_embedding_failure(mock_client_class: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.models.embed_content.side_effect = Exception("API error")

    service = EmbeddingService()
    with pytest.raises(EmbeddingError):
        service.generate_embedding("test text")


def test_build_candidate_text() -> None:
    from src.models.candidate import Candidate
    import uuid
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        skills=["Python", "FastAPI", "Docker"],
        experience_years=5,
        education="Bachelors",
        location="Remote"
    )
    service = EmbeddingService()
    text = service.build_candidate_text(candidate)
    expected_text = (
        "Skills:\n"
        "Python\n"
        "FastAPI\n"
        "Docker\n\n"
        "Experience:\n"
        "5 years backend engineering\n\n"
        "Education:\n"
        "Bachelors\n\n"
        "Location:\n"
        "Remote"
    )
    assert text == expected_text


@patch("src.services.embedding_service.EmbeddingService.generate_embedding")
def test_generate_candidate_embedding(mock_generate: MagicMock) -> None:
    from src.models.candidate import Candidate
    import uuid
    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        skills=["Python"]
    )
    mock_generate.return_value = [0.1, 0.2, 0.3]
    
    service = EmbeddingService()
    embedding = service.generate_candidate_embedding(candidate)
    
    assert embedding == [0.1, 0.2, 0.3]
    mock_generate.assert_called_once()
    assert "Skills:\nPython" in mock_generate.call_args.args[0]
