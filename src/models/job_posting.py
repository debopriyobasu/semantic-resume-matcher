import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class JobPosting(Base):
    __tablename__ = "job_postings"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    remote_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    visa_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False)
    min_salary: Mapped[int | None] = mapped_column(Integer)
    max_salary: Mapped[int | None] = mapped_column(Integer)
    required_skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    embeddings = relationship(
        "JobEmbedding",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    match_results = relationship(
        "MatchResult",
        back_populates="job",
        cascade="all, delete-orphan",
    )
