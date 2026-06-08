import logging
import time

from google import genai
from google.genai.errors import APIError

from src.core.config import get_settings
from src.core.metrics import metrics_store
from src.models.candidate import Candidate

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Exception raised for errors in the embedding service."""

    pass


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.google_api_key)

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding for the given text using gemini-embedding-2 model truncated to 768 dimensions."""
        start_time = time.perf_counter()
        try:
            from google.genai import types

            response = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768),
            )
            # The genai SDK returns an EmbedContentResponse which has an embeddings list
            duration = time.perf_counter() - start_time
            metrics_store.record_embedding_duration(duration)
            return response.embeddings[0].values
        except APIError as e:
            logger.error("Transient error generating embedding: %s", e)
            raise EmbeddingError(f"Transient error generating embedding: {e}") from e
        except Exception as e:
            logger.error("Failed to generate embedding: %s", e)
            raise EmbeddingError(f"Failed to generate embedding: {e}") from e

    def build_candidate_text(self, candidate: Candidate) -> str:
        """Build embedding text representation for a candidate."""
        parts = []
        if candidate.skills:
            parts.append("Skills:\n" + "\n".join(candidate.skills))
        if candidate.experience_years is not None:
            parts.append(
                f"Experience:\n{candidate.experience_years} years backend engineering"
            )  # Note: The prompt example had "5 years backend engineering", maybe it just means "years" but let's just use "years" or what's given.
        if candidate.education:
            parts.append(f"Education:\n{candidate.education}")
        if candidate.location:
            parts.append(f"Location:\n{candidate.location}")
        return "\n\n".join(parts)

    def generate_candidate_embedding(self, candidate: Candidate) -> list[float]:
        """Generate an embedding for a candidate."""
        text = self.build_candidate_text(candidate)
        return self.generate_embedding(text)
