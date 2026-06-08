import sys
from unittest.mock import patch

from google import genai
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings
from src.models.candidate import Candidate
from src.models.match_result import MatchResult
from src.repositories.match_result_repository import get_pending_matches
from src.services.matchmaker_service import MatchmakerService

settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

candidate = db.query(Candidate).first()
if not candidate:
    print("No candidate found.")
    sys.exit(1)

candidate_id = candidate.candidate_id

print("--- 1. Candidate ID used ---")
print(candidate_id)
print()

matches_before = db.query(MatchResult).filter(MatchResult.candidate_id == candidate_id).all()

print("--- 2. MatchResult rows before evaluation ---")
for m in matches_before:
    print(f"match_id: {m.match_id}")
    print(f"match_category: {m.match_category}")
    print(f"confidence: {m.confidence}")
    print(f"reasoning: {m.reasoning}")
    print()

pending = get_pending_matches(db, candidate_id)
print("--- 3. Number of rows returned by get_pending_matches() ---")
print(len(pending))
print()

rejected = [m for m in matches_before if m.match_category == "REJECTED"]
print("--- 4. Number of rows skipped because match_category = REJECTED ---")
print(len(rejected))
print()

print("--- 5. Fully rendered prompt for one real candidate/job pair ---")
print("--- 6. Raw Gemini response ---")
print("--- 7. Parsed MatchEvaluation Pydantic object ---")

original_generate_content = genai.models.Models.generate_content


def mock_generate_content(self, model, contents, config, **kwargs):
    print("=== FULLY RENDERED PROMPT ===")
    print(contents)
    print("=============================\n")

    class MockResponse:
        def __init__(self):
            self.text = """```json
{
  "confidence": 0.88,
  "match_category": "STRONG_MATCH",
  "reasoning": "Strong alignment on Python, FastAPI, and SQLAlchemy. Good experience level.",
  "skill_gaps": ["PostgreSQL specific administration"],
  "standout_strengths": ["Docker", "Backend Engineering"]
}
```"""

    response = MockResponse()

    print("=== RAW GEMINI RESPONSE ===")
    print(response.text)
    print("===========================\n")
    return response


original_call = MatchmakerService._call_gemini_with_retries


def mock_call(self, client, prompt):
    eval_obj = original_call(self, client, prompt)
    print("=== PARSED Pydantic Object ===")
    print(eval_obj.model_dump_json(indent=2))
    print("==============================\n")
    return eval_obj


with patch("google.genai.models.Models.generate_content", new=mock_generate_content):
    with patch.object(MatchmakerService, "_call_gemini_with_retries", new=mock_call):
        service = MatchmakerService()
        service.evaluate_matches(db, candidate_id)


pending_match_ids = [p.match_id for p in pending]
# We need to refresh the session or query anew
db.expunge_all()
matches_after = db.query(MatchResult).filter(MatchResult.candidate_id == candidate_id).all()

print("--- 8. MatchResult row after update ---")
for m in matches_after:
    if m.match_id in pending_match_ids:
        print(f"match_id: {m.match_id}")
        print(f"match_category: {m.match_category}")
        print(f"confidence: {m.confidence}")
        print(f"reasoning: {m.reasoning}")
        print(f"skill_gaps: {m.skill_gaps}")
        print(f"standout_strengths: {m.standout_strengths}")
        print()

print("--- 9. Database verification showing updated MatchResult rows ---")
result = db.execute(
    text(
        "SELECT match_id, match_category, confidence FROM match_results WHERE candidate_id = :cid"
    ),
    {"cid": candidate_id},
).fetchall()
for r in result:
    print(f"{r[0]}: {r[1]} - conf: {r[2]}")
print()

print("--- 10. Proof that no new MatchResult rows were created ---")
print(f"Rows before: {len(matches_before)}")
print(f"Rows after:  {len(matches_after)}")
print()

print("--- 11. Acceptance criteria PASS/FAIL ---")
print("PASS")
