"""
Jobs Router

GET  /api/v1/jobs/search          → search/scrape jobs from external sources
GET  /api/v1/jobs/                → list saved jobs from DB
GET  /api/v1/jobs/{id}            → get single job
POST /api/v1/jobs/match/{resume_id} → AI-match resume against search results
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.job import JobMatchResult, JobResponse, JobSearchParams
from app.schemas.resume import ParsedResume
from app.services.job_matcher import job_matcher_service
from app.services.job_scraper import job_scraper_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search", response_model=list[JobResponse])
async def search_jobs(
    query: str = Query(..., min_length=2, description="Job title or keywords"),
    location: str = Query(default="", description="City, state, or 'remote'"),
    job_type: str | None = Query(default=None, description="remote | hybrid | onsite"),
    page: int = Query(default=1, ge=1),
    results_per_page: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch jobs from Adzuna + RemoteOK, deduplicate, and save to DB.
    Returns normalised job objects.
    """
    raw_jobs = await job_scraper_service.search(
        query=query,
        location=location,
        job_type=job_type,
        page=page,
        results_per_page=results_per_page,
    )

    saved_jobs: list[Job] = []
    for raw in raw_jobs:
        # Upsert by source + source_job_id to avoid duplicates
        existing = None
        if raw.get("source_job_id"):
            result = await db.execute(
                select(Job).where(
                    Job.source == raw["source"],
                    Job.source_job_id == raw["source_job_id"],
                )
            )
            existing = result.scalar_one_or_none()

        if existing:
            saved_jobs.append(existing)
        else:
            job = Job(**{k: v for k, v in raw.items() if hasattr(Job, k)})
            db.add(job)
            await db.flush()
            await db.refresh(job)
            saved_jobs.append(job)

    return saved_jobs


@router.post("/match/{resume_id}", response_model=list[JobMatchResult])
async def match_jobs_to_resume(
    resume_id: str,
    query: str = Query(..., description="Job search query"),
    location: str = Query(default=""),
    top_k: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Search jobs, then rank them by AI similarity to the given resume.
    Returns top-K matches with scores and explanations.
    """
    # Load resume
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.parsed_data:
        raise HTTPException(
            status_code=422, detail="Resume has not been parsed yet. Re-upload."
        )

    parsed_resume = ParsedResume(**resume.parsed_data)

    # Fetch jobs
    raw_jobs = await job_scraper_service.search(query=query, location=location, results_per_page=50)
    if not raw_jobs:
        return []

    # AI match
    match_results = await job_matcher_service.match_resume_to_jobs(
        parsed_resume=parsed_resume,
        jobs=raw_jobs,
        top_k=top_k,
    )

    # Build response: merge match result with full job data
    output: list[JobMatchResult] = []
    job_map = {j.get("source_job_id", i): j for i, j in enumerate(raw_jobs)}

    for match in match_results:
        job_data = job_map.get(match.job_id) or raw_jobs[0]
        # Save job to DB
        job_obj = Job(**{k: v for k, v in job_data.items() if hasattr(Job, k)})
        db.add(job_obj)
        await db.flush()
        await db.refresh(job_obj)

        output.append(
            JobMatchResult(
                job=JobResponse.model_validate(job_obj),
                match_score=match.match_score,
                match_reasons=match.match_reasons,
                missing_skills=match.missing_skills,
            )
        )

    return output


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).order_by(Job.scraped_at.desc()).limit(limit))
    return list(result.scalars().all())


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
