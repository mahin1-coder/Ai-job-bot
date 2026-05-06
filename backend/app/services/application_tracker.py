"""
Application Tracker Service

Handles CRUD operations for job applications and status transitions.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus

logger = logging.getLogger(__name__)


class ApplicationTrackerService:

    async def create(
        self,
        db: AsyncSession,
        resume_id: str,
        job_id: str,
        match_score: float | None = None,
        match_reasons: list[str] | None = None,
        missing_skills: list[str] | None = None,
    ) -> Application:
        application = Application(
            resume_id=resume_id,
            job_id=job_id,
            match_score=match_score,
            match_reasons=match_reasons or [],
            missing_skills=missing_skills or [],
            status=ApplicationStatus.PENDING,
        )
        db.add(application)
        await db.flush()  # get ID without committing
        await db.refresh(application)
        logger.info("Application created", application_id=application.id)
        return application

    async def get_all(self, db: AsyncSession, limit: int = 100) -> list[Application]:
        result = await db.execute(
            select(Application).order_by(Application.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, application_id: str) -> Application | None:
        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        db: AsyncSession,
        application_id: str,
        status: ApplicationStatus,
        notes: str | None = None,
    ) -> Application | None:
        application = await self.get_by_id(db, application_id)
        if not application:
            return None
        application.status = status
        if notes:
            application.notes = notes
        if status == ApplicationStatus.APPLIED:
            application.applied_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(application)
        return application

    async def save_artifacts(
        self,
        db: AsyncSession,
        application_id: str,
        tailored_resume: str,
        cover_letter: str,
    ) -> Application | None:
        application = await self.get_by_id(db, application_id)
        if not application:
            return None
        application.tailored_resume = tailored_resume
        application.cover_letter = cover_letter
        await db.flush()
        await db.refresh(application)
        return application

    async def delete(self, db: AsyncSession, application_id: str) -> bool:
        application = await self.get_by_id(db, application_id)
        if not application:
            return False
        await db.delete(application)
        return True

    async def get_stats(self, db: AsyncSession) -> dict:
        """Dashboard summary stats."""
        apps = await self.get_all(db, limit=10000)
        stats: dict[str, int] = {}
        for app in apps:
            stats[app.status] = stats.get(app.status, 0) + 1
        return {
            "total": len(apps),
            "by_status": stats,
        }


application_tracker_service = ApplicationTrackerService()
