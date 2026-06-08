import json

from fastapi.testclient import TestClient

from src.main import app


def run():
    client = TestClient(app)

    # 5. Metrics before upload
    print("\n--- METRICS BEFORE ---")
    resp_before = client.get("/metrics")
    print(json.dumps(resp_before.json(), indent=2))

    # Upload resume
    print("\n--- UPLOADING RESUME ---")
    with open("resume.pdf", "rb") as f:
        resp_upload = client.post(
            "/upload-resume", files={"file": ("resume.pdf", f, "application/pdf")}
        )

    upload_data = resp_upload.json()
    print("Upload Response:", json.dumps(upload_data, indent=2))

    upload_data.get("candidate_id")

    # 5. Metrics after upload (wait a bit if background task was running, but TestClient runs background tasks synchronously after returning response)
    # Actually, Starlette TestClient executes background tasks before returning the response!
    # So pipeline should be fully complete.

    print("\n--- METRICS AFTER ---")
    resp_after = client.get("/metrics")
    print(json.dumps(resp_after.json(), indent=2))


if __name__ == "__main__":
    run()
