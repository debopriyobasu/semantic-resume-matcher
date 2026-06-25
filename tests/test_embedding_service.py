from unittest.mock import MagicMock, patch

import pytest

from src.services.embedding_service import EmbeddingError, EmbeddingService


@patch("httpx.post")
def test_generate_embedding_success(mock_post: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
    mock_post.return_value = mock_response

    service = EmbeddingService()
    embedding = service.generate_embedding("test text")

    assert len(embedding) == 768
    assert embedding[0] == 0.1
    assert embedding[1] == 0.2
    assert embedding[2] == 0.3
    assert all(v == 0.0 for v in embedding[3:])
    mock_post.assert_called_once()


@patch("httpx.post")
def test_generate_embedding_failure(mock_post: MagicMock) -> None:
    mock_post.side_effect = Exception("API error")

    service = EmbeddingService()
    with pytest.raises(EmbeddingError):
        service.generate_embedding("test text")


def test_build_candidate_text() -> None:
    import uuid

    from src.models.candidate import Candidate

    candidate = Candidate(
        candidate_id=uuid.uuid4(),
        skills=["Python", "FastAPI", "Docker"],
        experience_years=5,
        education="Bachelors",
        location="Remote",
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
    import uuid

    from src.models.candidate import Candidate

    candidate = Candidate(candidate_id=uuid.uuid4(), skills=["Python"])
    mock_generate.return_value = [0.1, 0.2, 0.3]

    service = EmbeddingService()
    embedding = service.generate_candidate_embedding(candidate)

    assert embedding == [0.1, 0.2, 0.3]
    mock_generate.assert_called_once()
    assert "Skills:\nPython" in mock_generate.call_args.args[0]
