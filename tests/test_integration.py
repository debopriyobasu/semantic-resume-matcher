import io
import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.db.session import get_db
from src.main import app
from src.models.candidate import Candidate
from src.models.job_posting import JobPosting
from src.models.match_result import MatchResult
from src.services.pipeline_service import PipelineService

client = TestClient(app)


class MockSession:
    def __init__(self):
        self.candidate = None
        self.job = None
        self.match_results = []
        self.commit_count = 0

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
        self.commit_count += 1

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
        for m in self.match_results:
            m.__dict__["job"] = self.job
        scalars_mock.all.return_value = self.match_results
        return scalars_mock


@pytest.fixture
def mock_db_session():
    return MockSession()


@pytest.fixture(autouse=True)
def setup_overrides(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield
    app.dependency_overrides.clear()


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
                "message": {
                    "content": json.dumps(
                        {
                            "confidence": 0.92,
                            "match_category": "STRONG_MATCH",
                            "reasoning": "Excellent skill match.",
                            "skill_gaps": [],
                            "standout_strengths": ["Python", "FastAPI"],
                        }
                    )
                }
            }
        else:
            mock_response.json.return_value = {
                "message": {
                    "content": json.dumps(
                        {
                            "name": "John Doe",
                            "email": "john@example.com",
                            "skills": ["Python", "FastAPI"],
                            "experience_years": 5,
                            "education": "BSc",
                            "location": "New York",
                        }
                    )
                }
            }
    return mock_response


@patch("src.api.upload.run_pipeline")
@patch("builtins.open")
@patch("src.services.resume_parser.PdfReader")
@patch("src.services.search_service.search_repository.find_similar_jobs")
@patch("httpx.post")
def test_end_to_end_pipeline_flow(
    mock_post,
    mock_find_similar_jobs,
    mock_pdf_reader,
    mock_open,
    mock_run_pipeline,
    mock_db_session,
):
    # 1. Setup the Job in mock session database
    job = JobPosting(
        job_id=uuid.uuid4(),
        title="Software Engineer",
        company="Tech Corp",
        location="New York",
        remote_ok=True,
        visa_sponsorship=True,
        min_salary=90000,
        max_salary=130000,
        required_skills=["Python", "FastAPI"],
    )
    mock_db_session.job = job

    # 2. Upload Resume via API
    file_content = b"%PDF-1.4\nMock PDF content"
    file = io.BytesIO(file_content)

    upload_response = client.post(
        "/upload-resume",
        files={"file": ("integration_test.pdf", file, "application/pdf")},
        data={
            "desired_salary": "100000",
            "visa_required": "false",
            "preferred_location": "New York",
            "preferred_remote": "true",
        },
    )

    assert upload_response.status_code == 200
    candidate_data = upload_response.json()
    candidate_id = uuid.UUID(candidate_data["candidate_id"])
    assert candidate_data["status"] == "PENDING"

    # Verify candidate is created and has fields
    assert mock_db_session.candidate is not None
    assert mock_db_session.candidate.desired_salary == 100000

    # 3. Mock all PDF, Embedding, Gemini, and Search operations for processing
    mock_open.return_value.__enter__.return_value.read.return_value = b"pdf content"

    # Parser Mocks
    mock_page = MagicMock()
    mock_page.extract_text.return_value = (
        "Resume text showing John Doe, Software Engineer, Python experience."
    )
    mock_pdf_reader.return_value.pages = [mock_page]

    # HTTP client mock setup
    mock_post.side_effect = mock_httpx_post

    # Search Mocks
    mock_find_similar_jobs.return_value = [(job, 0.88)]

    # 4. Process the candidate through the Pipeline Service
    pipeline = PipelineService(mock_db_session)
    pipeline.process_candidate(candidate_id)

    # 5. Verify candidate status is now COMPLETE via API
    status_response = client.get(f"/candidate/{candidate_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["pipeline_status"] == "COMPLETE"
    assert status_data["status"] == "COMPLETE"

    # 6. Retrieve match results via API
    matches_response = client.get(f"/candidate/{candidate_id}/matches")
    assert matches_response.status_code == 200
    matches_data = matches_response.json()
    assert matches_data["candidate_id"] == str(candidate_id)
    assert len(matches_data["matches"]) == 1
    match_detail = matches_data["matches"][0]
    assert match_detail["match_category"] == "STRONG_MATCH"
    assert match_detail["confidence"] == 0.92
    assert match_detail["vector_score"] == 0.88
    assert match_detail["job"]["title"] == "Software Engineer"
