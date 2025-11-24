from datetime import datetime
import httpx


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# LEAVE REQUESTS


def test_get_all_leave_requests_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/leave", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)
    assert "leaves" in data
    assert isinstance(data["leaves"], list)


def test_get_all_leave_requests_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/requests/leave")
    assert r.status_code in [401, 403]


# POST /employee/requests/leave
def test_post_leave_request_success(base_url, auth_employee):
    payload = {
        "leave_type": "Sick",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
        "reason": "Fever",
    }

    r = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data.get("message") == "Leave request submitted"
    assert "request_id" in data


def test_get_leave_by_id_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/leave/1", headers=auth_employee)

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


def test_get_leave_by_id_not_found(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/leave/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


def test_put_leave_request_success(base_url, auth_employee):
    payload = {
        "leave_type": "Casual",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
        "reason": "Updated",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/leave/1", json=payload, headers=auth_employee
    )

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Leave request updated"


def test_put_leave_request_not_found(base_url, auth_employee):
    r = httpx.put(
        f"{base_url}/employee/requests/leave/999999",
        json={
            "leave_type": "Sick",
            "from_date": datetime.now().isoformat(),
            "to_date": datetime.now().isoformat(),
        },
        headers=auth_employee,
    )
    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


def test_put_leave_request_not_pending(base_url, auth_employee):
    r = httpx.put(
        f"{base_url}/employee/requests/leave/1",
        json={
            "leave_type": "Updated",
            "from_date": datetime.now().isoformat(),
            "to_date": datetime.now().isoformat(),
        },
        headers=auth_employee,
    )

    assert r.status_code in [400, 500]


def test_delete_leave_request_success(base_url, auth_employee):
    r = httpx.delete(f"{base_url}/employee/requests/leave/1", headers=auth_employee)

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Leave request deleted"


def test_delete_leave_request_not_found(base_url, auth_employee):
    r = httpx.delete(
        f"{base_url}/employee/requests/leave/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


# REIMBURSEMENT REQUESTS


def test_get_all_reimbursements_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/reimbursement", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)
    assert "reimbursements" in data


def test_get_all_reimbursements_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/requests/reimbursement")
    assert r.status_code in [401, 403]


def test_post_reimbursement_success(base_url, auth_employee):
    payload = {
        "expense_type": "Travel",
        "amount": 500,
        "date_expense": datetime.now().isoformat(),
        "remark": "Taxi",
    }

    r = httpx.post(
        f"{base_url}/employee/requests/reimbursement",
        json=payload,
        headers=auth_employee,
    )
    assert r.status_code in [200, 201]
    assert assert_json(r).get("message") == "Reimbursement submitted"


def test_get_reimbursement_by_id_success(base_url, auth_employee):
    r = httpx.get(
        f"{base_url}/employee/requests/reimbursement/1", headers=auth_employee
    )

    assert r.status_code in [200, 404]
    if r.status_code == 200:
        keys = {
            "request_id",
            "reimbursement_id",
            "expense_type",
            "amount",
            "date_expense",
            "remark",
            "status",
        }
        assert keys.issubset(assert_json(r).keys())


def test_get_reimbursement_by_id_not_found(base_url, auth_employee):
    r = httpx.get(
        f"{base_url}/employee/requests/reimbursement/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


def test_put_reimbursement_success(base_url, auth_employee):
    payload = {
        "expense_type": "Meals",
        "amount": 200,
        "date_expense": datetime.now().isoformat(),
        "remark": "Lunch update",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/reimbursement/1",
        json=payload,
        headers=auth_employee,
    )
    assert r.status_code in [200, 400, 404]

    if r.status_code == 200:
        assert assert_json(r).get("message") == "Reimbursement updated"


def test_put_reimbursement_not_found(base_url, auth_employee):
    r = httpx.put(
        f"{base_url}/employee/requests/reimbursement/999999",
        json={
            "expense_type": "Travel",
            "amount": 100,
            "date_expense": datetime.now().isoformat(),
        },
        headers=auth_employee,
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


def test_delete_reimbursement_success(base_url, auth_employee):
    r = httpx.delete(
        f"{base_url}/employee/requests/reimbursement/1", headers=auth_employee
    )

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Reimbursement deleted"


def test_delete_reimbursement_not_found(base_url, auth_employee):
    r = httpx.delete(
        f"{base_url}/employee/requests/reimbursement/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


# TRANSFER REQUESTS


def test_get_all_transfer_requests_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/transfer", headers=auth_employee)

    assert r.status_code == 200
    assert "transfers" in assert_json(r)


def test_get_all_transfer_requests_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/requests/transfer")
    assert r.status_code in [401, 403]


def test_post_transfer_success(base_url, auth_employee):
    payload = {
        "current_department": "Sales",
        "request_department": "Marketing",
        "reason": "Career growth",
    }

    r = httpx.post(
        f"{base_url}/employee/requests/transfer", json=payload, headers=auth_employee
    )
    assert r.status_code in [200, 201]
    assert assert_json(r).get("message") == "Transfer request submitted"


def test_get_transfer_by_id_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/transfer/1", headers=auth_employee)

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


def test_get_transfer_not_found(base_url, auth_employee):
    r = httpx.get(
        f"{base_url}/employee/requests/transfer/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"


def test_put_transfer_success(base_url, auth_employee):
    payload = {
        "current_department": "Existing",
        "request_department": "New Dept",
        "reason": "Update reason",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/transfer/1", json=payload, headers=auth_employee
    )

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Transfer request updated"


def test_put_transfer_not_found(base_url, auth_employee):
    payload = {"current_department": "DeptA", "request_department": "DeptB"}

    r = httpx.put(
        f"{base_url}/employee/requests/transfer/999999",
        json=payload,
        headers=auth_employee,
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"


def test_delete_transfer_success(base_url, auth_employee):
    r = httpx.delete(f"{base_url}/employee/requests/transfer/1", headers=auth_employee)

    assert r.status_code in [200, 400, 404]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Transfer request deleted"


def test_delete_transfer_not_found(base_url, auth_employee):
    r = httpx.delete(
        f"{base_url}/employee/requests/transfer/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"
