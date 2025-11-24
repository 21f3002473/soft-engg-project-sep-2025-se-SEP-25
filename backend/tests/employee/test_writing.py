import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# LIST ALL QUICK NOTES (GET /employee/writing)

def test_list_quick_notes_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/writing", headers=headers)

    assert r.status_code == 200
    data = assert_json(r)
    assert "notes" in data
    assert isinstance(data["notes"], list)


def test_list_quick_notes_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/writing")
    assert r.status_code in [401, 403]


def test_list_quick_notes_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.exec",
        lambda *a, **k: (_ for _ in ()).throw(Exception("DB error")),
    )

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/writing", headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# CREATE QUICK NOTE (POST /employee/writing)

def test_create_quick_note_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Meeting Notes", "notes": "Discuss quarterly targets"}

    r = client.post(f"{BASE_URL}/employee/writing", json=payload, headers=headers)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "Note saved successfully"
    assert "id" in data


def test_create_quick_note_missing_notes_field(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Empty"}

    r = client.post(f"{BASE_URL}/employee/writing", json=payload, headers=headers)

    assert r.status_code == 422


def test_create_quick_note_unauthorized(client):
    payload = {"topic": "Hello", "notes": "Test note"}

    r = client.post(f"{BASE_URL}/employee/writing", json=payload)

    assert r.status_code in [401, 403]


def test_create_quick_note_internal_error(client, monkeypatch):
    def bad_commit(*a, **k):
        raise Exception("DB commit fail")

    monkeypatch.setattr("sqlmodel.Session.commit", bad_commit)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Crash", "notes": "Cause internal error"}

    r = client.post(f"{BASE_URL}/employee/writing", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# GET INDIVIDUAL QUICK NOTE (GET /employee/writing/{note_id})

def test_get_quick_note_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/writing/1", headers=headers)

    # Could be 200 or 404 depending on DB
    assert r.status_code in [200, 404]

    if r.status_code == 200:
        data = assert_json(r)
        assert "note" in data
        assert {"id", "topic", "notes"}.issubset(data["note"].keys())


def test_get_quick_note_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/writing/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_get_quick_note_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/writing/1")

    assert r.status_code in [401, 403]


# UPDATE QUICK NOTE (PUT /employee/writing/{note_id})

def test_update_quick_note_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Updated Topic", "notes": "Updated content"}

    r = client.put(f"{BASE_URL}/employee/writing/1", json=payload, headers=headers)

    assert r.status_code in [200, 404]

    if r.status_code == 200:
        assert assert_json(r)["message"] == "Note updated"


def test_update_quick_note_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Any", "notes": "Any"}

    r = client.put(f"{BASE_URL}/employee/writing/999999", json=payload, headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_update_quick_note_unauthorized(client):
    payload = {"topic": "X", "notes": "Y"}

    r = client.put(f"{BASE_URL}/employee/writing/1", json=payload)

    assert r.status_code in [401, 403]


def test_update_quick_note_internal_error(client, monkeypatch):
    def bad_commit(*a, **k):
        raise Exception("Commit failed")

    monkeypatch.setattr("sqlmodel.Session.commit", bad_commit)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"topic": "Try", "notes": "Crash"}

    r = client.put(f"{BASE_URL}/employee/writing/1", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# DELETE QUICK NOTE (DELETE /employee/writing/{note_id})

def test_delete_quick_note_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/writing/1", headers=headers)

    assert r.status_code in [200, 404]

    if r.status_code == 200:
        assert assert_json(r)["message"] == "Note deleted"


def test_delete_quick_note_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/writing/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_delete_quick_note_unauthorized(client):
    r = client.delete(f"{BASE_URL}/employee/writing/1")

    assert r.status_code in [401, 403]


def test_delete_quick_note_internal_error(client, monkeypatch):
    def bad_delete(*a, **k):
        raise Exception("Delete fail")

    monkeypatch.setattr("sqlmodel.Session.delete", bad_delete)

    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/writing/1", headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"