import io
import json

from google import genai
from pydantic import ValidationError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.core.config import get_settings
from src.core.exceptions import ResumeParseError
from src.core.prompts import render_prompt
from src.schemas.candidate import CandidateProfile


class ResumeParserService:
    def extract_text(self, file_content: bytes) -> str:
        """
        Extracts text from a PDF file.

        Args:
            file_content: The binary content of the PDF file.

        Returns:
            The extracted text as a string.

        Raises:
            ResumeParseError: If the PDF is invalid, empty, or corrupt.
        """
        if not file_content:
            raise ResumeParseError("Empty PDF file.")

        try:
            reader = PdfReader(io.BytesIO(file_content))

            if not reader.pages:
                raise ResumeParseError("PDF has no pages.")

            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

            extracted_text = extracted_text.strip()

            if not extracted_text:
                raise ResumeParseError("No text could be extracted from the PDF.")

            return extracted_text

        except PdfReadError as e:
            raise ResumeParseError(f"Corrupt or invalid PDF file: {str(e)}") from e
        except ResumeParseError:
            raise
        except Exception as e:
            raise ResumeParseError(f"Error parsing PDF: {str(e)}") from e

    def extract_profile(self, text: str) -> CandidateProfile:
        """
        Extracts a structured CandidateProfile from resume text using Gemini.

        Args:
            text: The text extracted from the resume.

        Returns:
            A structured CandidateProfile.

        Raises:
            ResumeParseError: If Gemini extraction or validation fails.
        """
        try:
            settings = get_settings()
            client = genai.Client(api_key=settings.google_api_key)
            prompt = render_prompt("resume_extraction.md", {"resume_text": text})

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            if not response.text:
                raise ResumeParseError("Received empty response from Gemini.")

            # Remove any markdown JSON block wrapping if present
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            profile_data = json.loads(response_text)
            profile = CandidateProfile(**profile_data)
            return profile

        except json.JSONDecodeError as e:
            raise ResumeParseError(f"Failed to parse Gemini response as JSON: {e}") from e
        except ValidationError as e:
            raise ResumeParseError(f"Failed to validate extracted profile: {e}") from e
        except ResumeParseError:
            raise
        except Exception as e:
            raise ResumeParseError(f"Error during Gemini extraction: {e}") from e
