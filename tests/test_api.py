"""Exercise API behavior without live Firestore writes or paid GPT calls."""

import copy
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import get_db
from app.main import app
from app.services.analyzer import calculate_summary


class Snapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self.data = copy.deepcopy(data)
        self.exists = data is not None

    def to_dict(self):
        return copy.deepcopy(self.data)


class Document:
    def __init__(self, store, doc_id):
        self.store = store
        self.id = doc_id

    def get(self):
        return Snapshot(self.id, self.store.get(self.id))

    def set(self, data):
        self.store[self.id] = copy.deepcopy(data)

    def update(self, data):
        self.store[self.id].update(copy.deepcopy(data))

    def delete(self):
        del self.store[self.id]


class Collection:
    def __init__(self):
        self.store = {}
        self.sequence = 0

    def document(self, doc_id=None):
        if doc_id is None:
            self.sequence += 1
            doc_id = f"doc-{self.sequence}"
        return Document(self.store, doc_id)

    def stream(self):
        return [Snapshot(key, value) for key, value in self.store.items()]


class Database:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return self.collections.setdefault(name, Collection())


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.client.close()

    def test_crud_and_summary(self):
        payload = {"date": "2026-10-01", "value": 4.5, "memo": "study"}
        response = self.client.post("/api/data", json=payload)
        self.assertEqual(response.status_code, 201)
        doc_id = response.json()["id"]
        self.assertEqual(
            self.client.get("/api/data").json()[0]["date"], payload["date"]
        )
        self.assertEqual(
            self.client.get("/api/data/summary").json()["count"], 1
        )
        updated = self.client.put(f"/api/data/{doc_id}", json={"value": 6})
        self.assertEqual(updated.json()["value"], 6)
        self.assertEqual(
            self.client.delete(f"/api/data/{doc_id}").status_code, 200
        )
        self.assertEqual(
            self.client.get("/api/data/summary").json()["count"], 0
        )
        self.assertEqual(
            self.client.delete(f"/api/data/{doc_id}").status_code, 404
        )

    def test_invalid_inputs_do_not_write(self):
        for payload in [
            {"date": "bad", "value": 1},
            {"date": "2026-02-30", "value": 1},
            {"date": "2026-01-01", "value": "NaN"},
            {"date": "2026-01-01", "value": "Infinity"},
        ]:
            self.assertEqual(
                self.client.post("/api/data", json=payload).status_code, 422
            )
        for payload in [{}, {"value": None}]:
            self.assertEqual(
                self.client.put("/api/data/x", json=payload).status_code, 422
            )
        self.assertEqual(
            self.client.post("/api/chat", json={"message": "  "}).status_code,
            422,
        )
        invalid = {
            "title": "x",
            "messages": [{"role": "system", "content": "x"}],
        }
        self.assertEqual(
            self.client.post("/api/conversations", json=invalid).status_code,
            422,
        )
        self.assertEqual(self.db.collection("data").store, {})

    def test_conversation_round_trip(self):
        payload = {
            "title": "Study",
            "messages": [{"role": "user", "content": "Hi"}],
        }
        response = self.client.post("/api/conversations", json=payload)
        self.assertEqual(response.status_code, 201)
        doc_id = response.json()["id"]
        self.assertEqual(
            self.client.get(f"/api/conversations/{doc_id}").json()["messages"],
            payload["messages"],
        )
        self.assertEqual(len(self.client.get("/api/conversations").json()), 1)
        self.client.delete(f"/api/conversations/{doc_id}")
        self.assertEqual(
            self.client.get(f"/api/conversations/{doc_id}").status_code, 404
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.routers.chat.OpenAI")
    def test_chat_context_save_and_continue(self, mock_openai):
        sdk = mock_openai.return_value.__enter__.return_value
        sdk.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="평균 4시간입니다.")
                )
            ]
        )
        self.client.post("/api/data", json={"date": "2026-10-01", "value": 4})
        response = self.client.post("/api/chat", json={"message": "평균?"})
        self.assertEqual(response.status_code, 200)
        doc_id = response.json()["conversation_id"]
        self.assertIn(
            '"average": 4.0',
            sdk.chat.completions.create.call_args.kwargs["messages"][0][
                "content"
            ],
        )
        self.client.post(
            "/api/chat", json={"message": "추세?", "conversation_id": doc_id}
        )
        saved = self.client.get(f"/api/conversations/{doc_id}").json()
        self.assertEqual(len(saved["messages"]), 4)
        missing = self.client.post(
            "/api/chat", json={"message": "x", "conversation_id": "missing"}
        )
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(sdk.chat.completions.create.call_count, 2)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.routers.chat.OpenAI")
    def test_failed_chat_does_not_save(self, mock_openai):
        sdk = mock_openai.return_value.__enter__.return_value
        sdk.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )
        self.assertEqual(
            self.client.post("/api/chat", json={"message": "Hi"}).status_code,
            502,
        )
        self.assertEqual(self.db.collection("conversations").store, {})

    def test_docs_without_credentials(self):
        self.assertEqual(self.client.get("/docs").status_code, 200)
        self.assertIn(
            "/api/chat", self.client.get("/openapi.json").json()["paths"]
        )


class SummaryTests(unittest.TestCase):
    def test_empty_single_and_negative_trend(self):
        self.assertEqual(calculate_summary([])["count"], 0)
        self.assertEqual(
            calculate_summary([{"date": "2026-01-01", "value": 2}])["trend"],
            "유지 추세",
        )
        items = [
            {"date": "2026-01-02", "value": -9},
            {"date": "2026-01-01", "value": -10},
        ]
        self.assertEqual(calculate_summary(items)["trend"], "상승 추세")
        self.assertEqual(
            calculate_summary(items)["metrics"]["standard_deviation"], 0.5
        )


if __name__ == "__main__":
    unittest.main()
