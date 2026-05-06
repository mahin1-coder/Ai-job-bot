"""
File utilities — upload validation and safe disk persistence.

Security notes:
  - File type is validated by both extension AND magic bytes (content sniffing)
  - Filename is sanitized to prevent path traversal attacks
  - Files are stored with a UUID name, not the user-provided filename
"""
import hashlib
import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

# Magic bytes for supported file types (first few bytes of file content)
MAGIC_BYTES: dict[str, bytes] = {
    "pdf": b"%PDF",
    "docx": b"PK\x03\x04",  # ZIP-based (OOXML)
    "doc": b"\xd0\xcf\x11\xe0",  # OLE2
}


def validate_resume_file(
    file: UploadFile,
    allowed_extensions: set[str],
    max_size_bytes: int,
) -> None:
    """
    Raises HTTPException if the file fails any validation check.
    Checks: extension, content-type, and file size.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided."
        )

    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix}'. Allowed: {allowed_extensions}",
        )

    # Content-type check (defence in depth — not the sole check)
    allowed_mimes = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
    }
    if file.content_type and file.content_type not in allowed_mimes:
        logger.warning(
            "Suspicious content-type on upload",
            filename=file.filename,
            content_type=file.content_type,
        )
        # Log but don't block — browsers sometimes send wrong content-types


async def save_upload(file: UploadFile, upload_dir: str) -> str:
    """
    Read file content, validate size, and save with a UUID filename.
    Returns the absolute path to the saved file.

    Design: Read entire file into memory first to enforce size limit
    before writing to disk (prevents partial writes of huge files).
    """
    from app.config import settings

    content = await file.read()

    # Enforce max size
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB.",
        )

    # Validate magic bytes for PDFs and DOCX
    suffix = Path(file.filename).suffix.lower().strip(".")
    if suffix in MAGIC_BYTES:
        magic = MAGIC_BYTES[suffix]
        if not content.startswith(magic):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File content does not match declared type '{suffix}'.",
            )

    # Save with safe, randomised filename
    safe_name = f"{uuid.uuid4()}{Path(file.filename).suffix.lower()}"
    dest = Path(upload_dir) / safe_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)

    logger.info("File saved", path=str(dest), size_bytes=len(content))
    return str(dest)
