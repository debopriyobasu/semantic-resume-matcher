import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text, index=True)
    original_filename: Mapped[str] = mapped_column(Text)
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    experience_years: Mapped[int | None] = mapped_column(Integer)
    education: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    desired_salary: Mapped[int | None] = mapped_column(Integer)
    visa_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    preferred_location: Mapped[str | None] = mapped_column(Text)
    preferred_remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    resume_path: Mapped[str] = mapped_column(Text)
    pipeline_status: Mapped[str] = mapped_column(Text, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    embeddings = relationship(
        "CandidateEmbedding",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    match_results = relationship(
        "MatchResult",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
