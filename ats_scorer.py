"""
ats_scorer.py
─────────────
Deterministic ATS Compatibility Scorer for HirangAI.

No LLM calls — scoring is purely regex/heuristic, mirroring how real
Applicant Tracking Systems perform keyword and structure matching.

Public API
----------
compute_ats_score(job_description, parsed_resume) -> ATSResult
    Produce an ATS compatibility score (0–100) and a full breakdown.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from resume_parser import ParsedResume

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# ATS Score interpretation labels
# ─────────────────────────────────────────────────────────────────────────────

_ATS_LABELS: list[tuple[int, str]] = [
    (90, "Excellent ATS Match"),
    (80, "Strong ATS Match"),
    (70, "Good ATS Match"),
    (60, "Moderate ATS Match"),
    (0,  "Low ATS Match"),
]


def _ats_label(score: int) -> str:
    for threshold, label in _ATS_LABELS:
        if score >= threshold:
            return label
    return "Low ATS Match"


# ─────────────────────────────────────────────────────────────────────────────
# Component weights (must sum to 1.0)
# ─────────────────────────────────────────────────────────────────────────────

_WEIGHT_REQUIRED_KW  = 0.40
_WEIGHT_PREFERRED_KW = 0.20
_WEIGHT_EXPERIENCE   = 0.20
_WEIGHT_EDUCATION    = 0.10
_WEIGHT_COMPLETENESS = 0.10


# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ATSResult:
    """Full ATS compatibility analysis for a single candidate."""

    ats_score: int = 0                                   # 0–100 composite
    ats_label: str = "Low ATS Match"

    # Keyword analysis
    required_keywords_matched: list[str] = field(default_factory=list)
    required_keywords_missing: list[str] = field(default_factory=list)
    preferred_keywords_matched: list[str] = field(default_factory=list)
    preferred_keywords_missing: list[str] = field(default_factory=list)

    # Sub-scores (0–100 each)
    required_kw_score: int  = 0
    preferred_kw_score: int = 0
    experience_score: int   = 0
    education_score: int    = 0
    completeness_score: int = 0

    # Resume structure
    sections_present: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)

    # Convenience breakdown dict for UI rendering
    sub_scores: dict[str, int] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Tech / skill keyword lexicon used as fallback extraction
# ─────────────────────────────────────────────────────────────────────────────

# Common tech keywords we always try to detect when the JD has no explicit
# "required:" section — ensures ATS matching still works on free-form JDs.
_TECH_LEXICON: set[str] = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "r", "scala", "ruby", "php", "perl", "bash", "shell",
    # Web
    "react", "angular", "vue", "next.js", "nuxt", "html", "css", "node.js",
    "express", "django", "flask", "fastapi", "spring", "laravel", "rails",
    # Data / ML
    "sql", "nosql", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "keras", "spark", "hadoop", "tableau", "power bi", "excel", "dbt",
    "airflow", "kafka", "flink", "hive", "presto",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "unix",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "oracle", "dynamodb", "bigquery", "snowflake",
    # Other
    "rest", "graphql", "grpc", "microservices", "agile", "scrum", "git",
    "jira", "confluence",
}

# Education degree keywords
_DEGREE_KEYWORDS: dict[str, list[str]] = {
    "phd":        ["phd", "ph.d", "doctorate", "doctoral"],
    "master":     ["master", "msc", "m.s.", "m.eng", "mba", "m.a.", "postgraduate"],
    "bachelor":   ["bachelor", "bsc", "b.s.", "b.eng", "b.a.", "b.tech", "undergraduate", "degree"],
    "associate":  ["associate", "a.s.", "a.a."],
    "diploma":    ["diploma", "certificate", "certification"],
}

# Resume section headers we look for (completeness check)
_COMPLETENESS_SECTIONS: list[tuple[str, list[str]]] = [
    ("Contact Information",  ["email", "phone", "@", "linkedin", "contact"]),
    ("Skills Section",       ["skill", "competenc", "technical", "technology", "technologies", "expertise"]),
    ("Experience Section",   ["experience", "employment", "work history", "career"]),
    ("Education Section",    ["education", "academic", "qualification", "degree", "university", "college"]),
    ("Projects Section",     ["project", "portfolio", "github", "built", "developed"]),
    ("Certifications Section",["certif", "license", "accredit", "aws certified", "pmp", "cissp"]),
]


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — keyword extraction
# ─────────────────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase, strip punctuation (except hyphen/dot for tech terms)."""
    return re.sub(r"[^\w\s.\-+#/]", " ", text.lower())


def _tokenise(text: str) -> set[str]:
    """Split on whitespace and return unique tokens."""
    return set(text.lower().split())


def _extract_section_text(jd: str, *headers: str) -> str:
    """
    Extract text following any of the given section headers in the JD.
    Returns concatenated text from all matching sections, or empty string.
    """
    combined: list[str] = []
    for header in headers:
        pattern = re.compile(
            rf"(?:^|\n)\s*{re.escape(header)}\s*[:\-–]?\s*\n(.*?)(?=\n\s*[A-Z][A-Za-z\s]+[:\-–]|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        for m in pattern.finditer(jd):
            combined.append(m.group(1))
    return "\n".join(combined)


def _extract_bullet_items(text: str) -> list[str]:
    """Extract bullet-point or numbered list items from a text block.

    Also splits comma-separated items on the same line so that
    'SQL, Python, Excel' yields three separate keyword candidates.
    """
    raw_items: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        # Remove bullet markers
        line = re.sub(r"^[-•*·◦▪▸►→✓✗✔]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if len(line) > 2:
            raw_items.append(line.strip())

    # Expand comma-separated items
    items: list[str] = []
    for item in raw_items:
        if "," in item:
            parts = [p.strip() for p in item.split(",") if p.strip()]
            items.extend(parts)
        else:
            items.append(item)
    return items


def _extract_tech_terms(text: str) -> list[str]:
    """
    Extract technology/skill terms from free-form text using the lexicon.
    Returns lowercase term list (may contain multi-word terms like 'power bi').
    """
    norm = _normalise(text)
    found: list[str] = []

    # Multi-word terms first (longest match wins)
    multi_word = sorted([t for t in _TECH_LEXICON if " " in t], key=len, reverse=True)
    for term in multi_word:
        if term in norm and term not in found:
            found.append(term)
            norm = norm.replace(term, "")  # avoid double-counting

    # Single-word terms
    tokens = set(norm.split())
    for term in _TECH_LEXICON:
        if " " not in term and term in tokens and term not in found:
            found.append(term)

    return found


def _extract_required_keywords(jd: str) -> list[str]:
    """
    Strategy (in priority order):
    1. Text under explicit 'required' / 'requirements' / 'qualifications' headers
    2. Fallback: all tech lexicon terms found anywhere in the JD
    """
    required_text = _extract_section_text(
        jd,
        "required", "requirements", "required qualifications",
        "must have", "must-have", "essential", "qualifications",
        "minimum qualifications", "minimum requirements",
    )

    if required_text.strip():
        items = _extract_bullet_items(required_text)
        # Also extract pure tech terms from those bullets
        tech_terms = _extract_tech_terms(required_text)
        # Merge: include the full bullet items AND extracted tech terms
        kw_set: list[str] = []
        seen: set[str] = set()
        for t in tech_terms:
            if t.lower() not in seen:
                kw_set.append(t)
                seen.add(t.lower())
        # Also pull short terms from bullet items (single word or 2-word phrases max)
        for item in items:
            words = item.split()
            if len(words) <= 2:  # only short skill-name phrases
                clean = item.strip().lower()
                if clean not in seen:
                    kw_set.append(item.strip())
                    seen.add(clean)
        return kw_set if kw_set else _extract_tech_terms(jd)

    # Pure fallback: any tech term in the full JD
    return _extract_tech_terms(jd)


def _extract_preferred_keywords(jd: str) -> list[str]:
    """
    Extract preferred / nice-to-have keywords from the JD.
    """
    preferred_text = _extract_section_text(
        jd,
        "preferred", "preferred qualifications", "nice to have",
        "nice-to-have", "bonus", "advantageous", "desirable",
        "additional", "plus", "a plus",
    )

    if preferred_text.strip():
        items = _extract_bullet_items(preferred_text)
        tech_terms = _extract_tech_terms(preferred_text)
        kw_set: list[str] = []
        seen: set[str] = set()
        for t in tech_terms:
            if t.lower() not in seen:
                kw_set.append(t)
                seen.add(t.lower())
        for item in items:
            words = item.split()
            if len(words) <= 2:  # only short skill-name phrases
                clean = item.strip().lower()
                if clean not in seen:
                    kw_set.append(item.strip())
                    seen.add(clean)
        return kw_set

    return []


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — keyword matching
# ─────────────────────────────────────────────────────────────────────────────

def _keyword_in_resume(keyword: str, resume_text_norm: str) -> bool:
    """Return True if keyword (or a close variant) appears in the normalised resume text."""
    kw = keyword.strip().lower()
    if not kw:
        return False
    # Direct substring search (handles multi-word terms like 'power bi')
    if kw in resume_text_norm:
        return True
    # Word-boundary search for single tokens
    if " " not in kw:
        return bool(re.search(rf"\b{re.escape(kw)}\b", resume_text_norm))
    return False


def _score_keywords(
    keywords: list[str],
    resume_text_norm: str,
) -> tuple[list[str], list[str], int]:
    """
    Check each keyword against the resume.
    Returns (matched, missing, score_0_100).
    """
    if not keywords:
        return [], [], 100  # no keywords to check → full score

    matched: list[str] = []
    missing: list[str] = []
    for kw in keywords:
        if _keyword_in_resume(kw, resume_text_norm):
            matched.append(kw)
        else:
            missing.append(kw)

    pct = round(len(matched) / len(keywords) * 100) if keywords else 100
    return matched, missing, pct


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — experience alignment
# ─────────────────────────────────────────────────────────────────────────────

def _extract_required_years(jd: str) -> Optional[int]:
    """Parse required years of experience from the JD (e.g. '5+ years', 'minimum 3 years')."""
    patterns = [
        r"(\d+)\s*\+?\s*years?\s+of\s+(?:relevant\s+|professional\s+)?experience",
        r"(\d+)\s*\+?\s*years?\s+experience",
        r"minimum\s+(?:of\s+)?(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
        r"(\d+)[-–](\d+)\s+years?",          # range — take lower bound
    ]
    for pattern in patterns:
        m = re.search(pattern, jd, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def _estimate_candidate_years(resume_text: str) -> int:
    """
    Heuristically estimate total years of professional experience from the resume.
    Looks for date ranges like '2018–2022', 'Jan 2019 – Present', etc.
    """
    # Match year pairs: e.g. 2018-2022, 2018 – Present
    year_range_pattern = re.compile(
        r"(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2}|present|current|now)",
        re.IGNORECASE,
    )

    import datetime
    current_year = datetime.datetime.now().year
    total_months = 0

    for m in year_range_pattern.finditer(resume_text):
        start_year = int(m.group(1))
        end_raw = m.group(2).lower()
        end_year = current_year if end_raw in ("present", "current", "now") else int(end_raw)

        if end_year >= start_year:
            months = (end_year - start_year) * 12
            # Cap individual tenure at 20 years to avoid parsing errors
            total_months += min(months, 240)

    # Deduplicate overlapping tenures by capping at plausible total
    total_years = min(total_months // 12, 35)
    return total_years


def _score_experience(jd: str, resume_text: str) -> int:
    """Return 0–100 score for experience alignment."""
    required_years = _extract_required_years(jd)
    if required_years is None:
        # No explicit requirement — check if resume has any experience mentions
        has_exp = bool(re.search(r"(experience|worked|position|role|job)", resume_text, re.IGNORECASE))
        return 80 if has_exp else 50

    candidate_years = _estimate_candidate_years(resume_text)

    if candidate_years >= required_years:
        # Full score if meets/exceeds; bonus diminishes above 150%
        ratio = candidate_years / required_years
        if ratio >= 1.5:
            return 100
        return min(100, round(70 + (ratio - 1.0) * 60))
    else:
        # Partial credit proportional to how close they are
        if required_years == 0:
            return 100
        ratio = candidate_years / required_years
        return max(0, round(ratio * 70))


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — education alignment
# ─────────────────────────────────────────────────────────────────────────────

_DEGREE_RANK: dict[str, int] = {
    "phd": 4,
    "master": 3,
    "bachelor": 2,
    "associate": 1,
    "diploma": 1,
}


def _detect_degree(text: str) -> Optional[str]:
    """Return the highest degree found in the text."""
    norm = text.lower()
    for degree, variants in _DEGREE_KEYWORDS.items():
        for v in variants:
            if v in norm:
                return degree
    return None


def _score_education(jd: str, resume_text: str) -> int:
    """Return 0–100 score for education alignment."""
    required_degree = _detect_degree(jd)
    candidate_degree = _detect_degree(resume_text)

    if required_degree is None:
        # No degree requirement stated — reward any degree mention
        return 90 if candidate_degree else 70

    req_rank  = _DEGREE_RANK.get(required_degree, 2)
    cand_rank = _DEGREE_RANK.get(candidate_degree, 0) if candidate_degree else 0

    if cand_rank >= req_rank:
        return 100
    elif cand_rank == req_rank - 1:
        return 65
    elif cand_rank > 0:
        return 40
    else:
        return 20


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers — resume completeness
# ─────────────────────────────────────────────────────────────────────────────

def _score_completeness(resume_text: str) -> tuple[list[str], list[str], int]:
    """
    Check for presence of standard resume sections.
    Returns (sections_present, sections_missing, score_0_100).
    """
    norm = resume_text.lower()
    present: list[str] = []
    missing: list[str] = []

    for section_name, hints in _COMPLETENESS_SECTIONS:
        found = any(hint in norm for hint in hints)
        if found:
            present.append(section_name)
        else:
            missing.append(section_name)

    total = len(_COMPLETENESS_SECTIONS)
    score = round(len(present) / total * 100) if total > 0 else 100
    return present, missing, score


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def compute_ats_score(
    job_description: str,
    parsed_resume: "ParsedResume",
) -> ATSResult:
    """
    Compute the ATS Compatibility Score for a single candidate.

    Parameters
    ----------
    job_description : str
        Raw job description text.
    parsed_resume : ParsedResume
        Parsed resume object from resume_parser.py.

    Returns
    -------
    ATSResult
        Full breakdown with composite score and all sub-scores.
        Always returned — never raises.
    """
    result = ATSResult()

    try:
        resume_text      = parsed_resume.raw_text or ""
        resume_text_norm = _normalise(resume_text)

        # ── 1. Required keyword match (40%) ──────────────────────────────────
        req_keywords = _extract_required_keywords(job_description)
        (
            result.required_keywords_matched,
            result.required_keywords_missing,
            result.required_kw_score,
        ) = _score_keywords(req_keywords, resume_text_norm)

        # ── 2. Preferred keyword match (20%) ─────────────────────────────────
        pref_keywords = _extract_preferred_keywords(job_description)
        (
            result.preferred_keywords_matched,
            result.preferred_keywords_missing,
            result.preferred_kw_score,
        ) = _score_keywords(pref_keywords, resume_text_norm)

        # ── 3. Experience alignment (20%) ─────────────────────────────────────
        result.experience_score = _score_experience(job_description, resume_text)

        # ── 4. Education alignment (10%) ──────────────────────────────────────
        result.education_score = _score_education(job_description, resume_text)

        # ── 5. Resume completeness (10%) ──────────────────────────────────────
        (
            result.sections_present,
            result.sections_missing,
            result.completeness_score,
        ) = _score_completeness(resume_text)

        # ── Composite score ───────────────────────────────────────────────────
        composite = (
            result.required_kw_score  * _WEIGHT_REQUIRED_KW
            + result.preferred_kw_score * _WEIGHT_PREFERRED_KW
            + result.experience_score   * _WEIGHT_EXPERIENCE
            + result.education_score    * _WEIGHT_EDUCATION
            + result.completeness_score * _WEIGHT_COMPLETENESS
        )
        result.ats_score = max(0, min(100, round(composite)))
        result.ats_label = _ats_label(result.ats_score)

        # ── Sub-scores dict for UI ────────────────────────────────────────────
        result.sub_scores = {
            "Required Keywords (40%)":  result.required_kw_score,
            "Preferred Keywords (20%)": result.preferred_kw_score,
            "Experience (20%)":         result.experience_score,
            "Education (10%)":          result.education_score,
            "Completeness (10%)":       result.completeness_score,
        }

    except Exception as exc:
        logger.exception("ATS scoring failed: %s", exc)
        result.ats_score = 0
        result.ats_label = "Low ATS Match"

    return result
