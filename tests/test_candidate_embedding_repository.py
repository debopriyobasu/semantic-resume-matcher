import uuid
from unittest.mock import Mock

from sqlalchemy import Select

from src.models.candidate_embedding import CandidateEmbedding
from src.repositories.candidate_embedding_repository import (
    create_candidate_embedding,
    get_candidate_embedding,
)


def test_create_candidate_embedding_persists() -> None:
    db = Mock()
    candidate_id = uuid.uuid4()
    embedding = [0.1, 0.2, 0.3]

    result = create_candidate_embedding(db, candidate_id, embedding)

    assert isinstance(result, CandidateEmbedding)
    assert result.candidate_id == candidate_id
    assert result.embedding == embedding

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(result)


def test_get_candidate_embedding_queries() -> None:
    db = Mock()
    mock_embedding = CandidateEmbedding(candidate_id=uuid.uuid4(), embedding=[0.1, 0.2, 0.3])
    db.scalar.return_value = mock_embedding

    candidate_id = uuid.uuid4()
    result = get_candidate_embedding(db, candidate_id)

    assert result == mock_embedding
    statement = db.scalar.call_args.args[0]
    assert isinstance(statement, Select)
