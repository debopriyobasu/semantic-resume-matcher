import json
import logging
import time
import uuid

from google import genai
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.exceptions import MatchmakingError
from src.core.metrics import metrics_store
from src.core.prompts import load_prompt, render_prompt
from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.repositories import match_result_repository
from src.schemas.matchmaker import MatchEvaluation

logger = logging.getLogger(__name__)


class MatchmakerService:
    def evaluate_matches(self, db: Session, candidate_id: uuid.UUID) -> None:
        """
        Evaluate PENDING matches for a candidate using Gemini.
        """
        candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if not candidate:
            return

        pending_matches = match_result_repository.get_pending_matches(db, candidate_id)
        if not pending_matches:
            return

        evaluation_criteria = load_prompt("evaluation_criteria.md")

        candidate_dict = {
            "skills": candidate.skills,
            "experience_years": candidate.experience_years,
            "education": candidate.education,
        }
        candidate_profile_json = json.dumps(candidate_dict, indent=2)

        settings = get_settings()
        client = genai.Client(api_key=settings.google_api_key)

        for match in pending_matches:
            job = db.query(JobPosting).filter(JobPosting.job_id == match.job_id).first()
            if not job:
                continue

            job_dict = {
                "title": job.title,
                "company": job.company,
                "required_skills": job.required_skills,
                "description": job.description,
            }
            job_posting_json = json.dumps(job_dict, indent=2)

            prompt = render_prompt(
                "matchmaker.md",
                {
                    "candidate_profile": candidate_profile_json,
                    "job_posting": job_posting_json,
                    "evaluation_criteria": evaluation_criteria,
                },
            )

            try:
                evaluation = self._call_gemini_with_retries(client, prompt)

                match_result_repository.update_match_result(
                    db,
                    match.match_id,
                    {
                        "confidence": evaluation.confidence,
                        "match_category": evaluation.match_category,
                        "reasoning": evaluation.reasoning,
                        "skill_gaps": evaluation.skill_gaps,
                        "standout_strengths": evaluation.standout_strengths,
                    },
                )

                metrics_store.record_match_confidence(evaluation.confidence)
                metrics_store.increment_match_category(evaluation.match_category)

            except MatchmakingError as e:
                logger.error(f"Failed to evaluate match {match.match_id}: {e}")
                # We could set status to FAILED or leave it PENDING
                # but usually we just skip it or log it

    def _call_gemini_with_retries(self, client: genai.Client, prompt: str) -> MatchEvaluation:
        max_retries = 3
        retry_delays = [1, 2, 4]

        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

                if not response.text:
                    raise MatchmakingError("Received empty response from Gemini.")

                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                evaluation_data = json.loads(response_text)
                return MatchEvaluation(**evaluation_data)

            except ValidationError as e:
                raise MatchmakingError(f"Failed to validate extracted evaluation: {e}") from e
            except Exception as e:
                if attempt < max_retries:
                    delay = retry_delays[attempt]
                    logger.warning(
                        f"Transient error calling Gemini. Retrying in {delay} seconds. Error: {e}"
                    )
                    time.sleep(delay)
                else:
                    raise MatchmakingError(f"Failed to call Gemini after retries: {e}") from e
