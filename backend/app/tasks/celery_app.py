"""
Celery configuration and task definitions.

Tasks:
  - scrape_jobs_task: Background job scraping
  - generate_artifacts_task: Background AI resume + cover letter generation
  - cleanup_old_jobs_task: Periodic cleanup of stale job listings
"""
from celery import Celery

from app.config import settings

# Create Celery app
celery_app = Celery(
    "job_bot_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    result_expires=3600,  # Results expire after 1 hour
)


@celery_app.task(name="scrape_jobs")
def scrape_jobs_task(query: str, location: str = "", results_per_page: int = 50):
    """
    Background task: Scrape jobs from all sources and save to DB.
    Returns the number of jobs scraped.
    """
    import asyncio
    from app.services.job_scraper import job_scraper_service
    from app.database import AsyncSessionLocal
    from app.models.job import Job

    async def run():
        raw_jobs = await job_scraper_service.search(
            query=query,
            location=location,
            results_per_page=results_per_page,
        )
        
        saved_count = 0
        async with AsyncSessionLocal() as db:
            for raw in raw_jobs:
                # Check if job already exists
                from sqlalchemy import select
                result = await db.execute(
                    select(Job).where(
                        Job.source == raw["source"],
                        Job.source_job_id == raw["source_job_id"],
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    job = Job(**{k: v for k, v in raw.items() if hasattr(Job, k)})
                    db.add(job)
                    saved_count += 1
            
            await db.commit()
        
        return saved_count

    return asyncio.run(run())


@celery_app.task(name="generate_artifacts")
def generate_artifacts_task(application_id: str, tone: str = "professional"):
    """
    Background task: Generate tailored resume + cover letter for an application.
    Returns True on success.
    """
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.application import Application
    from app.models.resume import Resume
    from app.models.job import Job
    from app.schemas.resume import ParsedResume
    from app.services.ai_generator import ai_generator_service
    from app.services.application_tracker import application_tracker_service

    async def run():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            
            # Load application + resume + job
            result = await db.execute(
                select(Application).where(Application.id == application_id)
            )
            app = result.scalar_one_or_none()
            if not app:
                return False

            resume_result = await db.execute(select(Resume).where(Resume.id == app.resume_id))
            resume = resume_result.scalar_one_or_none()
            if not resume or not resume.parsed_data:
                return False

            job_result = await db.execute(select(Job).where(Job.id == app.job_id))
            job = job_result.scalar_one_or_none()
            if not job:
                return False

            parsed_resume = ParsedResume(**resume.parsed_data)
            job_dict = {
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "skills_required": job.skills_required or [],
            }

            # Generate both artifacts concurrently
            tailored_resume, cover_letter = await asyncio.gather(
                ai_generator_service.generate_tailored_resume(parsed_resume, job_dict, tone),
                ai_generator_service.generate_cover_letter(parsed_resume, job_dict, tone),
            )

            # Save to DB
            await application_tracker_service.save_artifacts(
                db=db,
                application_id=application_id,
                tailored_resume=tailored_resume,
                cover_letter=cover_letter,
            )
            await db.commit()

        return True

    return asyncio.run(run())


@celery_app.task(name="cleanup_old_jobs")
def cleanup_old_jobs_task(days_old: int = 30):
    """
    Periodic task: Delete job listings older than X days.
    Returns the number of jobs deleted.
    """
    import asyncio
    from datetime import datetime, timedelta, timezone
    from app.database import AsyncSessionLocal
    from app.models.job import Job

    async def run():
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        async with AsyncSessionLocal() as db:
            from sqlalchemy import delete
            result = await db.execute(
                delete(Job).where(Job.scraped_at < cutoff).returning(Job.id)
            )
            deleted_ids = result.scalars().all()
            await db.commit()
        return len(deleted_ids)

    return asyncio.run(run())


# Periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    "cleanup-old-jobs-weekly": {
        "task": "cleanup_old_jobs",
        "schedule": 60 * 60 * 24 * 7,  # Every 7 days
        "args": (30,),
    },
}
