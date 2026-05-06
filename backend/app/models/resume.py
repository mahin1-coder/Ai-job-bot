"""
Resume model — stores raw file reference + AI-parsed structured data.
The parsed_data JSON column holds the structured resume (skills, experience, etc.)
so we don't re-parse on every request.
"""
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Original file info
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf | docx | txt

    # Raw extracted text (used for re-parsing or semantic search)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI-structured data: name, email, phone, summary, skills[], experience[], education[]
    # Stored as JSON so schema changes don't require migrations
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # OpenAI embedding vector stored as a JSON list (float[])
    # For production, use pgvector extension instead
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file={self.original_filename}>"
