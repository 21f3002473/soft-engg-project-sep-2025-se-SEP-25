import httpx
import pytest


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# LIST ALL QUICK NOTES (GET /employee/writing)
def test_list_quick_notes_success(auth_employee, base_url):
    r = httpx.get(f"{base_url}/employee/writing", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)
    assert "notes" in data
    assert isinstance(data["notes"], list)


def test_list_quick_notes_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/writing")
    assert r.status_code in [401, 403]


# CREATE QUICK NOTE (POST /employee/writing)
def test_create_quick_note_success(auth_employee, base_url):
    payload = {"topic": "Meeting Notes", "notes": "Discuss quarterly targets"}

    r = httpx.post(f"{base_url}/employee/writing", json=payload, headers=auth_employee)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "Note saved successfully"
    assert "id" in data


def test_create_quick_note_missing_notes_field(auth_employee, base_url):
    payload = {"topic": "Empty"}

    r = httpx.post(f"{base_url}/employee/writing", json=payload, headers=auth_employee)

    assert r.status_code == 422


def test_create_quick_note_unauthorized(base_url):
    payload = {"topic": "Hello", "notes": "Test note"}

    r = httpx.post(f"{base_url}/employee/writing", json=payload)

    assert r.status_code in [401, 403]


# GET /employee/writing/{note_id}
def test_get_quick_note_success(auth_employee, base_url):
    list_resp = httpx.get(f"{base_url}/employee/writing", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    notes = data.get("notes", [])

    if not notes:
        pytest.skip("No notes available to test GET")

    note_id = notes[0]["id"]
    r = httpx.get(f"{base_url}/employee/writing/{note_id}", headers=auth_employee)

    assert r.status_code == 200
    response_data = assert_json(r)
    assert "note" in response_data
    assert {"id", "topic", "notes"}.issubset(response_data["note"].keys())


def test_get_quick_note_not_found(auth_employee, base_url):
    r = httpx.get(f"{base_url}/employee/writing/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_get_quick_note_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/writing/1")
    assert r.status_code in [401, 403]


# PUT /employee/writing/{note_id}
def test_update_quick_note_success(auth_employee, base_url):
    list_resp = httpx.get(f"{base_url}/employee/writing", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    notes = data.get("notes", [])

    if not notes:
        pytest.skip("No notes available to test PUT")

    note_id = notes[0]["id"]
    payload = {"topic": "Updated Topic", "notes": "Updated content"}

    r = httpx.put(
        f"{base_url}/employee/writing/{note_id}", json=payload, headers=auth_employee
    )

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Note updated"


def test_update_quick_note_not_found(auth_employee, base_url):
    payload = {"topic": "Any", "notes": "Any"}

    r = httpx.put(
        f"{base_url}/employee/writing/999999", json=payload, headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_update_quick_note_unauthorized(base_url):
    payload = {"topic": "X", "notes": "Y"}

    r = httpx.put(f"{base_url}/employee/writing/1", json=payload)
    assert r.status_code in [401, 403]


# DELETE /employee/writing/{note_id}
def test_delete_quick_note_success(auth_employee, base_url):
    list_resp = httpx.get(f"{base_url}/employee/writing", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    notes = data.get("notes", [])

    if not notes:
        pytest.skip("No notes available to test DELETE")

    note_id = notes[0]["id"]
    r = httpx.delete(f"{base_url}/employee/writing/{note_id}", headers=auth_employee)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Note deleted"


def test_delete_quick_note_not_found(auth_employee, base_url):
    r = httpx.delete(f"{base_url}/employee/writing/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Note not found"


def test_delete_quick_note_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/employee/writing/1")
    assert r.status_code in [401, 403]
