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


def test_extract_profile_happy_path(parser):
    with patch("src.services.resume_parser.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = '{"name": "John Doe", "email": "john@example.com", "skills": ["Python"], "experience_years": 5, "education": "BSc", "location": "Remote"}'
        mock_client.models.generate_content.return_value = mock_response

        profile = parser.extract_profile("fake resume text")

        assert profile.name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.skills == ["Python"]
        assert profile.experience_years == 5


def test_extract_profile_validation_failure(parser):
    with patch("src.services.resume_parser.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_response = MagicMock()
        # Missing skills which is a required list field, though it has default_factory it might just use it.
        # Let's send an invalid type for experience_years
        mock_response.text = '{"name": "John", "experience_years": "five years"}'
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ResumeParseError, match="Failed to validate extracted profile"):
            parser.extract_profile("fake text")


def test_extract_profile_empty_response(parser):
    with patch("src.services.resume_parser.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ResumeParseError, match="Received empty response from Gemini"):
            parser.extract_profile("fake text")
