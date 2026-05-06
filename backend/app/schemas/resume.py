"""
Pydantic schemas for Resume API request/response validation.
Separating schemas from models keeps the API contract independent of DB internals.
"""
from datetime import datetime

from pydantic import BaseModel, Field


# ── Parsed Resume Structure (AI output) ──────────────────────────────────────
class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    graduation_year: str | None = None


class ParsedResume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


# ── API Response Schemas ──────────────────────────────────────────────────────
class ResumeResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    parsed_data: ParsedResume | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeListItem(BaseModel):
    id: str
    original_filename: str
    file_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
