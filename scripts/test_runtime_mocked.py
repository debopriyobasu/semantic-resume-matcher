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
    def mock_httpx_post(url, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        url_str = str(url)
        if "embeddings" in url_str:
            mock_response.json.return_value = {"embedding": [0.1] * 768}
        elif "chat" in url_str:
            json_data = kwargs.get("json", {})
            messages = json_data.get("messages", [])
            prompt_content = ""
            if messages:
                prompt_content = messages[-1].get("content", "")
            if "strong fit" in prompt_content or "Evaluation criteria" in prompt_content or "candidate_profile" in prompt_content:
                mock_response.json.return_value = {
                    "message": {
                        "content": json.dumps(
                            {
                                "confidence": 0.95,
                                "match_category": "STRONG_MATCH",
                                "reasoning": "Excellent fit.",
                                "skill_gaps": [],
                                "standout_strengths": ["Python"],
                            }
                        )
                    }
                }
            else:
                mock_response.json.return_value = {
                    "message": {
                        "content": json.dumps(
                            {
                                "name": "Jane Doe",
                                "skills": ["Python", "FastAPI"],
                                "experience_years": 5,
                                "education": "BS CS",
                                "location": "Remote",
                            }
                        )
                    }
                }
        return mock_response

    # Setup mocks
    with patch("httpx.post", side_effect=mock_httpx_post):
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
