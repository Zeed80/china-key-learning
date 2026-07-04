import os
import tempfile

db_path = os.path.join(tempfile.gettempdir(), "china_key_learning_test.sqlite3")
if os.path.exists(db_path):
    os.remove(db_path)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.content_audit import audit_seed_data  # noqa: E402
from app.db.seed import run_seed  # noqa: E402
from app.main import app  # noqa: E402


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin12345"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_mvp_api_flow() -> None:
    audit = audit_seed_data()
    assert audit["radicals"] == 214
    assert audit["examples"] >= 214
    assert audit["confusables"] >= 214

    run_seed("admin@example.com", "admin12345")
    client = TestClient(app)
    headers = auth_headers(client)

    assert client.get("/health").json() == {"status": "ok"}

    radicals = client.get("/radicals", headers=headers)
    assert radicals.status_code == 200
    radical_items = radicals.json()
    assert len(radical_items) == 214
    assert radical_items[0]["character"] == "一"
    assert 'role="img"' in radical_items[0]["asset_svg"]
    assert "<title>" in radical_items[0]["asset_svg"]
    water_item = next(item for item in radical_items if item["number"] == 85)
    water_detail = client.get(f"/radicals/{water_item['id']}", headers=headers)
    assert water_detail.status_code == 200
    water_examples = water_detail.json()["examples"]
    assert len(water_examples) >= 3
    assert any("Разбор:" in example["note_ru"] for example in water_examples)
    assert all(example["sentence_zh"] and example["sentence_ru"] for example in water_examples)

    checked = 0
    for item in radical_items:
        detail = client.get(f"/radicals/{item['id']}", headers=headers)
        assert detail.status_code == 200
        payload = detail.json()
        assert payload["examples"], payload["number"]
        assert payload["confusables"], payload["number"]
        assert all(example["sentence_zh"] and example["sentence_ru"] for example in payload["examples"])
        checked += 1
    assert checked == 214

    overview = client.get("/study/overview/next", headers=headers)
    assert overview.status_code == 200
    overview_radical = overview.json()
    assert overview_radical["number"] == 1

    seen = client.post("/study/overview/seen", headers=headers, json={"radical_id": overview_radical["id"]})
    assert seen.status_code == 200

    question = client.post("/training/next", headers=headers)
    assert question.status_code == 200
    question_payload = question.json()
    assert len(question_payload["options"]) >= 3

    selected = question_payload["options"][0]["radical_id"]
    answer = client.post(
        "/training/answer",
        headers=headers,
        json={"radical_id": question_payload["radical"]["id"], "selected_radical_id": selected},
    )
    assert answer.status_code == 200
    answer_payload = answer.json()
    assert "mastery" in answer_payload
    assert answer_payload["next_question"] is None

    exam = client.post("/exams/start", headers=headers)
    assert exam.status_code == 200
    exam_payload = exam.json()
    assert exam_payload["total"] == 20
    assert exam_payload["question"] is not None
    exam_answer = client.post(
        f"/exams/{exam_payload['attempt_id']}/answer",
        headers=headers,
        json={
            "radical_id": exam_payload["question"]["radical"]["id"],
            "selected_radical_id": exam_payload["question"]["options"][0]["radical_id"],
        },
    )
    assert exam_answer.status_code == 200
    exam_answer_payload = exam_answer.json()
    assert "is_correct" not in exam_answer_payload
    assert "correct_radical_id" not in exam_answer_payload

    updated = client.patch(
        f"/admin/radicals/{overview_radical['id']}",
        headers=headers,
        json={"status": "reviewed", "meaning_ru": "единица; горизонтальная черта"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "reviewed"

    summary = client.get("/progress/summary", headers=headers)
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["total_radicals"] == 214
    assert "learning_score_10" in summary_payload
    assert "remembered_count" in summary_payload
