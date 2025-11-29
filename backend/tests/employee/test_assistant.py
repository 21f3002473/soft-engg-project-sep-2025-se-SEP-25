import os

from dotenv import load_dotenv

load_dotenv()
import httpx


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# POST /employee/assistant  — SUCCESS (200 OK)


BASE_URL = os.getenv("BASE_URL")


def test_assistant_success(base_url, auth_employee):
    payload = {"message": "Hello assistant"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    if os.getenv("GEMINI_API_KEY"):
        assert r.status_code == 200
    else:
        assert r.status_code in [500]
    data = assert_json(r)
    if r.status_code == 200:
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0


# POST /employee/assistant  — 422 (Missing Required Field)


def test_assistant_missing_message_field(base_url, auth_employee):
    r = httpx.post(
        f"{base_url}/employee/assistant",
        json={},
        headers=auth_employee,
    )

    assert r.status_code == 422


# POST /employee/assistant  — 401/403 Unauthorized


def test_assistant_unauthorized(base_url):
    payload = {"message": "Is WFH allowed?"}

    r = httpx.post(f"{base_url}/employee/assistant", json=payload)

    assert r.status_code in (401, 403)


# GET /employee/assistant/history — SUCCESS (200 OK)


def test_assistant_history_success(base_url, auth_employee):
    """
    First send a message so the user has at least one chat entry,
    then fetch history and verify structure.
    """

    httpx.post(
        f"{base_url}/employee/assistant",
        json={"message": "Hello assistant"},
        headers=auth_employee,
    )

    r = httpx.get(f"{base_url}/employee/assistant/history", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)

    assert "messages" in data
    assert isinstance(data["messages"], list)

    for msg in data["messages"]:
        assert "id" in msg
        assert "role" in msg
        assert msg["role"] in ("user", "assistant")

        assert "message" in msg
        assert isinstance(msg["message"], str)

        assert "created_at" in msg


# GET /employee/assistant/history — EMPTY HISTORY (200 OK)


def test_assistant_history_empty(base_url, auth_employee, clear_chats_for_user=None):
    """
    Optional helper `clear_chats_for_user` can be used in your testing infra,
    otherwise this test checks behavior for a new/clean user session.
    """
    if clear_chats_for_user:
        clear_chats_for_user()

    r = httpx.get(f"{base_url}/employee/assistant/history", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)

    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert all(isinstance(m, dict) for m in data["messages"])


# GET /employee/assistant/history — Unauthorized


def test_assistant_history_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/assistant/history")

    assert r.status_code in (401, 403)
