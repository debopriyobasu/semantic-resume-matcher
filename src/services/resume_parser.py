import io
import json
import httpx

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
        Extracts a structured CandidateProfile from resume text using Gemini or Ollama.

        Args:
            text: The text extracted from the resume.

        Returns:
            A structured CandidateProfile.

        Raises:
            ResumeParseError: If extraction or validation fails.
        """
        try:
            settings = get_settings()
            prompt = render_prompt("resume_extraction.md", {"resume_text": text})

            if settings.use_ollama:
                try:
                    response = httpx.post(
                        f"{settings.ollama_base_url}/api/chat",
                        json={
                            "model": settings.ollama_llm_model,
                            "messages": [{"role": "user", "content": prompt}],
                            "stream": False,
                            "options": {"temperature": 0.0},
                            "format": "json",
                        },
                        timeout=60.0,
                    )
                    response.raise_for_status()
                    response_json = response.json()
                    response_text = response_json["message"]["content"]
                except Exception as e:
                    raise ResumeParseError(f"Error during Ollama extraction: {e}") from e
            else:
                client = genai.Client(api_key=settings.google_api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                if not response.text:
                    raise ResumeParseError("Received empty response from Gemini.")
                response_text = response.text

            # Remove any markdown JSON block wrapping if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            profile_data = json.loads(response_text)

            # Sanitize experience_years
            exp = profile_data.get("experience_years")
            if exp is not None and not isinstance(exp, int):
                try:
                    profile_data["experience_years"] = int(float(exp))
                except (ValueError, TypeError):
                    if isinstance(exp, str):
                        import re
                        digits = re.findall(r"\d+", exp)
                        if digits:
                            profile_data["experience_years"] = int(digits[0])
                        elif "-" in exp or "to" in exp:
                            # e.g., "2018 - Present" or "2018 to 2023"
                            parts = re.findall(r"\b\d{4}\b", exp)
                            if parts:
                                start_year = int(parts[0])
                                # Assume current year is 2026
                                profile_data["experience_years"] = max(0, 2026 - start_year)
                            else:
                                profile_data["experience_years"] = None
                        else:
                            profile_data["experience_years"] = None
                    else:
                        profile_data["experience_years"] = None

            # Sanitize education
            edu = profile_data.get("education")
            if edu is not None and not isinstance(edu, str):
                if isinstance(edu, dict):
                    edu_parts = []
                    for k, v in edu.items():
                        if isinstance(v, list):
                            v_str = ", ".join(str(x) for x in v)
                        else:
                            v_str = str(v)
                        edu_parts.append(f"{k}: {v_str}")
                    profile_data["education"] = "; ".join(edu_parts)
                elif isinstance(edu, list):
                    profile_data["education"] = ", ".join(str(x) for x in edu)
                else:
                    profile_data["education"] = str(edu)

            # Sanitize skills
            skills = profile_data.get("skills")
            if skills is not None and not isinstance(skills, list):
                if isinstance(skills, str):
                    import re
                    profile_data["skills"] = [s.strip() for s in re.split(r"[,;]+", skills) if s.strip()]
                else:
                    profile_data["skills"] = []

            profile = CandidateProfile(**profile_data)
            return profile

        except json.JSONDecodeError as e:
            raise ResumeParseError(f"Failed to parse model response as JSON: {e}") from e
        except ValidationError as e:
            raise ResumeParseError(f"Failed to validate extracted profile: {e}") from e
        except ResumeParseError:
            raise
        except Exception as e:
            raise ResumeParseError(f"Error during model extraction: {e}") from e
