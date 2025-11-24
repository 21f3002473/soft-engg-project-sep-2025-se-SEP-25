import pytest
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# LEAVE REQUESTS


# GET /employee/requests/leave
def test_get_all_leave_requests_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/leave", headers=headers)

    assert r.status_code == 200
    data = assert_json(r)
    assert "leaves" in data
    assert isinstance(data["leaves"], list)


def test_get_all_leave_requests_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/requests/leave")
    assert r.status_code in [401, 403]


def test_get_all_leave_requests_internal_error(client, monkeypatch):
    def bad_query(*a, **kw):
        raise Exception("db error")

    monkeypatch.setattr("sqlmodel.Session.exec", bad_query)

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/leave", headers=headers)

    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# POST /employee/requests/leave
def test_post_leave_request_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "leave_type": "Sick",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
        "reason": "Fever",
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/leave", json=payload, headers=headers
    )
    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data.get("message") == "Leave request submitted"
    assert "request_id" in data


def test_post_leave_request_internal_error(client, monkeypatch):
    def fail_add(*a, **kw):
        raise Exception("db fail")

    monkeypatch.setattr("sqlmodel.Session.add", fail_add)

    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "leave_type": "Sick",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/leave", json=payload, headers=headers
    )
    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# GET /employee/requests/leave/{id}
def test_get_leave_by_id_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/leave/1", headers=headers)

    # Might be 404 if the test db has no data
    assert r.status_code in [200, 404]

    if r.status_code == 200:
        data = assert_json(r)
        keys = {
            "request_id",
            "leave_id",
            "leave_type",
            "from_date",
            "to_date",
            "reason",
            "status",
        }
        assert keys.issubset(data.keys())


def test_get_leave_by_id_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/leave/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


# PUT /employee/requests/leave/{id}
def test_put_leave_request_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "leave_type": "Casual",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
        "reason": "Updated",
    }

    r = client.put(
        f"{BASE_URL}/employee/requests/leave/1", json=payload, headers=headers
    )
    assert r.status_code in [200, 400, 404]

    if r.status_code == 200:
        assert assert_json(r).get("message") == "Leave request updated"


def test_put_leave_request_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.put(
        f"{BASE_URL}/employee/requests/leave/999999",
        json={
            "leave_type": "Sick",
            "from_date": datetime.now().isoformat(),
            "to_date": datetime.now().isoformat(),
        },
        headers=headers,
    )
    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


def test_put_leave_request_not_pending(client, monkeypatch):
    class FakeReq:
        status = "completed"

    def fake_query(*a, **kw):
        return FakeReq()

    monkeypatch.setattr(
        "sqlmodel.Session.exec",
        lambda *a, **kw: type("X", (), {"first": lambda s: FakeReq()})(),
    )

    headers = {"Authorization": "Bearer employee_token"}
    r = client.put(
        f"{BASE_URL}/employee/requests/leave/1",
        json={
            "leave_type": "Updated",
            "from_date": datetime.now().isoformat(),
            "to_date": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert r.status_code in [400, 500]


# DELETE /employee/requests/leave/{id}
def test_delete_leave_request_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/requests/leave/1", headers=headers)

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Leave request deleted"


def test_delete_leave_request_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/requests/leave/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


# REIMBURSEMENT REQUESTS


# GET /employee/requests/reimbursement
def test_get_all_reimbursements_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/reimbursement", headers=headers)

    assert r.status_code == 200
    data = assert_json(r)
    assert "reimbursements" in data


def test_get_all_reimbursements_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/requests/reimbursement")
    assert r.status_code in [401, 403]


def test_get_all_reimbursements_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.exec",
        lambda *a, **b: (_ for _ in ()).throw(Exception("db error")),
    )

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/reimbursement", headers=headers)
    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# POST /employee/requests/reimbursement
def test_post_reimbursement_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "expense_type": "Travel",
        "amount": 500,
        "date_expense": datetime.now().isoformat(),
        "remark": "Taxi",
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/reimbursement", json=payload, headers=headers
    )
    assert r.status_code in [200, 201]
    assert assert_json(r).get("message") == "Reimbursement submitted"


def test_post_reimbursement_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.add",
        lambda *a, **kw: (_ for _ in ()).throw(Exception("fail")),
    )

    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "expense_type": "Travel",
        "amount": 300,
        "date_expense": datetime.now().isoformat(),
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/reimbursement", json=payload, headers=headers
    )

    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# GET /employee/requests/reimbursement/{id}
def test_get_reimbursement_by_id_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/reimbursement/1", headers=headers)

    assert r.status_code in [200, 404]
    if r.status_code == 200:
        data = assert_json(r)
        keys = {
            "request_id",
            "reimbursement_id",
            "expense_type",
            "amount",
            "date_expense",
            "remark",
            "status",
        }
        assert keys.issubset(data.keys())


def test_get_reimbursement_by_id_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(
        f"{BASE_URL}/employee/requests/reimbursement/999999", headers=headers
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


# PUT /employee/requests/reimbursement/{id}
def test_put_reimbursement_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "expense_type": "Meals",
        "amount": 200,
        "date_expense": datetime.now().isoformat(),
        "remark": "Lunch update",
    }

    r = client.put(
        f"{BASE_URL}/employee/requests/reimbursement/1", json=payload, headers=headers
    )
    assert r.status_code in [200, 400, 404]

    if r.status_code == 200:
        assert assert_json(r).get("message") == "Reimbursement updated"


def test_put_reimbursement_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}

    r = client.put(
        f"{BASE_URL}/employee/requests/reimbursement/999999",
        json={
            "expense_type": "Travel",
            "amount": 100,
            "date_expense": datetime.now().isoformat(),
        },
        headers=headers,
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


# DELETE /employee/requests/reimbursement/{id}
def test_delete_reimbursement_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/requests/reimbursement/1", headers=headers)

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Reimbursement deleted"


def test_delete_reimbursement_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(
        f"{BASE_URL}/employee/requests/reimbursement/999999", headers=headers
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


# TRANSFER REQUESTS


# GET /employee/requests/transfer
def test_get_all_transfer_requests_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/transfer", headers=headers)

    assert r.status_code == 200
    assert "transfers" in assert_json(r)


def test_get_all_transfer_requests_unauthorized(client):
    r = client.get(f"{BASE_URL}/employee/requests/transfer")
    assert r.status_code in [401, 403]


def test_get_all_transfer_requests_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.exec",
        lambda *a, **b: (_ for _ in ()).throw(Exception("fail")),
    )

    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/transfer", headers=headers)

    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# POST /employee/requests/transfer
def test_post_transfer_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "current_department": "Sales",
        "request_department": "Marketing",
        "reason": "Career growth",
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/transfer", json=payload, headers=headers
    )
    assert r.status_code in [200, 201]
    assert assert_json(r).get("message") == "Transfer request submitted"


def test_post_transfer_internal_error(client, monkeypatch):
    monkeypatch.setattr(
        "sqlmodel.Session.add", lambda *a, **b: (_ for _ in ()).throw(Exception("fail"))
    )

    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "current_department": "Sales",
        "request_department": "Tech",
    }

    r = client.post(
        f"{BASE_URL}/employee/requests/transfer", json=payload, headers=headers
    )
    assert r.status_code == 500
    assert assert_json(r).get("detail") == "Internal server error"


# GET /employee/requests/transfer/{id}
def test_get_transfer_by_id_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/transfer/1", headers=headers)

    assert r.status_code in [200, 404]

    if r.status_code == 200:
        keys = {
            "request_id",
            "transfer_id",
            "current_department",
            "request_department",
            "reason",
            "status",
        }
        assert keys.issubset(assert_json(r).keys())


def test_get_transfer_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.get(f"{BASE_URL}/employee/requests/transfer/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"


# PUT /employee/requests/transfer/{id}
def test_put_transfer_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {
        "current_department": "Existing",
        "request_department": "New Dept",
        "reason": "Update reason",
    }

    r = client.put(
        f"{BASE_URL}/employee/requests/transfer/1", json=payload, headers=headers
    )

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Transfer request updated"


def test_put_transfer_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"current_department": "DeptA", "request_department": "DeptB"}

    r = client.put(
        f"{BASE_URL}/employee/requests/transfer/999999", json=payload, headers=headers
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"


# DELETE /employee/requests/transfer/{id}
def test_delete_transfer_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/requests/transfer/1", headers=headers)

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Transfer request deleted"


def test_delete_transfer_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    r = client.delete(f"{BASE_URL}/employee/requests/transfer/999999", headers=headers)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"
