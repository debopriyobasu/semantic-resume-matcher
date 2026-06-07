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
