import logging

from google import genai
from google.genai.errors import APIError

from src.core.config import get_settings

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
        try:
            from google.genai import types
            response = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=text,
                config=types.EmbedContentConfig(output_dimensionality=768),
            )
            # The genai SDK returns an EmbedContentResponse which has an embeddings list
            return response.embeddings[0].values
        except APIError as e:
            logger.error("Transient error generating embedding: %s", e)
            raise EmbeddingError(f"Transient error generating embedding: {e}") from e
        except Exception as e:
            logger.error("Failed to generate embedding: %s", e)
            raise EmbeddingError(f"Failed to generate embedding: {e}") from e
