from pathlib import Path


def test_initial_migration_enables_pgvector_and_creates_milestone_one_tables() -> None:
    migration = Path("migrations/versions/20260607_0001_initial_database.py").read_text()

    assert "CREATE EXTENSION IF NOT EXISTS vector" in migration
    for table_name in [
        "candidates",
        "candidate_embeddings",
        "job_postings",
        "job_embeddings",
        "match_results",
    ]:
        assert f'"{table_name}"' in migration
