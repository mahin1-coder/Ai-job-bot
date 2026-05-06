"""
Resume Parser Service

Pipeline:
  1. Extract raw text from PDF / DOCX / TXT
  2. Send raw text to OpenAI with a structured output prompt
  3. Return a ParsedResume object

Design decision: We use OpenAI for structuring instead of regex/spaCy because
real-world resumes have wildly inconsistent formats. GPT-4o handles all of them.
"""
import json
import logging
from pathlib import Path

import pdfplumber
import fitz  # PyMuPDF fallback
from docx import Document
from openai import AsyncOpenAI

from app.config import settings
from app.schemas.resume import ParsedResume

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# ── Structured output schema passed to OpenAI ────────────────────────────────
RESUME_EXTRACTION_PROMPT = """
You are a resume parser. Extract structured data from the resume text below.
Return ONLY valid JSON matching this exact schema — no markdown, no explanation:

{
  "name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "string or null",
      "end_date": "string or null",
      "description": "string or null",
      "achievements": ["string", ...]
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string or null",
      "field": "string or null",
      "graduation_year": "string or null"
    }
  ],
  "certifications": ["string", ...],
  "languages": ["string", ...]
}

Resume text:
"""


class ResumeParserService:
    """Handles file reading and AI-powered structuring of resume data."""

    # ── Public API ────────────────────────────────────────────────────────────
    async def parse(self, file_path: str, file_type: str) -> tuple[str, ParsedResume]:
        """
        Extract text from file then parse into structured data.
        Returns (raw_text, ParsedResume).
        """
        raw_text = self._extract_text(file_path, file_type)
        parsed = await self._structure_with_ai(raw_text)
        return raw_text, parsed

    # ── Text extraction ───────────────────────────────────────────────────────
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Route to the appropriate extractor based on file type."""
        ext = file_type.lower().strip(".")
        if ext == "pdf":
            return self._extract_pdf(file_path)
        elif ext in ("docx", "doc"):
            return self._extract_docx(file_path)
        else:
            return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    def _extract_pdf(self, file_path: str) -> str:
        """
        Primary: pdfplumber (better layout preservation).
        Fallback: PyMuPDF (fitz) for scanned or complex PDFs.
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages).strip()
                if text:
                    return text
        except Exception as e:
            logger.warning("pdfplumber failed, trying PyMuPDF", error=str(e))

        # Fallback: PyMuPDF
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()

    def _extract_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    # ── AI structuring ────────────────────────────────────────────────────────
    async def _structure_with_ai(self, raw_text: str) -> ParsedResume:
        """Send raw text to OpenAI and parse the JSON response."""
        if not raw_text.strip():
            logger.warning("Empty resume text, returning empty ParsedResume")
            return ParsedResume()

        # Truncate to ~6000 words to stay within token limits
        truncated = raw_text[:24000]

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise resume parser. Output only valid JSON.",
                    },
                    {"role": "user", "content": RESUME_EXTRACTION_PROMPT + truncated},
                ],
                temperature=0,  # deterministic output for parsing
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            return ParsedResume(**data)
        except Exception as e:
            logger.error("AI resume parsing failed", error=str(e))
            # Return partially-parsed result rather than failing the whole upload
            return ParsedResume(raw_text=truncated[:500])  # type: ignore[call-arg]


# Singleton to avoid re-instantiating the client on every request
resume_parser_service = ResumeParserService()
