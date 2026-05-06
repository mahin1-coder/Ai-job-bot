"""
Application model — tracks each job application attempt.
Stores AI-generated artifacts (tailored resume, cover letter) alongside status.
"""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ApplicationStatus(str, Enum):
    PENDING = "pending"          # matched, not yet applied
    APPLYING = "applying"        # auto-fill in progress
    APPLIED = "applied"          # submitted
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # ── Foreign keys ─────────────────────────────────────────────
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )

    # ── AI match result ───────────────────────────────────────────
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0–1.0
    match_reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)  # ["Strong Python match", ...]
    missing_skills: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── AI-generated artifacts ────────────────────────────────────
    tailored_resume: Mapped[str | None] = mapped_column(Text, nullable=True)   # markdown/plain text
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Application tracking ──────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ApplicationStatus.PENDING
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ─────────────────────────────────────────────
    resume = relationship("Resume", lazy="selectin")
    job = relationship("Job", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Application id={self.id} job_id={self.job_id} status={self.status}>"
