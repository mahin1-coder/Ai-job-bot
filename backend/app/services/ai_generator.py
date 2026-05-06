"""
AI Generator Service

Generates two artifacts per application:
  1. Tailored Resume — rewrites bullet points to mirror job description language
  2. Cover Letter    — personalised, 3-paragraph letter highlighting fit

Design decisions:
  - Uses streaming for real-time UX (SSE endpoint) but also supports non-streaming
  - Temperature 0.7 balances creativity with professionalism
  - Prompts are carefully engineered to avoid hallucination (facts come from the resume)
"""
import logging
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.resume import ParsedResume

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class AIGeneratorService:

    # ── Tailored Resume ───────────────────────────────────────────────────────
    async def generate_tailored_resume(
        self,
        parsed_resume: ParsedResume,
        job: dict,
        tone: str = "professional",
    ) -> str:
        """
        Rewrite resume bullet points to align with job description keywords.
        Returns plain-text resume (Markdown format for easy rendering).
        """
        prompt = self._tailored_resume_prompt(parsed_resume, job, tone)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert resume writer. "
                        "Tailor the candidate's resume to the target job without inventing experience. "
                        "Use strong action verbs and quantify achievements where possible. "
                        "Output clean Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()

    async def stream_tailored_resume(
        self,
        parsed_resume: ParsedResume,
        job: dict,
        tone: str = "professional",
    ) -> AsyncGenerator[str, None]:
        """Streaming version — use with SSE endpoint for real-time display."""
        prompt = self._tailored_resume_prompt(parsed_resume, job, tone)
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Output clean Markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    # ── Cover Letter ─────────────────────────────────────────────────────────
    async def generate_cover_letter(
        self,
        parsed_resume: ParsedResume,
        job: dict,
        tone: str = "professional",
    ) -> str:
        """
        Generate a 3-paragraph cover letter targeting the specific job.
        """
        prompt = self._cover_letter_prompt(parsed_resume, job, tone)
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional cover letter writer. "
                        "Write concise, compelling cover letters. "
                        "3 paragraphs: opening hook, value proposition, call to action. "
                        "Do not use clichés like 'I am writing to express my interest'. "
                        "Only use facts from the resume provided — never fabricate."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    async def stream_cover_letter(
        self,
        parsed_resume: ParsedResume,
        job: dict,
        tone: str = "professional",
    ) -> AsyncGenerator[str, None]:
        prompt = self._cover_letter_prompt(parsed_resume, job, tone)
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    # ── Prompt builders ───────────────────────────────────────────────────────
    def _tailored_resume_prompt(
        self, resume: ParsedResume, job: dict, tone: str
    ) -> str:
        experience_text = "\n".join(
            f"- {e.title} at {e.company} ({e.start_date} – {e.end_date or 'Present'})\n"
            f"  {e.description or ''}\n"
            + "\n".join(f"  • {a}" for a in e.achievements)
            for e in resume.experience
        )
        return f"""
Candidate Name: {resume.name or 'N/A'}
Current Summary: {resume.summary or 'N/A'}
Skills: {', '.join(resume.skills[:40])}
Experience:
{experience_text}
Education: {', '.join(f"{e.degree} from {e.institution}" for e in resume.education)}

TARGET JOB:
Title: {job.get('title')}
Company: {job.get('company')}
Description: {(job.get('description') or '')[:1500]}
Required skills: {', '.join(job.get('skills_required', [])[:20])}

TASK: Rewrite this resume tailored to the target job above.
Tone: {tone}
- Keep all facts accurate — do not invent experience
- Reorder and rephrase bullets to mirror job description language
- Emphasize relevant skills
- Format as clean Markdown with sections: Summary, Skills, Experience, Education
"""

    def _cover_letter_prompt(
        self, resume: ParsedResume, job: dict, tone: str
    ) -> str:
        top_experiences = resume.experience[:3]
        exp_summary = "; ".join(
            f"{e.title} at {e.company}" for e in top_experiences
        )
        return f"""
Candidate: {resume.name or 'N/A'}
Top experience: {exp_summary}
Key skills: {', '.join(resume.skills[:20])}
Summary: {resume.summary or 'N/A'}

TARGET JOB:
Title: {job.get('title')}
Company: {job.get('company')}
Description excerpt: {(job.get('description') or '')[:800]}

Write a {tone} cover letter for this application.
3 paragraphs max. No fluff. No clichés. Address the hiring manager.
"""


ai_generator_service = AIGeneratorService()
