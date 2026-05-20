import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402


FIXTURE_PATH = ROOT / "tests" / "fixtures" / "academic-sample.pdf"


def main() -> None:
    if not FIXTURE_PATH.exists():
        raise SystemExit(f"Missing fixture PDF: {FIXTURE_PATH}")

    client = TestClient(app)

    with FIXTURE_PATH.open("rb") as handle:
        upload_response = client.post(
            "/api/documents/upload",
            files={"file": ("academic-sample.pdf", handle, "application/pdf")},
        )

    if upload_response.status_code != 200:
        raise SystemExit(f"Upload failed: {upload_response.status_code} {upload_response.text}")

    upload_payload = upload_response.json()
    document_id = upload_payload["document_id"]

    answer_response = client.post(
        "/api/documents/answer",
        json={
            "document_id": document_id,
            "question": "How does normalization help in DBMS?",
            "top_k": 3,
        },
    )

    if answer_response.status_code != 200:
        raise SystemExit(f"Answer failed: {answer_response.status_code} {answer_response.text}")

    answer_payload = answer_response.json()
    if not answer_payload.get("citations"):
        raise SystemExit("Answer payload did not include citations.")
    if not answer_payload.get("answer", "").strip():
        raise SystemExit("Answer payload was empty.")

    summary = {
        "upload_status": upload_payload["status"],
        "retrieval_ready": upload_payload["retrieval_ready"],
        "answer_mode": answer_payload["answer_mode"],
        "generation_used": answer_payload["generation_used"],
        "confidence": answer_payload["confidence"],
        "citations_count": len(answer_payload["citations"]),
        "warning": answer_payload.get("warning"),
        "first_citation": answer_payload["citations"][0],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
