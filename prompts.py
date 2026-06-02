"""
prompts.py
──────────
Central repository for all LLM prompt templates used by HirangAI.
Each prompt is a plain Python string (or callable returning a string) so
they can be imported and composed freely.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Category definitions  (shared with candidate_evaluator.py)
# ─────────────────────────────────────────────────────────────────────────────

# Canonical category keys used throughout the system
CATEGORY_KEYS = [
    "technical_skills",
    "relevant_experience",
    "education",
    "certifications",
    "communication_soft_skills",
]

# Human-readable labels for display
CATEGORY_LABELS = {
    "technical_skills":          "Technical Skills",
    "relevant_experience":       "Relevant Experience",
    "education":                 "Education",
    "certifications":            "Certifications",
    "communication_soft_skills": "Communication & Soft Skills",
}

# Weights used to compute the overall match score from category scores
CATEGORY_WEIGHTS = {
    "technical_skills":          0.30,
    "relevant_experience":       0.30,
    "education":                 0.15,
    "certifications":            0.10,
    "communication_soft_skills": 0.15,
}


# ─────────────────────────────────────────────────────────────────────────────
# System prompt
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are HirangAI, an expert HR talent-acquisition assistant.
Your role is to evaluate candidates objectively and provide structured,
actionable feedback to help recruiters make informed hiring decisions.

Guidelines:
- Be factual and evidence-based; cite specific resume details.
- Remain unbiased; focus on skills, experience, and role fit.
- Structure every response clearly with headings and bullet points.
- Assign numeric scores on a 0–100 scale as instructed.
- Always include the SCORE_BLOCK exactly as specified — it is machine-parsed.
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# Scoring reference
# ─────────────────────────────────────────────────────────────────────────────

SCORING_GUIDE = """
Overall Match Score scale (0–100) — weighted average of category scores:
  95–100 → Exceptional Candidate
  90–94  → Outstanding Match
  85–89  → Strong Hire
  75–84  → Recommended
  65–74  → Potential Fit
  55–64  → Consider with Reservations
  40–54  → Weak Match
  Below 40 → Not Recommended

Category weights:
  Technical Skills          30%
  Relevant Experience       30%
  Education                 15%
  Communication & Soft Skills 15%
  Certifications            10%

Confidence Level:
  High   — resume is detailed and closely matches the JD
  Medium — resume partially matches or has gaps
  Low    — resume is vague, very short, or mostly unrelated
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# Candidate evaluation prompt
# ─────────────────────────────────────────────────────────────────────────────

def build_evaluation_prompt(job_description: str, resume_text: str) -> str:
    """Return a filled evaluation prompt for a single candidate."""
    return f"""
## Job Description
{job_description}

## Candidate Resume
{resume_text}

---

{SCORING_GUIDE}

Please evaluate the candidate against the job description and respond with
the following sections IN ORDER:

### 1. Category Breakdown (score each 0–100)
Score each category and provide one bullet of evidence per category.

- **Technical Skills** (score X/100): <evidence from resume>
- **Relevant Experience** (score X/100): <evidence from resume>
- **Education** (score X/100): <evidence from resume>
- **Certifications** (score X/100): <evidence from resume>
- **Communication & Soft Skills** (score X/100): <evidence from resume>

### 2. Overall Match Score  (weighted average of categories)
State the calculated integer score and a one-sentence rationale.
Example: "Score: 78 — Strong technical background but limited relevant experience."

### 3. Key Strengths
List up to 5 bullet points highlighting what makes the candidate a strong fit.

### 4. Skill Gaps
List any required skills or experience the candidate appears to lack.

### 5. Experience Summary
Briefly summarise the candidate's relevant work history (2–4 sentences).

### 6. Recommendation
Choose the label that matches the overall score:
  95–100 → **Exceptional Candidate**
  90–94  → **Outstanding Match**
  85–89  → **Strong Hire**
  75–84  → **Recommended**
  65–74  → **Potential Fit**
  55–64  → **Consider with Reservations**
  40–54  → **Weak Match**
  Below 40 → **Not Recommended**

Followed by a short paragraph justifying the recommendation.

### 7. SCORE_BLOCK
Output this block EXACTLY — it is machine-parsed. No prose before or after.

```json
{{
  "match_score": <weighted integer 0-100>,
  "recommendation": "<label from the scale above>",
  "confidence": "<High|Medium|Low>",
  "category_scores": {{
    "technical_skills": <integer 0-100>,
    "relevant_experience": <integer 0-100>,
    "education": <integer 0-100>,
    "certifications": <integer 0-100>,
    "communication_soft_skills": <integer 0-100>
  }}
}}
```
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# Comparison / ranking prompt  (multi-candidate)
# ─────────────────────────────────────────────────────────────────────────────

def build_ranking_prompt(job_description: str, candidates: list[dict]) -> str:
    """
    Build a prompt to rank multiple candidates.

    Parameters
    ----------
    job_description : str
    candidates      : list of dicts with keys ``name`` and ``resume_text``
    """
    candidate_blocks = "\n\n".join(
        f"### Candidate {i + 1}: {c['name']}\n{c['resume_text']}"
        for i, c in enumerate(candidates)
    )
    return f"""
## Job Description
{job_description}

## Candidates
{candidate_blocks}

---

Rank all candidates from most suitable to least suitable for the role.
For each candidate provide:
- Rank position
- Overall match score (0–100)
- One-sentence justification

Finish with a short paragraph recommending which candidate(s) to advance
to the next interview stage.
""".strip()
