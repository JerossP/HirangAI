"""
candidate_evaluator.py
──────────────────────
Orchestration layer that combines parsed resume data with job requirements
to produce a structured candidate evaluation report.

Public API
----------
evaluate_candidate(job_description, parsed_resume) -> EvaluationResult
    Run the full evaluation pipeline for a single candidate.
"""

from __future__ import annotations

import json
import logging
import os
import re
import traceback as _traceback
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv
from groq import (
    Groq,
    AuthenticationError,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
)

from resume_parser import ParsedResume
from prompts import (
    build_evaluation_prompt,
    SYSTEM_PROMPT,
    CATEGORY_KEYS,
    CATEGORY_WEIGHTS,
)
from ats_scorer import ATSResult, compute_ats_score

load_dotenv(override=True)  # reads .env with force override!

logger = logging.getLogger(__name__)

_GROQ_MODEL = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────────────────────────────────────────
# Recommendation scale  (0–100)
# ─────────────────────────────────────────────────────────────────────────────

_SCORE_TO_RECOMMENDATION: list[tuple[int, str]] = [
    (95, "Exceptional Candidate"),
    (90, "Outstanding Match"),
    (85, "Strong Hire"),
    (75, "Recommended"),
    (65, "Potential Fit"),
    (55, "Consider with Reservations"),
    (40, "Weak Match"),
    (0,  "Not Recommended"),
]


def _score_to_recommendation(score: int) -> str:
    """Derive the canonical recommendation label from a 0–100 score."""
    for threshold, label in _SCORE_TO_RECOMMENDATION:
        if score >= threshold:
            return label
    return "Not Recommended"


def _recommendation_to_midpoint(recommendation: str) -> int:
    """Return a reasonable midpoint score for a recommendation label."""
    midpoints = {
        "Exceptional Candidate":       98,
        "Outstanding Match":           92,
        "Strong Hire":                 87,
        "Recommended":                 80,
        "Potential Fit":               70,
        "Consider with Reservations":  60,
        "Weak Match":                  47,
        "Not Recommended":             25,
        # Legacy labels
        "Hire":                        78,
        "Maybe":                       60,
        "No Hire":                     25,
    }
    return midpoints.get(recommendation, 50)


def _calculate_weighted_score(category_scores: dict[str, int]) -> Optional[int]:
    """
    Compute the overall match score as a weighted average of category scores.

    Only includes categories that are present in the dict.  If no recognised
    categories are found, returns None.
    """
    total_weight = 0.0
    weighted_sum = 0.0
    for key, weight in CATEGORY_WEIGHTS.items():
        if key in category_scores:
            weighted_sum += category_scores[key] * weight
            total_weight += weight
    if total_weight == 0:
        return None
    return max(0, min(100, round(weighted_sum / total_weight)))


# ─────────────────────────────────────────────────────────────────────────────
# Data models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EvaluationResult:
    """Output of the candidate evaluation pipeline."""

    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    match_score: Optional[int] = None           # 0–100 weighted overall
    recommendation: Optional[str] = None
    confidence_level: Optional[str] = None      # High / Medium / Low
    category_scores: dict[str, int] = field(default_factory=dict)  # per-category 0–100
    strengths: list[str] = field(default_factory=list)
    skill_gaps: list[str] = field(default_factory=list)
    experience_summary: Optional[str] = None
    raw_llm_response: Optional[str] = None
    errors: list[str] = field(default_factory=list)
    # ATS Compatibility Score — computed deterministically after LLM evaluation
    ats_result: Optional[ATSResult] = None

    @property
    def is_complete(self) -> bool:
        return self.match_score is not None and self.recommendation is not None

    def to_dict(self) -> dict:
        return {
            "candidate_name":   self.candidate_name,
            "email":            self.email,
            "phone":            self.phone,
            "match_score":      self.match_score,
            "recommendation":   self.recommendation,
            "confidence_level": self.confidence_level,
            "category_scores":  self.category_scores,
            "strengths":        self.strengths,
            "skill_gaps":       self.skill_gaps,
            "experience_summary": self.experience_summary,
            "raw_llm_response": self.raw_llm_response,
            "errors":           self.errors,
            "ats_score":        self.ats_result.ats_score if self.ats_result else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# LLM call
# ─────────────────────────────────────────────────────────────────────────────

def _call_llm(prompt: str) -> str:
    """
    Call the Groq Chat Completions API with the given prompt.

    Raises
    ------
    EnvironmentError  — GROQ_API_KEY missing or empty.
    PermissionError   — API key invalid / rejected.
    ConnectionError   — Cannot reach the Groq API.
    TimeoutError      — Request timed out.
    RuntimeError      — Any other API-level error.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file and restart the app."
        )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2500,
        )
        return response.choices[0].message.content

    except AuthenticationError as exc:
        raise PermissionError(
            "Invalid GROQ_API_KEY — check your .env file and make sure the key "
            "is active in the Groq console."
        ) from exc

    except APITimeoutError as exc:
        raise TimeoutError(
            "The Groq API request timed out. "
            "Check your internet connection and try again."
        ) from exc

    except APIConnectionError as exc:
        raise ConnectionError(
            f"Could not reach the Groq API: {exc}. "
            "Check your internet connection."
        ) from exc

    except APIStatusError as exc:
        raise RuntimeError(
            f"Groq API returned an error (HTTP {exc.status_code}): {exc.message}"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Response parsing
# ─────────────────────────────────────────────────────────────────────────────

def _parse_llm_response(response: str, result: EvaluationResult) -> None:
    """
    Parse structured fields from the raw LLM markdown response.

    Extraction strategy (in priority order):
    1. JSON SCORE_BLOCK  — most reliable; parses all fields atomically
    2. Regex fallback    — handles free-form markdown for missing fields
    3. Derivation        — fill any remaining gaps from sister fields
    """
    result.raw_llm_response = response

    # ── Strategy 1: structured SCORE_BLOCK ───────────────────────────────────
    _extract_score_block(response, result)

    # ── Strategy 2: regex fallback for missing scalar fields ─────────────────
    if result.match_score is None:
        _extract_score_regex(response, result)

    if result.recommendation is None:
        _extract_recommendation_regex(response, result)

    if result.confidence_level is None:
        _extract_confidence_regex(response, result)

    # Regex fallback for any missing category scores
    if len(result.category_scores) < len(CATEGORY_KEYS):
        _extract_category_scores_regex(response, result)

    # ── Strategy 3: recalculate overall from categories if we have them ───────
    if result.category_scores:
        weighted = _calculate_weighted_score(result.category_scores)
        if weighted is not None:
            # Use weighted score as ground truth; override LLM's stated score
            result.match_score = weighted

    # ── Strategy 4: cross-derive recommendation ↔ score ──────────────────────
    if result.recommendation is None and result.match_score is not None:
        result.recommendation = _score_to_recommendation(result.match_score)

    if result.match_score is None and result.recommendation is not None:
        result.match_score = _recommendation_to_midpoint(result.recommendation)

    # ── Defaults ──────────────────────────────────────────────────────────────
    if result.confidence_level is None:
        result.confidence_level = "Medium"

    # ── Narrative sections ────────────────────────────────────────────────────
    _extract_strengths(response, result)
    _extract_skill_gaps(response, result)
    _extract_experience_summary(response, result)


def _extract_score_block(response: str, result: EvaluationResult) -> None:
    """Parse the machine-readable SCORE_BLOCK JSON from the LLM response."""
    # Try fenced code block first
    block_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        response,
        re.DOTALL | re.IGNORECASE,
    )
    if not block_match:
        # Bare JSON object fallback
        block_match = re.search(
            r'(\{\s*"match_score"\s*:.*?\})',
            response,
            re.DOTALL,
        )
    if not block_match:
        return

    try:
        data = json.loads(block_match.group(1))
    except (json.JSONDecodeError, ValueError):
        return

    raw_score = data.get("match_score")
    if isinstance(raw_score, (int, float)):
        result.match_score = max(0, min(100, int(raw_score)))

    raw_rec = data.get("recommendation", "")
    if isinstance(raw_rec, str) and raw_rec.strip():
        result.recommendation = raw_rec.strip()

    raw_conf = data.get("confidence", "") or data.get("confidence_level", "")
    if isinstance(raw_conf, str) and raw_conf.strip():
        conf = raw_conf.strip().capitalize()
        if conf in ("High", "Medium", "Low"):
            result.confidence_level = conf

    # Category scores from SCORE_BLOCK
    raw_cats = data.get("category_scores", {})
    if isinstance(raw_cats, dict):
        for key in CATEGORY_KEYS:
            raw_val = raw_cats.get(key)
            if isinstance(raw_val, (int, float)):
                result.category_scores[key] = max(0, min(100, int(raw_val)))


def _extract_score_regex(response: str, result: EvaluationResult) -> None:
    """Regex extraction for match score (0–100)."""
    patterns = [
        r"[Ss]core\s*[:\-–]\s*(\d{1,3})",
        r"[Oo]verall\s+[Mm]atch\s+[Ss]core.*?(\d{1,3})",
        r"[Mm]atch\s+[Ss]core.*?(\d{1,3})",
        r"(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s+out\s+of\s+100",
    ]
    for pattern in patterns:
        m = re.search(pattern, response)
        if m:
            score = int(m.group(1))
            if 0 <= score <= 100:
                result.match_score = score
                return
            if 0 <= score <= 10:
                result.match_score = score * 10
                return


def _extract_recommendation_regex(response: str, result: EvaluationResult) -> None:
    """Regex extraction for recommendation label."""
    bold_pattern = re.search(
        r"\*\*(Exceptional Candidate|Outstanding Match|Strong Hire|Recommended|"
        r"Potential Fit|Consider with Reservations|Weak Match|Not Recommended)\*\*",
        response,
        re.IGNORECASE,
    )
    if bold_pattern:
        result.recommendation = bold_pattern.group(1)
        return
    plain_pattern = re.search(
        r"\b(Exceptional Candidate|Outstanding Match|Strong Hire|Recommended|"
        r"Potential Fit|Consider with Reservations|Weak Match|Not Recommended)\b",
        response,
        re.IGNORECASE,
    )
    if plain_pattern:
        result.recommendation = plain_pattern.group(1)


def _extract_confidence_regex(response: str, result: EvaluationResult) -> None:
    """Regex extraction for confidence level."""
    m = re.search(
        r"[Cc]onfidence\s*[:\-–]\s*(High|Medium|Low)",
        response,
        re.IGNORECASE,
    )
    if m:
        result.confidence_level = m.group(1).capitalize()


# Mapping from the human-readable category label used in prompts → internal key
_CATEGORY_LABEL_TO_KEY: dict[str, str] = {
    "technical skills":            "technical_skills",
    "relevant experience":         "relevant_experience",
    "education":                   "education",
    "certifications":              "certifications",
    "communication & soft skills": "communication_soft_skills",
    "communication and soft skills": "communication_soft_skills",
    "communication":               "communication_soft_skills",
    "soft skills":                 "communication_soft_skills",
}


def _extract_category_scores_regex(response: str, result: EvaluationResult) -> None:
    """
    Regex fallback to extract per-category scores from the prose section.

    Matches patterns like:
      - **Technical Skills** (score 92/100)
      - Technical Skills: 92
      - Technical Skills — 88/100
    """
    pattern = re.compile(
        r"\*?\*?(Technical Skills|Relevant Experience|Education|Certifications|"
        r"Communication\s*(?:&|and)\s*Soft Skills|Communication|Soft Skills)"
        r"\*?\*?"
        r"[\s\S]{0,60}?"          # allow short label/punctuation gap
        r"(?:score\s+)?(\d{1,3})" # the score digits
        r"(?:\s*/\s*100)?",        # optional /100
        re.IGNORECASE,
    )
    for m in pattern.finditer(response):
        label = m.group(1).strip().lower()
        key = _CATEGORY_LABEL_TO_KEY.get(label)
        if key and key not in result.category_scores:
            score = int(m.group(2))
            if 0 <= score <= 100:
                result.category_scores[key] = score


def _extract_strengths(response: str, result: EvaluationResult) -> None:
    block = re.search(
        r"Key Strengths\s*\n(.*?)(?=###|\Z)", response, re.DOTALL | re.IGNORECASE
    )
    if block:
        result.strengths = [
            line.lstrip("-•* ").strip()
            for line in block.group(1).splitlines()
            if line.strip().startswith(("-", "•", "*"))
        ]


def _extract_skill_gaps(response: str, result: EvaluationResult) -> None:
    block = re.search(
        r"Skill Gaps\s*\n(.*?)(?=###|\Z)", response, re.DOTALL | re.IGNORECASE
    )
    if block:
        result.skill_gaps = [
            line.lstrip("-•* ").strip()
            for line in block.group(1).splitlines()
            if line.strip().startswith(("-", "•", "*"))
        ]


def _extract_experience_summary(response: str, result: EvaluationResult) -> None:
    block = re.search(
        r"Experience Summary\s*\n(.*?)(?=###|\Z)", response, re.DOTALL | re.IGNORECASE
    )
    if block:
        result.experience_summary = block.group(1).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_candidate(
    job_description: str,
    parsed_resume: ParsedResume,
) -> EvaluationResult:
    """
    Run the full evaluation pipeline for a single candidate.

    Returns
    -------
    EvaluationResult
        Structured evaluation report.  Always returned — never None.
    """
    result = EvaluationResult(
        candidate_name=parsed_resume.candidate_name,
        email=parsed_resume.email,
        phone=parsed_resume.phone,
    )

    if not parsed_resume.is_valid:
        result.errors.append("Resume text could not be extracted from the PDF.")
        return result

    if not job_description.strip():
        result.errors.append("Job description is empty.")
        return result

    # ── ATS Compatibility Score (deterministic — runs before LLM) ────────────
    result.ats_result = compute_ats_score(job_description, parsed_resume)

    prompt = build_evaluation_prompt(
        job_description=job_description,
        resume_text=parsed_resume.raw_text,
    )

    try:
        llm_response = _call_llm(prompt)
        _parse_llm_response(llm_response, result)
    except EnvironmentError as exc:
        logger.error("Missing API key: %s", exc)
        result.errors.append(f"Configuration error: {exc}")
    except PermissionError as exc:
        logger.error("Invalid API key: %s", exc)
        result.errors.append(f"Authentication error: {exc}")
    except TimeoutError as exc:
        logger.error("Groq request timed out: %s", exc)
        result.errors.append(f"Timeout: {exc}")
    except ConnectionError as exc:
        logger.error("Groq connection failed: %s", exc)
        result.errors.append(f"Connection error: {exc}")
    except RuntimeError as exc:
        logger.error("Groq API error: %s", exc)
        result.errors.append(f"API error: {exc}")
    except Exception as exc:
        tb = _traceback.format_exc()
        logger.error("Unexpected error during evaluation:\n%s", tb)
        result.errors.append(f"Unexpected error: {exc}")

    return result
