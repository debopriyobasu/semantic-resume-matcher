"""Initial database schema.

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260607_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "candidates",
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("resume_path", sa.Text(), nullable=False),
        sa.Column("pipeline_status", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_candidates_email", "candidates", ["email"])

    op.create_table(
        "job_postings",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("company", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("remote_ok", sa.Boolean(), nullable=False),
        sa.Column("visa_sponsorship", sa.Boolean(), nullable=False),
        sa.Column("min_salary", sa.Integer(), nullable=True),
        sa.Column("max_salary", sa.Integer(), nullable=True),
        sa.Column("required_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "candidate_embeddings",
        sa.Column("embedding_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.candidate_id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_candidate_embeddings_candidate_id",
        "candidate_embeddings",
        ["candidate_id"],
    )

    op.create_table(
        "job_embeddings",
        sa.Column("embedding_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.job_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_job_embeddings_job_id", "job_embeddings", ["job_id"])

    op.create_table(
        "match_results",
        sa.Column("match_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vector_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("match_category", sa.Text(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("skill_gaps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("standout_strengths", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.candidate_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.job_id"], ondelete="CASCADE"),
    )
    op.create_index("ix_match_results_candidate_id", "match_results", ["candidate_id"])
    op.create_index("ix_match_results_job_id", "match_results", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_match_results_job_id", table_name="match_results")
    op.drop_index("ix_match_results_candidate_id", table_name="match_results")
    op.drop_table("match_results")
    op.drop_index("ix_job_embeddings_job_id", table_name="job_embeddings")
    op.drop_table("job_embeddings")
    op.drop_index("ix_candidate_embeddings_candidate_id", table_name="candidate_embeddings")
    op.drop_table("candidate_embeddings")
    op.drop_table("job_postings")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_table("candidates")
