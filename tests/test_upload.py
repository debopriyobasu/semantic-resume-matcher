import io
import os
import uuid
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.db.session import get_db
from src.models.candidate import Candidate

client = TestClient(app)

def override_get_db():
    db = Mock()
    def mock_add(obj):
        if getattr(obj, "candidate_id", None) is None:
            obj.candidate_id = uuid.uuid4()
    db.add.side_effect = mock_add
    db.refresh = Mock()
    yield db

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    os.makedirs("uploads", exist_ok=True)
    yield
    # Teardown: Remove uploaded test files
    for f in os.listdir("uploads"):
        if f.endswith(".pdf"):
            os.remove(os.path.join("uploads", f))

def test_upload_valid_pdf() -> None:
    file_content = b"%PDF-1.4\nMock content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/upload-resume",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "candidate_id" in data
    assert data["status"] == "PENDING"

def test_upload_duplicate_pdf() -> None:
    file_content = b"%PDF-1.4\nDuplicate mock content"
    
    # Upload 1
    file1 = io.BytesIO(file_content)
    response1 = client.post(
        "/upload-resume",
        files={"file": ("duplicate.pdf", file1, "application/pdf")}
    )
    assert response1.status_code == 200
    
    # Upload 2
    file2 = io.BytesIO(file_content)
    response2 = client.post(
        "/upload-resume",
        files={"file": ("duplicate.pdf", file2, "application/pdf")}
    )
    assert response2.status_code == 200
    
    c1 = response1.json()
    c2 = response2.json()
    assert c1["candidate_id"] != c2["candidate_id"]

def test_upload_invalid_mime_type() -> None:
    file_content = b"%PDF-1.4\nMock content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/upload-resume",
        files={"file": ("test.pdf", file, "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]

def test_upload_invalid_extension() -> None:
    file_content = b"%PDF-1.4\nMock content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/upload-resume",
        files={"file": ("test.txt", file, "application/pdf")}
    )
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]

def test_upload_invalid_magic_bytes() -> None:
    file_content = b"Not a PDF"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/upload-resume",
        files={"file": ("test.pdf", file, "application/pdf")}
    )
    assert response.status_code == 400
    assert "Invalid PDF file format" in response.json()["detail"]

def test_upload_exceeds_size_limit() -> None:
    # Creating a dummy file of 10MB + 10 bytes
    file_content = b"%PDF-1.4\n" + b"0" * (10 * 1024 * 1024)
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/upload-resume",
        files={"file": ("large.pdf", file, "application/pdf")}
    )
    assert response.status_code == 400
    assert "File size exceeds 10MB limit" in response.json()["detail"]
