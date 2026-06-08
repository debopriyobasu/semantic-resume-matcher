import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.core.metrics import metrics_store
from src.main import app


def run():
    client = TestClient(app)

    print("\n--- METRICS BEFORE ---")
    resp_before = client.get("/metrics")
    print(json.dumps(resp_before.json(), indent=2))

    # Setup mocks
    with (
        patch("src.services.resume_parser.genai.Client") as mock_client_parser,
        patch(
            "src.services.embedding_service.EmbeddingService.generate_embedding"
        ) as mock_generate_embedding,
        patch("src.services.matchmaker_service.genai.Client") as mock_client_matchmaker,
    ):
        # Mock Parser
        mock_parser_instance = mock_client_parser.return_value
        mock_generate_content_parser = MagicMock()
        mock_generate_content_parser.text = json.dumps(
            {
                "name": "Jane Doe",
                "skills": ["Python", "FastAPI"],
                "experience_years": 5,
                "education": "BS CS",
                "location": "Remote",
            }
        )
        mock_parser_instance.models.generate_content.return_value = mock_generate_content_parser

        # Mock Embedder
        mock_generate_embedding.return_value = [0.1] * 768

        # Mock Matchmaker
        mock_matchmaker_instance = mock_client_matchmaker.return_value
        mock_generate_content_matchmaker = MagicMock()
        mock_generate_content_matchmaker.text = json.dumps(
            {
                "confidence": 0.95,
                "match_category": "STRONG_MATCH",
                "reasoning": "Excellent fit.",
                "skill_gaps": [],
                "standout_strengths": ["Python"],
            }
        )
        mock_matchmaker_instance.models.generate_content.return_value = (
            mock_generate_content_matchmaker
        )

        print("\n--- UPLOADING RESUME ---")
        with open("resume.pdf", "rb") as f:
            resp_upload = client.post(
                "/upload-resume", files={"file": ("resume.pdf", f, "application/pdf")}
            )

        upload_data = resp_upload.json()
        print("Upload Response:", json.dumps(upload_data, indent=2))

    print("\n--- METRICS AFTER ---")
    resp_after = client.get("/metrics")
    print(json.dumps(resp_after.json(), indent=2))


if __name__ == "__main__":
    # Ensure fresh state
    metrics_store._pipeline_durations.clear()
    metrics_store._embedding_durations.clear()
    for k in metrics_store._match_confidence_distribution:
        metrics_store._match_confidence_distribution[k] = 0
    for k in metrics_store._pipeline_status_counts:
        metrics_store._pipeline_status_counts[k] = 0
    for k in metrics_store._match_category_counts:
        metrics_store._match_category_counts[k] = 0

    run()
