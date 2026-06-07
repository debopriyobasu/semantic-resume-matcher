import uuid
from unittest.mock import Mock

from sqlalchemy import Select

from src.models.job_embedding import JobEmbedding
from src.repositories.job_embedding_repository import create_job_embedding, get_job_embedding


def test_create_job_embedding_persists() -> None:
    db = Mock()
    job_id = uuid.uuid4()
    embedding = [0.1, 0.2, 0.3]

    result = create_job_embedding(db, job_id, embedding)

    assert isinstance(result, JobEmbedding)
    assert result.job_id == job_id
    assert result.embedding == embedding

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(result)


def test_get_job_embedding_queries() -> None:
    db = Mock()
    mock_embedding = JobEmbedding(job_id=uuid.uuid4(), embedding=[0.1, 0.2, 0.3])
    db.scalar.return_value = mock_embedding

    job_id = uuid.uuid4()
    result = get_job_embedding(db, job_id)

    assert result == mock_embedding
    statement = db.scalar.call_args.args[0]
    assert isinstance(statement, Select)
