"""
Applications Router — tracks every job application attempt.

POST /api/v1/applications/              → create application record
GET  /api/v1/applications/              → list all (dashboard)
GET  /api/v1/applications/stats         → summary stats
GET  /api/v1/applications/{id}          → single record
PATCH /api/v1/applications/{id}/status  → update status
DELETE /api/v1/applications/{id}        → delete
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.application import ApplicationStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.services.application_tracker import application_tracker_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
):
    app = await application_tracker_service.create(
        db=db,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
    )
    return app


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    return await application_tracker_service.get_stats(db)


@router.get("/", response_model=list[ApplicationResponse])
async def list_applications(db: AsyncSession = Depends(get_db)):
    return await application_tracker_service.get_all(db)


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, db: AsyncSession = Depends(get_db)):
    app = await application_tracker_service.get_by_id(db, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str,
    payload: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    app = await application_tracker_service.update_status(
        db=db,
        application_id=application_id,
        status=payload.status,
        notes=payload.notes,
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await application_tracker_service.delete(db, application_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
