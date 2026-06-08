from fastapi.testclient import TestClient

from src.core.metrics import metrics_store
from src.main import app

client = TestClient(app)


def test_metrics_endpoint():
    # Reset singleton to clear shared state from other tests
    metrics_store.__init__()

    # Record some mock data
    metrics_store.record_pipeline_duration(5.0)
    metrics_store.record_pipeline_duration(10.0)
    metrics_store.record_embedding_duration(2.0)
    metrics_store.record_match_confidence(0.9)
    metrics_store.increment_pipeline_status("COMPLETE")
    metrics_store.increment_match_category("STRONG_MATCH")

    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["pipeline_duration_seconds"]["count"] >= 2
    assert data["pipeline_duration_seconds"]["total_seconds"] >= 15.0
    assert data["pipeline_duration_seconds"]["average_seconds"] >= 7.5

    assert data["embedding_duration_seconds"]["count"] >= 1
    assert data["embedding_duration_seconds"]["total_seconds"] >= 2.0

    assert data["match_confidence_distribution"]["0.8-1.0"] >= 1
    assert data["pipeline_status_counts"]["COMPLETE"] >= 1
    assert data["match_category_counts"]["STRONG_MATCH"] >= 1
