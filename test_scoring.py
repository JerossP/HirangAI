"""Quick unit tests for the new scoring engine."""
import sys
sys.path.insert(0, ".")

from candidate_evaluator import EvaluationResult, _parse_llm_response, _score_to_recommendation

# ── Test 1: JSON SCORE_BLOCK extraction ──────────────────────────────────────
r1 = EvaluationResult()
_parse_llm_response(
    "Score: 82 — Strong match.\n"
    "```json\n"
    '{"match_score": 82, "recommendation": "Recommended", "confidence": "High"}\n'
    "```",
    r1,
)
print("Test 1 (JSON block):", r1.match_score, "|", r1.recommendation, "|", r1.confidence_level)
assert r1.match_score == 82, f"Expected 82 got {r1.match_score}"
assert r1.recommendation == "Recommended"
assert r1.confidence_level == "High"

# ── Test 2: regex fallback (no JSON block) ───────────────────────────────────
r2 = EvaluationResult()
_parse_llm_response("Score: 91 — Outstanding.\n**Outstanding Match** recommendation.", r2)
print("Test 2 (regex):", r2.match_score, "|", r2.recommendation, "|", r2.confidence_level)
assert r2.match_score == 91
assert r2.recommendation == "Outstanding Match"

# ── Test 3: derive recommendation from score only ────────────────────────────
r3 = EvaluationResult()
_parse_llm_response("Score: 55", r3)
print("Test 3 (derive rec):", r3.match_score, "|", r3.recommendation)
assert r3.match_score == 55
assert r3.recommendation == "Consider with Reservations"

# ── Test 4: derive score from recommendation only ────────────────────────────
r4 = EvaluationResult()
_parse_llm_response("**Strong Hire**", r4)
print("Test 4 (derive score):", r4.match_score, "|", r4.recommendation)
assert r4.match_score == 87

# ── Test 5: score_to_recommendation scale ────────────────────────────────────
assert _score_to_recommendation(97) == "Exceptional Candidate"
assert _score_to_recommendation(92) == "Outstanding Match"
assert _score_to_recommendation(87) == "Strong Hire"
assert _score_to_recommendation(80) == "Recommended"
assert _score_to_recommendation(69) == "Potential Fit"
assert _score_to_recommendation(58) == "Consider with Reservations"
assert _score_to_recommendation(45) == "Weak Match"
assert _score_to_recommendation(30) == "Not Recommended"

# ── Test 6: score capped to 0-100 ────────────────────────────────────────────
r5 = EvaluationResult()
_parse_llm_response(
    "```json\n"
    '{"match_score": 110, "recommendation": "Exceptional Candidate", "confidence": "High"}\n'
    "```",
    r5,
)
assert r5.match_score == 100, f"Expected 100 (capped), got {r5.match_score}"

print("\nAll 6 tests passed.")
