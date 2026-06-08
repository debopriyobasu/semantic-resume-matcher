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
