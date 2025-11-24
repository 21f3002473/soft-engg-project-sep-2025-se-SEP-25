import pytest
import requests

BASE_URL = "http://localhost:8000/api"


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# HR FAQ CREATE  (POST /hr/faq)


def test_hr_faq_create_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {
        "question": "What is the leave policy?",
        "answer": "Employees get 20 days of leave.",
    }

    r = client.post(f"{BASE_URL}/hr/faq", json=payload, headers=headers)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "FAQ created successfully"
    assert "id" in data


def test_hr_faq_create_missing_field(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"question": "Missing answer"}

    r = client.post(f"{BASE_URL}/hr/faq", json=payload, headers=headers)

    assert r.status_code == 422  # Pydantic validation
    # FastAPI returns validation error in standard format


def test_hr_faq_create_unauthorized(client):
    payload = {"question": "Test?", "answer": "Test!"}

    r = client.post(f"{BASE_URL}/hr/faq", json=payload)

    assert r.status_code in [401, 403]


def test_hr_faq_create_internal_error(client, monkeypatch):
    def bad_add(*a, **kw):
        raise Exception("DB FAIL")

    monkeypatch.setattr("sqlmodel.Session.add", bad_add)

    headers = {"Authorization": "Bearer hr_token"}
    payload = {"question": "Q?", "answer": "A"}

    r = client.post(f"{BASE_URL}/hr/faq", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# FAQ DETAIL GET (GET /hr/faq/{id})  – Employee allowed


def test_faq_detail_get_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/hr/faq/1", headers=headers)

    assert r.status_code in [200, 404]
    if r.status_code == 200:
        data = assert_json(r)
        assert "faq" in data
        assert {"id", "question", "answer"}.issubset(data["faq"].keys())


def test_faq_detail_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/hr/faq/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_detail_unauthorized(client):
    r = client.get(f"{BASE_URL}/hr/faq/1")
    assert r.status_code in [401, 403]


# UPDATE FAQ (PUT /hr/faq/{id})


def test_faq_update_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"question": "Updated Q?", "answer": "Updated A."}

    r = client.put(f"{BASE_URL}/hr/faq/1", json=payload, headers=headers)

    assert r.status_code in [200, 404]
    if r.status_code == 200:
        assert assert_json(r)["message"] == "FAQ updated successfully"


def test_faq_update_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"question": "Anything?", "answer": "Anything!"}

    r = client.put(f"{BASE_URL}/hr/faq/999999", json=payload, headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_update_unauthorized(client):
    payload = {"question": "No auth", "answer": "No auth answer"}

    r = client.put(f"{BASE_URL}/hr/faq/1", json=payload)
    assert r.status_code in [401, 403]


def test_faq_update_internal_error(client, monkeypatch):
    def bad_commit(*a, **kw):
        raise Exception("Commit fail")

    monkeypatch.setattr("sqlmodel.Session.commit", bad_commit)

    headers = {"Authorization": "Bearer hr_token"}
    payload = {"question": "Q", "answer": "A"}

    r = client.put(f"{BASE_URL}/hr/faq/1", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# DELETE FAQ (DELETE /hr/faq/{id})


def test_faq_delete_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    r = client.delete(f"{BASE_URL}/hr/faq/1", headers=headers)

    assert r.status_code in [200, 404]
    if r.status_code == 200:
        assert assert_json(r)["message"] == "FAQ deleted successfully"


def test_faq_delete_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    r = client.delete(f"{BASE_URL}/hr/faq/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_delete_unauthorized(client):
    r = client.delete(f"{BASE_URL}/hr/faq/1")
    assert r.status_code in [401, 403]


def test_faq_delete_internal_error(client, monkeypatch):
    def bad_delete(*a, **kw):
        raise Exception("Delete failed")

    monkeypatch.setattr("sqlmodel.Session.delete", bad_delete)

    headers = {"Authorization": "Bearer hr_token"}
    r = client.delete(f"{BASE_URL}/hr/faq/1", headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# LIST ALL FAQS (GET /employee/hr-faqs)


def test_employee_list_faqs_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/hr-faqs", headers=headers)

    assert r.status_code == 200
    data = assert_json(r)
    assert "faqs" in data
    assert isinstance(data["faqs"], list)


def test_employee_list_faqs_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/hr-faqs")
    assert r.status_code in [401, 403]


def test_employee_list_faqs_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.exec",
        lambda *a, **b: (_ for _ in ()).throw(Exception("DB error")),
    )

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/hr-faqs", headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"
