from unittest.mock import MagicMock, patch

import pytest
from pypdf.errors import PdfReadError

from src.core.exceptions import ResumeParseError
from src.services.resume_parser import ResumeParserService


@pytest.fixture
def parser():
    return ResumeParserService()


def test_extract_text_happy_path(parser):
    with patch("src.services.resume_parser.PdfReader") as MockReader:
        mock_pdf = MockReader.return_value

        mock_page_1 = MagicMock()
        mock_page_1.extract_text.return_value = "John Doe\nSoftware Engineer"
        mock_page_2 = MagicMock()
        mock_page_2.extract_text.return_value = "Experience: 5 years"

        mock_pdf.pages = [mock_page_1, mock_page_2]

        text = parser.extract_text(b"fake pdf bytes")

        assert "John Doe" in text
        assert "Software Engineer" in text
        assert "Experience: 5 years" in text


def test_extract_text_empty_bytes(parser):
    with pytest.raises(ResumeParseError, match="Empty PDF file"):
        parser.extract_text(b"")


def test_extract_text_no_pages(parser):
    with patch("src.services.resume_parser.PdfReader") as MockReader:
        mock_pdf = MockReader.return_value
        mock_pdf.pages = []

        with pytest.raises(ResumeParseError, match="PDF has no pages"):
            parser.extract_text(b"fake pdf bytes")


def test_extract_text_no_text(parser):
    with patch("src.services.resume_parser.PdfReader") as MockReader:
        mock_pdf = MockReader.return_value

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "   \n  "

        mock_pdf.pages = [mock_page]

        with pytest.raises(ResumeParseError, match="No text could be extracted"):
            parser.extract_text(b"fake pdf bytes")


def test_extract_text_corrupt_pdf(parser):
    with patch(
        "src.services.resume_parser.PdfReader", side_effect=PdfReadError("EOF marker not found")
    ):
        with pytest.raises(ResumeParseError, match="Corrupt or invalid PDF"):
            parser.extract_text(b"not a pdf")


@patch("httpx.post")
def test_extract_profile_happy_path(mock_post, parser):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "content": '{"name": "John Doe", "email": "john@example.com", "skills": ["Python"], "experience_years": 5, "education": "BSc", "location": "Remote"}'
        }
    }
    mock_post.return_value = mock_response

    profile = parser.extract_profile("fake resume text")

    assert profile.name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.skills == ["Python"]
    assert profile.experience_years == 5


@patch("httpx.post")
def test_extract_profile_validation_failure(mock_post, parser):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {"content": '{"name": {"first": "John"}, "experience_years": 5}'}
    }
    mock_post.return_value = mock_response

    with pytest.raises(ResumeParseError, match="Failed to validate extracted profile"):
        parser.extract_profile("fake text")


@patch("httpx.post")
def test_extract_profile_empty_response(mock_post, parser):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": {"content": ""}}
    mock_post.return_value = mock_response

    with pytest.raises(ResumeParseError, match="Failed to parse model response as JSON"):
        parser.extract_profile("fake text")
