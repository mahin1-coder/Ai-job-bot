from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus
from app.schemas.job import JobResponse
from app.schemas.resume import ResumeListItem


class ApplicationCreate(BaseModel):
    resume_id: str
    job_id: str


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = None


class ApplicationResponse(BaseModel):
    id: str
    resume_id: str
    job_id: str
    match_score: float | None = None
    match_reasons: list[str] | None = None
    missing_skills: list[str] | None = None
    tailored_resume: str | None = None
    cover_letter: str | None = None
    status: str
    applied_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    # Nested objects (populated via relationship)
    job: JobResponse | None = None

    model_config = {"from_attributes": True}


class GenerateArtifactsRequest(BaseModel):
    """Request to generate tailored resume + cover letter for an application."""
    application_id: str
    tone: str = "professional"  # professional | enthusiastic | concise


class GenerateArtifactsResponse(BaseModel):
    application_id: str
    tailored_resume: str
    cover_letter: str
