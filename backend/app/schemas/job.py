from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class JobBase(BaseModel):
    title: str
    company: str
    location: str | None = None
    job_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = "USD"
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    skills_required: list[str] = Field(default_factory=list)
    source: str
    apply_url: str | None = None
    posted_at: datetime | None = None


class JobResponse(JobBase):
    id: str
    scraped_at: datetime

    model_config = {"from_attributes": True}


class JobMatchResult(BaseModel):
    """Returned when a resume is matched against a list of jobs."""
    job: JobResponse
    match_score: float = Field(..., ge=0.0, le=1.0)
    match_reasons: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class JobSearchParams(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    location: str | None = None
    job_type: str | None = None  # remote | hybrid | onsite
    page: int = Field(default=1, ge=1)
    results_per_page: int = Field(default=20, ge=1, le=50)
