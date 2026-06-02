"""
resume_parser.py
────────────────
Handles PDF ingestion and raw text extraction for HirangAI.

Public API
----------
parse_resume(file_bytes: bytes) -> dict
    Extract text and metadata from a PDF resume.

NOTE: AI integration is not yet implemented.  This module handles only
      the extraction layer; semantic analysis lives in candidate_evaluator.py.
"""

from __future__ import annotations

import io
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ParsedResume:
    """Structured representation of an extracted resume."""

    raw_text: str = ""
    page_count: int = 0
    word_count: int = 0
    # Heuristically detected fields (populated by _extract_heuristics)
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sections: dict[str, str] = field(default_factory=dict)
    parsing_errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True if at least some text was extracted."""
        return bool(self.raw_text.strip())

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "phone": self.phone,
            "sections": self.sections,
            "parsing_errors": self.parsing_errors,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")

_SECTION_HEADERS = [
    "experience", "work experience", "employment",
    "education", "qualifications",
    "skills", "technical skills", "core competencies",
    "projects", "certifications", "awards",
    "summary", "objective", "profile",
    "languages", "publications", "references",
]


def _extract_heuristics(resume: ParsedResume) -> None:
    """Populate structured fields via lightweight regex heuristics."""
    text = resume.raw_text

    # Email
    email_match = _EMAIL_RE.search(text)
    if email_match:
        resume.email = email_match.group()

    # Phone
    phone_match = _PHONE_RE.search(text)
    if phone_match:
        resume.phone = phone_match.group().strip()

    # Candidate name — first non-empty line heuristic
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 5 and not _EMAIL_RE.search(line):
            resume.candidate_name = line
            break

    # Sections
    lines = text.splitlines()
    current_section: Optional[str] = None
    buffer: list[str] = []

    for line in lines:
        lower = line.strip().lower().rstrip(":")
        if lower in _SECTION_HEADERS:
            if current_section and buffer:
                resume.sections[current_section] = "\n".join(buffer).strip()
            current_section = lower
            buffer = []
        else:
            if current_section:
                buffer.append(line)

    if current_section and buffer:
        resume.sections[current_section] = "\n".join(buffer).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def parse_resume(file_bytes: bytes) -> ParsedResume:
    """
    Extract text and metadata from a PDF resume.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the uploaded PDF file.

    Returns
    -------
    ParsedResume
        Structured object containing extracted text and heuristic fields.
    """
    resume = ParsedResume()

    try:
        import pdfplumber  # lazy import — keeps startup fast

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            resume.page_count = len(pdf.pages)
            pages_text: list[str] = []

            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                    pages_text.append(page_text)
                except Exception as exc:
                    msg = f"Failed to extract text from page {page_num}: {exc}"
                    logger.warning(msg)
                    resume.parsing_errors.append(msg)

            resume.raw_text = "\n".join(pages_text)
            resume.word_count = len(resume.raw_text.split())

    except ImportError:
        msg = "pdfplumber is not installed. Run: pip install pdfplumber"
        logger.error(msg)
        resume.parsing_errors.append(msg)
    except Exception as exc:
        msg = f"Unexpected error during PDF parsing: {exc}"
        logger.error(msg)
        resume.parsing_errors.append(msg)

    if resume.is_valid:
        _extract_heuristics(resume)

    return resume
