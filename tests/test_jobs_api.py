import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.db.session import get_db
from src.main import app
from src.models.job_embedding import JobEmbedding
from src.models.job_posting import JobPosting

client = TestClient(app)


class MockSession:
    def __init__(self):
        self.jobs = []
        self.embeddings = []
        self.commit_called = False
        self.deleted_all = False

    def execute(self, query):
        query_str = str(query).lower()
        if "delete" in query_str and "job_postings" in query_str:
            count = len(self.jobs)
            self.jobs = []
            self.embeddings = []
            self.deleted_all = True
            mock_res = MagicMock()
            mock_res.rowcount = count
            return mock_res
        return MagicMock()

    def add(self, obj):
        self.jobs.append(obj)

    def add_all(self, objs):
        self.jobs.extend(objs)

    def commit(self):
        self.commit_called = True

    def rollback(self):
        pass

    def close(self):
        pass

    def query(self, model):
        mock_query = MagicMock()
        if model == JobEmbedding:

            def mock_filter(*args, **kwargs):
                filter_mock = MagicMock()

                def mock_delete():
                    # Simulate delete of an embedding
                    return 1

                filter_mock.delete.side_effect = mock_delete
                return filter_mock

            mock_query.filter.side_effect = mock_filter
        return mock_query

    def scalars(self, stmt):
        mock_res = MagicMock()
        mock_res.all.return_value = self.jobs
        return mock_res

    def scalar(self, stmt):
        stmt_str = str(stmt).lower()
        if "count" in stmt_str:
            if "job_embeddings" in stmt_str:
                embedded_ids = {e.job_id for e in self.embeddings}
                not_embedded = [j for j in self.jobs if j.job_id not in embedded_ids]
                return len(not_embedded)
            else:
                return len(self.jobs)
        return None


@pytest.fixture
def mock_db():
    session = MockSession()
    return session


@pytest.fixture(autouse=True)
def setup_overrides(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_background_tasks():
    with patch("fastapi.BackgroundTasks.add_task") as mock:
        yield mock


def test_delete_jobs_dataset(mock_db) -> None:
    # Populate mock db
    mock_db.jobs = [
        JobPosting(job_id=uuid.uuid4(), title="Job1", company="Company1", description="Desc1"),
        JobPosting(job_id=uuid.uuid4(), title="Job2", company="Company2", description="Desc2"),
    ]

    response = client.delete("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["deleted_count"] == 2
    assert len(mock_db.jobs) == 0


def test_get_embedding_status(mock_db) -> None:
    job1_id = uuid.uuid4()
    job2_id = uuid.uuid4()
    mock_db.jobs = [
        JobPosting(job_id=job1_id, title="Job1", company="Company1", description="Desc1"),
        JobPosting(job_id=job2_id, title="Job2", company="Company2", description="Desc2"),
    ]
    # Simulate job1 embedded, job2 not embedded
    mock_db.embeddings = [JobEmbedding(job_id=job1_id)]

    response = client.get("/jobs/embedding-status")
    assert response.status_code == 200
    data = response.json()
    assert data["embedding_completed"] is False
    assert data["total_jobs"] == 2
    assert data["jobs_without_embeddings"] == 1

    # Simulate all embedded
    mock_db.embeddings.append(JobEmbedding(job_id=job2_id))
    response = client.get("/jobs/embedding-status")
    assert response.status_code == 200
    data = response.json()
    assert data["embedding_completed"] is True
    assert data["jobs_without_embeddings"] == 0


def test_upload_jobs_replace_mode(mock_db, mock_background_tasks) -> None:
    mock_db.jobs = [
        JobPosting(job_id=uuid.uuid4(), title="OldJob", company="OldCompany", description="Desc")
    ]

    csv_data = (
        "title,company,location,remote_ok,visa_sponsorship,min_salary,max_salary,required_skills,description\n"
        "New Job 1,New Company,Remote,true,false,100000,150000,Python;FastAPI,Build APIs\n"
        "New Job 2,New Company,,false,true,,,SQL,Database admin\n"
    )
    file = io.BytesIO(csv_data.encode("utf-8"))

    response = client.post(
        "/jobs/upload?mode=replace", files={"file": ("jobs.csv", file, "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mode"] == "replace"
    assert data["added_count"] == 2
    assert data["deleted_count"] == 1
    assert data["updated_count"] == 0
    assert data["embedding_completed"] is False  # Because they are not embedded yet

    assert len(mock_db.jobs) == 2
    assert mock_db.jobs[0].title == "New Job 1"
    assert mock_db.jobs[1].title == "New Job 2"
    assert mock_db.jobs[1].remote_ok is False
    assert mock_db.jobs[1].required_skills == ["SQL"]

    mock_background_tasks.assert_called_once()


def test_upload_jobs_update_mode(mock_db, mock_background_tasks) -> None:
    job1_id = uuid.uuid4()
    job2_id = uuid.uuid4()
    mock_db.jobs = [
        JobPosting(
            job_id=job1_id,
            title="Software Engineer",
            company="Tech Corp",
            location="New York",
            remote_ok=True,
            visa_sponsorship=True,
            min_salary=100000,
            max_salary=150000,
            required_skills=["Python", "FastAPI"],
            description="Build apps.",
        ),
        JobPosting(
            job_id=job2_id,
            title="Product Manager",
            company="Biz Corp",
            location="Remote",
            remote_ok=True,
            visa_sponsorship=False,
            min_salary=120000,
            max_salary=180000,
            required_skills=["Agile"],
            description="Manage backlog.",
        ),
    ]
    # Assume both currently have embeddings
    mock_db.embeddings = [JobEmbedding(job_id=job1_id), JobEmbedding(job_id=job2_id)]

    csv_data = (
        "title,company,location,remote_ok,visa_sponsorship,min_salary,max_salary,required_skills,description\n"
        # Software Engineer unchanged
        "Software Engineer,Tech Corp,New York,true,true,100000,150000,Python;FastAPI,Build apps.\n"
        # Product Manager changed (location changed to New York, required skills changed)
        "Product Manager,Biz Corp,New York,true,false,120000,180000,Agile;Scrum,Manage backlog.\n"
        # New Job
        "Data Analyst,Biz Corp,Remote,true,false,80000,100000,SQL;Python,Analyze data\n"
    )
    file = io.BytesIO(csv_data.encode("utf-8"))

    response = client.post(
        "/jobs/upload?mode=update", files={"file": ("jobs.csv", file, "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mode"] == "update"
    assert data["added_count"] == 1
    assert data["updated_count"] == 1
    assert data["deleted_count"] == 0

    # There should now be 3 jobs
    assert len(mock_db.jobs) == 3

    # Product Manager location should be updated
    pm = next(j for j in mock_db.jobs if j.title == "Product Manager")
    assert pm.location == "New York"
    assert pm.required_skills == ["Agile", "Scrum"]

    mock_background_tasks.assert_called_once()


def test_upload_jobs_invalid_format() -> None:
    # Test uploading a non-CSV file
    file = io.BytesIO(b"Hello World")
    response = client.post(
        "/jobs/upload?mode=replace", files={"file": ("jobs.txt", file, "text/plain")}
    )
    assert response.status_code == 400
    assert "Only CSV files are allowed" in response.json()["detail"]


def test_upload_jobs_missing_columns() -> None:
    # CSV missing 'description' column
    csv_data = "title,company,location,remote_ok,visa_sponsorship,min_salary,max_salary,required_skills\n"
    file = io.BytesIO(csv_data.encode("utf-8"))
    response = client.post(
        "/jobs/upload?mode=replace", files={"file": ("jobs.csv", file, "text/csv")}
    )
    assert response.status_code == 400
    assert "CSV must contain headers" in response.json()["detail"]


def test_upload_jobs_empty_file() -> None:
    file = io.BytesIO(b"")
    response = client.post(
        "/jobs/upload?mode=replace", files={"file": ("jobs.csv", file, "text/csv")}
    )
    assert response.status_code == 400
    assert "CSV file is empty" in response.json()["detail"]
