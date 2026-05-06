"""
Resume Router — handles upload, parsing, and retrieval.

POST /api/v1/resumes/upload  → upload + parse a resume file
GET  /api/v1/resumes/        → list all resumes
GET  /api/v1/resumes/{id}    → get single resume with parsed data
DELETE /api/v1/resumes/{id}  → delete resume
"""
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeListItem, ResumeResponse
from app.services.resume_parser import resume_parser_service
from app.utils.file_utils import validate_resume_file, save_upload

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a resume file (PDF/DOCX/TXT).
    Automatically extracts text and structures it with AI.
    """
    # Validate file
    validate_resume_file(file, ALLOWED_EXTENSIONS, settings.max_file_size_bytes)

    # Save to disk
    file_suffix = Path(file.filename).suffix.lower()
    saved_path = await save_upload(file, settings.UPLOAD_DIR)

    # Parse with AI
    try:
        raw_text, parsed_data = await resume_parser_service.parse(
            file_path=saved_path,
            file_type=file_suffix.strip("."),
        )
    except Exception as e:
        logger.error("Resume parsing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse resume: {str(e)}",
        )

    # Persist to database
    resume = Resume(
        original_filename=file.filename,
        file_path=saved_path,
        file_type=file_suffix.strip("."),
        raw_text=raw_text,
        parsed_data=parsed_data.model_dump(),
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)

    logger.info("Resume uploaded", resume_id=resume.id, filename=file.filename)
    return resume


@router.get("/", response_model=list[ResumeListItem])
async def list_resumes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    # Clean up file
    try:
        Path(resume.file_path).unlink(missing_ok=True)
    except Exception:
        pass
    await db.delete(resume)
