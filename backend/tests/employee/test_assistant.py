import pytest
import requests

BASE_URL = "http://localhost:8000/api"


@pytest.fixture
def client():
    return requests


def assert_json(resp):
    assert "application/json" in resp.headers.get("Content-Type", "")
    return resp.json()


# SUCCESS — 200 OK


def test_assistant_success(monkeypatch, client):
    """Mock Gemini API and ensure a successful chatbot response."""

    class MockResp:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "Hello! I am your AI Assistant."}]}}
                ]
            }

    async def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"message": "Hello assistant"}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload, headers=headers)

    assert r.status_code == 200
    data = assert_json(r)
    assert "reply" in data
    assert data["reply"] == "Hello! I am your AI Assistant."


# 422 — Missing Required Field


def test_assistant_missing_message_field(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload, headers=headers)

    assert r.status_code == 422


# 401/403 — Unauthorized Access


def test_assistant_unauthorized(client):
    """No Authorization header → require_employee() rejects the request."""

    payload = {"message": "Is WFH allowed?"}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload)

    assert r.status_code in (401, 403)


# 500 — Gemini API non-200 response


def test_assistant_gemini_failure(monkeypatch, client):
    """Gemini API returns 500 → endpoint returns 500."""

    class MockResp:
        status_code = 500

        def text(self):
            return "Error"

    async def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"message": "Trigger error"}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# 500 — Timeout or Exception in httpx


def test_assistant_timeout(monkeypatch, client):
    """Exception raised by httpx → returns 500."""

    async def boom(*a, **k):
        raise Exception("Timeout happened")

    monkeypatch.setattr("httpx.AsyncClient.post", boom)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"message": "Timeout test"}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# 500 — Invalid Gemini Response Structure


def test_assistant_invalid_response_format(monkeypatch, client):
    """Missing expected keys → KeyError → endpoint returns 500."""

    class MockResp:
        status_code = 200

        def json(self):
            return {"invalid": "data"}

    async def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"message": "Invalid response test"}

    r = client.post(f"{BASE_URL}/employee/assistant", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"
