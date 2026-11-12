from datetime import date, timedelta
from fastapi.testclient import TestClient
from routers.exam_packs import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)

def test_preview_schedule_and_keyword_matches():
    response = client.post("/api/exam-packs/preview", json={
        "subject": "DBMS",
        "units": ["Normalization", "Transactions"],
        "exam_date": (date.today() + timedelta(days=3)).isoformat(),
        "previous_year_questions": ["Explain normalization up to BCNF"],
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["revision_schedule"]) == 3
    assert data["pyq_keyword_matches"][0]["matches"] == 1
    assert data["payment_required"] is False
    assert data["limitations"]

def test_rejects_empty_unit_and_oversized_inputs():
    response = client.post("/api/exam-packs/preview", json={
        "subject": "DBMS", "units": [""], "exam_date": date.today().isoformat()
    })
    assert response.status_code == 422

def test_past_exam_date_produces_one_immediate_task():
    response = client.post("/api/exam-packs/preview", json={
        "subject": "DBMS", "units": ["SQL"], "exam_date": (date.today() - timedelta(days=1)).isoformat()
    })
    assert response.status_code == 200
    assert len(response.json()["revision_schedule"]) == 1
