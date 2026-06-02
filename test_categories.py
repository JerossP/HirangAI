"""Unit tests for category-based scoring."""
import sys
sys.path.insert(0, ".")

from candidate_evaluator import (
    EvaluationResult,
    _parse_llm_response,
    _calculate_weighted_score,
)
from prompts import CATEGORY_KEYS, CATEGORY_WEIGHTS

# ── Test 1: full JSON SCORE_BLOCK with category_scores ───────────────────────
r1 = EvaluationResult()
_parse_llm_response(
    "### Category Breakdown\n"
    "- **Technical Skills** (score 92/100): Strong Python and FastAPI.\n"
    "- **Relevant Experience** (score 88/100): 6 years backend.\n"
    "- **Education** (score 80/100): BSc Computer Science.\n"
    "- **Certifications** (score 75/100): AWS Certified.\n"
    "- **Communication & Soft Skills** (score 85/100): Led cross-functional teams.\n\n"
    "```json\n"
    '{\n'
    '  "match_score": 86,\n'
    '  "recommendation": "Strong Hire",\n'
    '  "confidence": "High",\n'
    '  "category_scores": {\n'
    '    "technical_skills": 92,\n'
    '    "relevant_experience": 88,\n'
    '    "education": 80,\n'
    '    "certifications": 75,\n'
    '    "communication_soft_skills": 85\n'
    '  }\n'
    '}\n'
    "```",
    r1,
)
print("Test 1 category_scores:", r1.category_scores)
assert r1.category_scores["technical_skills"] == 92
assert r1.category_scores["relevant_experience"] == 88
assert r1.category_scores["education"] == 80
assert r1.category_scores["certifications"] == 75
assert r1.category_scores["communication_soft_skills"] == 85
print("Test 1 match_score (weighted):", r1.match_score)
# Weighted: 92*0.30 + 88*0.30 + 80*0.15 + 75*0.10 + 85*0.15
expected = round(92*0.30 + 88*0.30 + 80*0.15 + 75*0.10 + 85*0.15)
assert r1.match_score == expected, f"Expected {expected}, got {r1.match_score}"
print(f"  weighted score correct: {r1.match_score}")

# ── Test 2: _calculate_weighted_score with all categories ────────────────────
scores = {"technical_skills": 70, "relevant_experience": 60, "education": 80,
          "certifications": 50, "communication_soft_skills": 90}
w = _calculate_weighted_score(scores)
expected2 = round(70*0.30 + 60*0.30 + 80*0.15 + 50*0.10 + 90*0.15)
assert w == expected2, f"Expected {expected2}, got {w}"
print("Test 2 weighted score:", w, "(correct)")

# ── Test 3: partial categories — weighted average over available only ─────────
partial = {"technical_skills": 80, "relevant_experience": 60}
w3 = _calculate_weighted_score(partial)
# total_weight = 0.30 + 0.30 = 0.60; weighted_sum = 80*0.30 + 60*0.30 = 42
expected3 = round((80*0.30 + 60*0.30) / 0.60)
assert w3 == expected3, f"Expected {expected3}, got {w3}"
print("Test 3 partial weighted:", w3, "(correct)")

# ── Test 4: regex fallback extracts category scores from prose ───────────────
from candidate_evaluator import _extract_category_scores_regex
r4 = EvaluationResult()
_extract_category_scores_regex(
    "- **Technical Skills** (score 77/100): Good Python.\n"
    "- **Education** (score 65/100): Bachelor's.\n"
    "- **Certifications** (score 50/100): None listed.",
    r4,
)
print("Test 4 regex categories:", r4.category_scores)
assert r4.category_scores.get("technical_skills") == 77
assert r4.category_scores.get("education") == 65
assert r4.category_scores.get("certifications") == 50

# ── Test 5: ensure all CATEGORY_KEYS are in CATEGORY_WEIGHTS ─────────────────
for k in CATEGORY_KEYS:
    assert k in CATEGORY_WEIGHTS, f"Missing weight for {k}"
total = sum(CATEGORY_WEIGHTS.values())
assert abs(total - 1.0) < 0.001, f"Weights don't sum to 1: {total}"
print("Test 5 weights sum:", round(total, 3), "(correct)")

print("\nAll 5 tests passed.")
