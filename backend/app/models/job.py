"""
Job model — scraped or API-sourced job listings.
match_score is populated when a user runs AI matching against their resume.
"""
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # ── Job details ───────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # remote|hybrid|onsite
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # ── Description ───────────────────────────────────────────────
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[list | None] = mapped_column(JSON, nullable=True)  # extracted list
    skills_required: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Source ────────────────────────────────────────────────────
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # adzuna|remoteok|linkedin
    source_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    apply_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── AI matching ───────────────────────────────────────────────
    # Cached embedding for fast similarity comparisons
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} company={self.company}>"
