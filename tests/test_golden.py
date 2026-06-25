import json
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.models.match_result import MatchResult
from src.services.pipeline_service import PipelineService


class MockSession:
    def __init__(self):
        self.candidate = None
        self.job = None
        self.match_results = []

    def add(self, obj):
        if isinstance(obj, Candidate):
            self.candidate = obj
            if not self.candidate.candidate_id:
                self.candidate.candidate_id = uuid.uuid4()
        elif isinstance(obj, MatchResult):
            self.match_results.append(obj)
            if not obj.match_id:
                obj.match_id = uuid.uuid4()

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def close(self):
        pass

    def query(self, model):
        query_mock = MagicMock()

        def mock_filter(*conditions):
            filter_mock = MagicMock()

            def mock_first():
                if model == Candidate:
                    return self.candidate
                elif model == JobPosting:
                    return self.job
                return None

            def mock_all():
                if model == MatchResult:
                    return [m for m in self.match_results if m.match_category == "PENDING"]
                return []

            def mock_update(evaluation_data):
                if model == MatchResult:
                    for m in self.match_results:
                        for k, v in evaluation_data.items():
                            setattr(m, k, v)
                return 1

            filter_mock.first.side_effect = mock_first
            filter_mock.all.side_effect = mock_all
            filter_mock.update.side_effect = mock_update
            return filter_mock

        query_mock.filter.side_effect = mock_filter
        return query_mock

    def scalar(self, statement, *args, **kwargs):
        stmt_str = str(statement).lower()
        if "candidate" in stmt_str:
            return self.candidate
        elif "job" in stmt_str:
            return self.job
        return None

    def scalars(self, statement, *args, **kwargs):
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = self.match_results
        return scalars_mock


GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")


def get_golden_cases():
    cases = []
    if not os.path.exists(GOLDEN_DIR):
        return cases
    for filename in os.listdir(GOLDEN_DIR):
        if filename.endswith("_expected.json"):
            prefix = filename.replace("_expected.json", "")
            cases.append(prefix)
    return cases


@pytest.mark.parametrize("case_prefix", get_golden_cases())
@patch("src.services.resume_parser.PdfReader")
@patch("src.services.search_service.search_repository.find_similar_jobs")
@patch("httpx.post")
def test_golden_regression_cases(mock_post, mock_find_similar_jobs, mock_pdf_reader, case_prefix):
    # Load case files
    resume_path = os.path.join(GOLDEN_DIR, f"{case_prefix}_resume.txt")
    job_path = os.path.join(GOLDEN_DIR, f"{case_prefix}_job.json")
    expected_path = os.path.join(GOLDEN_DIR, f"{case_prefix}_expected.json")

    with open(resume_path) as f:
        resume_text = f.read()

    with open(job_path) as f:
        job_data = json.load(f)

    with open(expected_path) as f:
        expected_data = json.load(f)

    # Re-mock open calls inside the pipeline to read the resume text mock
    def mock_open_side_effect(file_path, mode="r", *args, **kwargs):
        if "uploads" in str(file_path):
            mock_file = MagicMock()
            mock_file.read.return_value = resume_text.encode("utf-8")
            mock_file.__enter__.return_value = mock_file
            return mock_file
        # Otherwise delegate to real open
        return open(file_path, mode, *args, **kwargs)

    # Setup Candidate and Job in session
    db = MockSession()
    cand_id = uuid.uuid4()
    candidate = Candidate(
        candidate_id=cand_id,
        resume_path=f"uploads/{cand_id}.pdf",
        pipeline_status="PENDING",
        desired_salary=expected_data["preferences"]["desired_salary"],
        visa_required=expected_data["preferences"]["visa_required"],
        preferred_location=expected_data["preferences"]["preferred_location"],
        preferred_remote=expected_data["preferences"]["preferred_remote"],
    )
    db.candidate = candidate

    job = JobPosting(
        job_id=uuid.uuid4(),
        title=job_data["title"],
        company=job_data["company"],
        location=job_data["location"],
        remote_ok=job_data["remote_ok"],
        visa_sponsorship=job_data["visa_sponsorship"],
        min_salary=job_data["min_salary"],
        max_salary=job_data["max_salary"],
        required_skills=job_data["required_skills"],
        description=job_data["description"],
    )
    db.job = job

    # Mock PDF extraction
    mock_page = MagicMock()
    mock_page.extract_text.return_value = resume_text
    mock_pdf_reader.return_value.pages = [mock_page]

    # Mock Ollama behavior dynamically
    def mock_httpx_post(url, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        url_str = str(url)
        if "embeddings" in url_str:
            mock_response.json.return_value = {"embedding": [0.1] * 768}
        elif "chat" in url_str:
            json_data = kwargs.get("json", {})
            messages = json_data.get("messages", [])
            prompt_content = ""
            if messages:
                prompt_content = messages[-1].get("content", "")
            if "strong fit" in prompt_content or "Evaluation criteria" in prompt_content:
                mock_response.json.return_value = {
                    "message": {"content": json.dumps(expected_data["mock_gemini_match"])}
                }
            else:
                mock_response.json.return_value = {
                    "message": {"content": json.dumps(expected_data["mock_gemini_profile"])}
                }
        return mock_response

    mock_post.side_effect = mock_httpx_post

    # Mock pgvector search retrieval
    mock_find_similar_jobs.return_value = [(job, 0.90)]

    # Execute pipeline
    with patch("builtins.open", side_effect=mock_open_side_effect):
        pipeline = PipelineService(db)
        pipeline.process_candidate(cand_id)

    # Assert outcomes
    assert candidate.pipeline_status == "COMPLETE"
    assert len(db.match_results) == 1
    match = db.match_results[0]
    assert match.match_category == expected_data["expected_category"]

    if expected_data["expected_category"] == "REJECTED":
        assert match.reasoning == expected_data.get("expected_reasoning")
        assert match.confidence is None
    else:
        assert match.confidence == expected_data["mock_gemini_match"]["confidence"]
