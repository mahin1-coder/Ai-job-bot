"""
Job Matcher Service

Algorithm:
  1. Embed the resume's skills + experience text using OpenAI embeddings
  2. Embed each job's title + description
  3. Compute cosine similarity → match_score (0.0 – 1.0)
  4. Use GPT-4o to generate human-readable match reasons and missing skills

Design decision: Embeddings give semantic matching (e.g. "React" matches "ReactJS"),
while GPT-4o explains WHY the match is good/bad — useful for the user.

In production: Store embeddings in pgvector for sub-millisecond similarity search
over millions of jobs. For now we compute similarity in-memory.
"""
import logging
from dataclasses import dataclass

import numpy as np
from openai import AsyncOpenAI

from app.config import settings
from app.schemas.resume import ParsedResume

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


@dataclass
class MatchResult:
    job_id: str
    match_score: float
    match_reasons: list[str]
    missing_skills: list[str]


class JobMatcherService:
    """Ranks job listings by semantic similarity to a resume."""

    async def match_resume_to_jobs(
        self,
        parsed_resume: ParsedResume,
        jobs: list[dict],
        top_k: int = 20,
    ) -> list[MatchResult]:
        """
        Main entry point. Returns jobs ranked by match score.
        """
        if not jobs:
            return []

        resume_text = self._build_resume_text(parsed_resume)
        resume_embedding = await self._embed(resume_text)

        # Embed all jobs concurrently (batched to respect rate limits)
        job_texts = [self._build_job_text(j) for j in jobs]
        job_embeddings = await self._embed_batch(job_texts)

        results: list[MatchResult] = []
        for job, job_emb in zip(jobs, job_embeddings):
            score = self._cosine_similarity(resume_embedding, job_emb)
            result = MatchResult(
                job_id=job.get("source_job_id", ""),
                match_score=round(float(score), 4),
                match_reasons=[],
                missing_skills=[],
            )
            results.append(result)

        # Sort by score descending
        results.sort(key=lambda r: r.match_score, reverse=True)
        top_results = results[:top_k]

        # Enrich top 5 with GPT-4o reasoning (avoid excessive API calls)
        for result, job in zip(top_results[:5], jobs[:5]):
            reasons, missing = await self._explain_match(parsed_resume, job, result.match_score)
            result.match_reasons = reasons
            result.missing_skills = missing

        return top_results

    # ── Text builders ─────────────────────────────────────────────────────────
    def _build_resume_text(self, resume: ParsedResume) -> str:
        parts = []
        if resume.summary:
            parts.append(resume.summary)
        if resume.skills:
            parts.append("Skills: " + ", ".join(resume.skills))
        for exp in resume.experience:
            parts.append(f"{exp.title} at {exp.company}. {exp.description or ''}")
            parts.extend(exp.achievements)
        return "\n".join(parts)[:6000]

    def _build_job_text(self, job: dict) -> str:
        parts = [job.get("title", ""), job.get("company", "")]
        if job.get("description"):
            parts.append(job["description"])
        if job.get("skills_required"):
            parts.append("Required: " + ", ".join(job["skills_required"]))
        return "\n".join(parts)[:6000]

    # ── Embedding ─────────────────────────────────────────────────────────────
    async def _embed(self, text: str) -> list[float]:
        resp = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text[:8192],
        )
        return resp.data[0].embedding

    async def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed up to 100 texts in one API call (OpenAI supports batching)."""
        if not texts:
            return []
        resp = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=[t[:8192] for t in texts],
        )
        # Results are returned in the same order as input
        return [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]

    # ── Similarity ────────────────────────────────────────────────────────────
    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        va = np.array(a)
        vb = np.array(b)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)

    # ── GPT-4o explanation ────────────────────────────────────────────────────
    async def _explain_match(
        self,
        resume: ParsedResume,
        job: dict,
        score: float,
    ) -> tuple[list[str], list[str]]:
        """Generate bullet-point reasons + missing skills for a match."""
        prompt = f"""
Resume skills: {', '.join(resume.skills[:30])}
Resume experience titles: {', '.join(e.title for e in resume.experience[:5])}

Job title: {job.get('title')}
Job required skills: {', '.join(job.get('skills_required', [])[:20])}
Job description (excerpt): {(job.get('description') or '')[:500]}

Match score: {score:.0%}

List 3 reasons why this is a good/bad match, then list up to 5 skills the candidate is missing.
Return JSON: {{"reasons": ["..."], "missing_skills": ["..."]}}
"""
        try:
            resp = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            import json
            data = json.loads(resp.choices[0].message.content)
            return data.get("reasons", []), data.get("missing_skills", [])
        except Exception as e:
            logger.warning("Match explanation failed", error=str(e))
            return [], []


job_matcher_service = JobMatcherService()
