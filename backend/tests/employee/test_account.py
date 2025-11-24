import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    return requests


def assert_json(resp):
    assert "application/json" in resp.headers.get("Content-Type", "")
    return resp.json()


# GET /employee/account


def test_account_get_success(monkeypatch, client):
    """Return account info successfully."""

    class MockUser:
        id = 1
        name = "Alice"
        email = "alice@example.com"
        role = "employee"
        department_id = None
        reporting_manager = None
        img_base64 = None

    def mock_require_employee():
        return lambda: MockUser()

    monkeypatch.setattr("app.middleware.require_employee", mock_require_employee)

    headers = {"Authorization": "Bearer employee_token"}

    r = client.get(f"{BASE_URL}/employee/account", headers=headers)

    assert r.status_code == 200
    data = assert_json(r)

    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "employee"


def test_account_get_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/account")
    assert r.status_code in (401, 403)


def test_account_get_failure(monkeypatch, client):
    """Simulate database error -> return 500."""

    def boom(*a, **k):
        raise Exception("DB error")

    monkeypatch.setattr("sqlmodel.Session.get", boom)

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/account", headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# PUT /employee/account


def test_account_update_success(monkeypatch, client):
    """Successfully update partial account fields."""

    class MockUser:
        id = 1
        name = "Old Name"
        email = "old@example.com"
        role = "employee"
        department_id = None
        reporting_manager = None
        img_base64 = None

    def mock_require_employee():
        return lambda: MockUser()

    class FakeSession:
        def merge(self, u):
            return u

        def commit(self): ...
        def refresh(self, u): ...

    monkeypatch.setattr("app.middleware.require_employee", mock_require_employee)
    monkeypatch.setattr("app.database.get_session", lambda: FakeSession())

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"name": "New Name"}

    r = client.put(f"{BASE_URL}/employee/account", json=payload, headers=headers)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Account updated successfully"


def test_account_update_validation_error(client):
    """Missing required format leads to 422 (Pydantic)."""

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"email": 12345}  # invalid format

    r = client.put(f"{BASE_URL}/employee/account", json=payload, headers=headers)

    assert r.status_code == 422


def test_account_update_unauthorized(client):
    payload = {"name": "xyz"}
    r = client.put(f"{BASE_URL}/employee/account", json=payload)
    assert r.status_code in (401, 403)


def test_account_update_failure(monkeypatch, client):
    """Any exception → return 500."""

    class FakeSession:
        def merge(self, u):
            return u

        def commit(self):
            raise Exception("Update fail")

    monkeypatch.setattr("app.database.get_session", lambda: FakeSession())

    headers = {"Authorization": "Bearer employee_token"}
    payload = {"name": "Crash Test"}

    r = client.put(f"{BASE_URL}/employee/account", json=payload, headers=headers)

    assert r.status_code == 500
    assert assert_json(r)["detail"] == "Internal server error"


# DELETE /employee/account


def test_account_logout_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/account", headers=headers)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Logged out successfully"


def test_account_logout_unauthorized(client):
    r = client.delete(f"{BASE_URL}/employee/account")
    assert r.status_code in (401, 403)
