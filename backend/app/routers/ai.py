"""
AI Router — generates tailored resumes and cover letters.

POST /api/v1/ai/generate                  → generate both artifacts (non-streaming)
GET  /api/v1/ai/stream/resume/{app_id}    → SSE stream: tailored resume
GET  /api/v1/ai/stream/cover-letter/{app_id} → SSE stream: cover letter
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.application import GenerateArtifactsRequest, GenerateArtifactsResponse
from app.schemas.resume import ParsedResume
from app.services.ai_generator import ai_generator_service
from app.services.application_tracker import application_tracker_service

logger = logging.getLogger(__name__)
router = APIRouter()


async def _load_application_context(application_id: str, db: AsyncSession):
    """Helper to load application + resume + job from DB."""
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    resume_result = await db.execute(select(Resume).where(Resume.id == app.resume_id))
    resume = resume_result.scalar_one_or_none()
    if not resume or not resume.parsed_data:
        raise HTTPException(status_code=422, detail="Resume data not available")

    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return app, ParsedResume(**resume.parsed_data), job


@router.post("/generate", response_model=GenerateArtifactsResponse)
async def generate_artifacts(
    payload: GenerateArtifactsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Non-streaming: generate tailored resume + cover letter and save to DB.
    Use this for background generation. For real-time UX, use the /stream endpoints.
    """
    app, parsed_resume, job = await _load_application_context(payload.application_id, db)
    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "skills_required": job.skills_required or [],
    }

    tailored_resume, cover_letter = await _generate_both(
        parsed_resume, job_dict, payload.tone
    )

    # Persist to application record
    await application_tracker_service.save_artifacts(
        db=db,
        application_id=app.id,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
    )

    return GenerateArtifactsResponse(
        application_id=app.id,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
    )


@router.get("/stream/resume/{application_id}")
async def stream_resume(
    application_id: str,
    tone: str = "professional",
    db: AsyncSession = Depends(get_db),
):
    """Server-Sent Events stream for real-time resume generation."""
    _, parsed_resume, job = await _load_application_context(application_id, db)
    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "skills_required": job.skills_required or [],
    }

    async def event_generator():
        async for chunk in ai_generator_service.stream_tailored_resume(
            parsed_resume, job_dict, tone
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/stream/cover-letter/{application_id}")
async def stream_cover_letter(
    application_id: str,
    tone: str = "professional",
    db: AsyncSession = Depends(get_db),
):
    """Server-Sent Events stream for real-time cover letter generation."""
    _, parsed_resume, job = await _load_application_context(application_id, db)
    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "skills_required": job.skills_required or [],
    }

    async def event_generator():
        async for chunk in ai_generator_service.stream_cover_letter(
            parsed_resume, job_dict, tone
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _generate_both(parsed_resume, job_dict, tone) -> tuple[str, str]:
    """Run both AI generation calls concurrently."""
    import asyncio
    tailored, cover = await asyncio.gather(
        ai_generator_service.generate_tailored_resume(parsed_resume, job_dict, tone),
        ai_generator_service.generate_cover_letter(parsed_resume, job_dict, tone),
    )
    return tailored, cover
