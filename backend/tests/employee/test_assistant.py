import httpx


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


#  SUCCESS — 200 OK


def test_assistant_success(base_url, auth_employee, monkeypatch):
    """Mock Gemini API and ensure a successful chatbot response."""

    class MockResp:
        status_code = 200

        def json(self):
            return {
                "candidates": [
                    {"content": {"parts": [{"text": "Hello! I am your AI Assistant."}]}}
                ]
            }

    def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.post", mock_post)

    payload = {"message": "Hello assistant"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    assert r.status_code == 200
    data = assert_json(r)
    assert data["reply"] == "Hello! I am your AI Assistant."


#  422 — Missing Required Field


def test_assistant_missing_message_field(base_url, auth_employee):
    r = httpx.post(f"{base_url}/employee/assistant", json={}, headers=auth_employee)

    assert r.status_code == 422


# 401 / 403 Unauthorized


def test_assistant_unauthorized(base_url):
    payload = {"message": "Is WFH allowed?"}

    r = httpx.post(f"{base_url}/employee/assistant", json=payload)

    assert r.status_code in (401, 403)


#  500 — Gemini API non-200 response


def test_assistant_gemini_failure(base_url, auth_employee, monkeypatch):

    class MockResp:
        status_code = 500

        def json(self):
            return {"error": "Gemini failed"}

    def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.post", mock_post)

    payload = {"message": "Trigger error"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


#  500 — httpx exception (timeout, network err)


def test_assistant_timeout(base_url, auth_employee, monkeypatch):
    def boom(*a, **k):
        raise Exception("Timeout happened")

    monkeypatch.setattr("httpx.post", boom)

    payload = {"message": "Timeout test"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# 500 — Invalid Gemini response format


def test_assistant_invalid_response_format(base_url, auth_employee, monkeypatch):

    class MockResp:
        status_code = 200

        def json(self):
            return {"invalid": "data"}

    def mock_post(*a, **k):
        return MockResp()

    monkeypatch.setattr("httpx.post", mock_post)

    payload = {"message": "Invalid response test"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"
