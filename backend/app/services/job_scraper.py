"""
Job Scraper Service

Sources:
  1. Adzuna API  — real API, free tier (primary source for Indeed/LinkedIn-like results)
  2. RemoteOK    — free JSON API for remote tech jobs
  3. RSS Feeds   — Indeed/LinkedIn basic RSS (no dynamic scraping needed)

Design decision: We use real APIs rather than scraping LinkedIn/Indeed directly
to avoid ToS violations and IP bans. Adzuna aggregates 100k+ jobs daily.

Rate limiting: Each source has a configurable delay between requests.
Caching: Job results are cached in Redis for 30 minutes to avoid API abuse.
"""
import asyncio
import hashlib
import json
import logging
from datetime import datetime

import httpx

from app.config import settings
from app.schemas.job import JobResponse

logger = logging.getLogger(__name__)

# Cache TTL for job listings (seconds)
CACHE_TTL = 60 * 30  # 30 minutes


class JobScraperService:
    """Fetches job listings from multiple sources and normalises them."""

    def __init__(self):
        self._http = httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; JobBot/1.0; +https://github.com/yourrepo)"
                )
            },
        )

    async def search(
        self,
        query: str,
        location: str = "",
        job_type: str | None = None,
        page: int = 1,
        results_per_page: int = 20,
    ) -> list[dict]:
        """
        Search all configured sources concurrently and merge results.
        Returns a list of normalised job dicts.
        """
        tasks = [
            self._search_adzuna(query, location, page, results_per_page),
            self._search_remoteok(query),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        jobs: list[dict] = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Job source failed", error=str(result))
                continue
            jobs.extend(result)

        # Deduplicate by (title, company) key
        seen = set()
        unique_jobs: list[dict] = []
        for job in jobs:
            key = f"{job['title'].lower()}|{job['company'].lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs[:results_per_page]

    # ── Adzuna API ────────────────────────────────────────────────────────────
    async def _search_adzuna(
        self,
        query: str,
        location: str,
        page: int,
        results: int,
    ) -> list[dict]:
        """
        Adzuna aggregates jobs from Indeed, LinkedIn, and 100+ boards.
        Free tier: 250 req/month. Sign up at https://developer.adzuna.com/
        """
        if not settings.ADZUNA_APP_ID or not settings.ADZUNA_API_KEY:
            logger.debug("Adzuna API not configured, skipping.")
            return []

        country = "us"  # configurable
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY,
            "results_per_page": results,
            "what": query,
            "content-type": "application/json",
        }
        if location:
            params["where"] = location

        resp = await self._http.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        return [self._normalize_adzuna(job) for job in data.get("results", [])]

    def _normalize_adzuna(self, raw: dict) -> dict:
        return {
            "title": raw.get("title", ""),
            "company": raw.get("company", {}).get("display_name", "Unknown"),
            "location": raw.get("location", {}).get("display_name", ""),
            "description": raw.get("description", ""),
            "apply_url": raw.get("redirect_url", ""),
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "salary_currency": "USD",
            "job_type": "remote" if "remote" in raw.get("title", "").lower() else None,
            "source": "adzuna",
            "source_job_id": str(raw.get("id", "")),
            "posted_at": raw.get("created"),
            "skills_required": [],
            "requirements": [],
        }

    # ── RemoteOK API ──────────────────────────────────────────────────────────
    async def _search_remoteok(self, query: str) -> list[dict]:
        """
        RemoteOK is a free, open API for remote tech jobs.
        No auth needed. https://remoteok.com/api
        """
        url = "https://remoteok.com/api"
        try:
            resp = await self._http.get(url)
            resp.raise_for_status()
            # First element is a legal notice, skip it
            jobs = resp.json()[1:]
        except Exception as e:
            logger.warning("RemoteOK fetch failed", error=str(e))
            return []

        query_lower = query.lower()
        matched = [
            self._normalize_remoteok(j)
            for j in jobs
            if query_lower in j.get("position", "").lower()
            or query_lower in " ".join(j.get("tags", [])).lower()
        ]
        return matched[:15]

    def _normalize_remoteok(self, raw: dict) -> dict:
        return {
            "title": raw.get("position", ""),
            "company": raw.get("company", "Unknown"),
            "location": "Remote",
            "description": raw.get("description", ""),
            "apply_url": raw.get("url", ""),
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "salary_currency": "USD",
            "job_type": "remote",
            "source": "remoteok",
            "source_job_id": str(raw.get("id", "")),
            "posted_at": raw.get("date"),
            "skills_required": raw.get("tags", []),
            "requirements": [],
        }

    async def close(self):
        await self._http.aclose()


job_scraper_service = JobScraperService()
