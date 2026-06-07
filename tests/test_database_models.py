from pgvector.sqlalchemy import Vector

from src.db.base import Base
from src.models import Candidate, CandidateEmbedding, JobEmbedding, JobPosting, MatchResult


def test_milestone_one_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "candidates",
        "candidate_embeddings",
        "job_postings",
        "job_embeddings",
        "match_results",
    }


def test_candidate_model_columns_match_milestone_one_contract() -> None:
    assert set(Candidate.__table__.columns.keys()) == {
        "candidate_id",
        "name",
        "email",
        "skills",
        "experience_years",
        "education",
        "location",
        "resume_path",
        "pipeline_status",
        "created_at",
        "updated_at",
    }


def test_embedding_models_use_768_dimension_pgvector_columns() -> None:
    candidate_embedding = CandidateEmbedding.__table__.columns["embedding"].type
    job_embedding = JobEmbedding.__table__.columns["embedding"].type

    assert isinstance(candidate_embedding, Vector)
    assert isinstance(job_embedding, Vector)
    assert candidate_embedding.dim == 768
    assert job_embedding.dim == 768


def test_job_and_match_tables_include_documented_columns() -> None:
    assert set(JobPosting.__table__.columns.keys()) == {
        "job_id",
        "title",
        "company",
        "location",
        "remote_ok",
        "visa_sponsorship",
        "min_salary",
        "max_salary",
        "required_skills",
        "description",
        "created_at",
    }
    assert set(MatchResult.__table__.columns.keys()) == {
        "match_id",
        "candidate_id",
        "job_id",
        "vector_score",
        "confidence",
        "match_category",
        "reasoning",
        "skill_gaps",
        "standout_strengths",
        "created_at",
    }
