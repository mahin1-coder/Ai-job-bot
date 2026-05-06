"""Text utility helpers used across the service layer."""
import re


def truncate(text: str, max_chars: int = 6000) -> str:
    """Truncate text to a token-safe length for OpenAI API calls."""
    return text[:max_chars] if len(text) > max_chars else text


def clean_whitespace(text: str) -> str:
    """Collapse multiple blank lines and strip trailing spaces."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def extract_emails(text: str) -> list[str]:
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def extract_phones(text: str) -> list[str]:
    pattern = r"(\+?1?\s?)?(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})"
    matches = re.findall(pattern, text)
    return ["".join(m).strip() for m in matches if "".join(m).strip()]


def extract_urls(text: str) -> list[str]:
    pattern = r"https?://[^\s\"\')>]+"
    return re.findall(pattern, text)
