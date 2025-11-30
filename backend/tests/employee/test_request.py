from datetime import datetime

import httpx
import pytest


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# HR REQUEST MANAGEMENT TESTS

# GET /hr/request — All requests with optional filters
def test_hr_get_all_requests_success(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/request", headers=auth_hr, params={})
    assert r.status_code == 200

    data = assert_json(r)
    assert "requests" in data
    assert isinstance(data["requests"], list)


def test_hr_get_all_requests_with_filters(base_url, auth_hr):
    r = httpx.get(
        f"{base_url}/hr/request",
        headers=auth_hr,
        params={"request_type": "leave", "status": "pending"},
    )

    assert r.status_code == 200

    data = assert_json(r)
    assert "requests" in data
    assert isinstance(data["requests"], list)


def test_hr_get_all_requests_invalid_type(base_url, auth_hr):
    r = httpx.get(
        f"{base_url}/hr/request",
        headers=auth_hr,
        params={"request_type": "random_type"},
    )
    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Invalid request type"


def test_hr_get_all_requests_invalid_status(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/request", headers=auth_hr, params={"status": "wrong"})
    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Invalid status"


def test_hr_get_all_requests_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/request")
    assert r.status_code in (401, 403)


# GET /hr/request/{request_id}
def test_hr_get_request_by_id_success(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "Sick",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    assert create.status_code in [200, 201]
    request_id = assert_json(create)["request_id"]

    r = httpx.get(f"{base_url}/hr/request/{request_id}", headers=auth_hr)
    assert r.status_code == 200

    data = assert_json(r)
    keys = {
        "request_id",
        "user_id",
        "request_type",
        "status",
        "created_date",
        "details",
    }
    assert keys.issubset(data.keys())


def test_hr_get_request_by_id_not_found(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/request/999999", headers=auth_hr)
    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Request not found"


def test_hr_get_request_by_id_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/request/1")
    assert r.status_code in (401, 403)


# PUT /hr/request/{request_id} — Accept/Reject
def test_hr_update_request_accept_success(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "Casual",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    assert create.status_code in [200, 201]
    req_id = assert_json(create)["request_id"]

    r = httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "accept"}, headers=auth_hr
    )
    assert r.status_code == 200
    assert assert_json(r)["message"] == "Request accepted successfully"


def test_hr_update_request_reject_success(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "Emergency",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    req_id = assert_json(create)["request_id"]

    r = httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "reject"}, headers=auth_hr
    )

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Request rejected successfully"


def test_hr_update_request_missing_action(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "WFH",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    req_id = assert_json(create)["request_id"]

    r = httpx.put(
        f"{base_url}/hr/request/{req_id}", json={}, headers=auth_hr  # missing action
    )

    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Missing required field: 'action'"


def test_hr_update_request_invalid_action(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "WFH",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    req_id = assert_json(create)["request_id"]

    r = httpx.put(
        f"{base_url}/hr/request/{req_id}",
        json={"action": "invalid_action"},
        headers=auth_hr,
    )

    assert r.status_code == 400
    assert (
        assert_json(r).get("detail") == "Invalid action. Must be 'accept' or 'reject'"
    )


def test_hr_update_request_not_pending(base_url, auth_hr, auth_employee):
    payload = {
        "leave_type": "Medical",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )
    req_id = assert_json(create)["request_id"]

    httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "accept"}, headers=auth_hr
    )

    r = httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "reject"}, headers=auth_hr
    )

    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Only pending requests can be updated"


def test_hr_update_request_not_found(base_url, auth_hr):
    r = httpx.put(
        f"{base_url}/hr/request/999999", json={"action": "accept"}, headers=auth_hr
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Request not found"


def test_hr_update_request_unauthorized(base_url):
    r = httpx.put(
        f"{base_url}/hr/request/1",
        json={"action": "accept"},
    )
    assert r.status_code in (401, 403)


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
    list_resp = httpx.get(f"{base_url}/employee/requests/leave", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    leaves = data.get("leaves", [])

    if not leaves:
        pytest.skip("No leave requests available to test GET")

    leave_id = leaves[0]["leave_id"]
    r = httpx.get(
        f"{base_url}/employee/requests/leave/{leave_id}", headers=auth_employee
    )

    assert r.status_code == 200
    response_data = assert_json(r)
    keys = {
        "request_id",
        "leave_id",
        "leave_type",
        "from_date",
        "to_date",
        "reason",
        "status",
    }
    assert keys.issubset(response_data.keys())


def test_get_leave_by_id_not_found(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/requests/leave/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Leave request not found"


def test_put_leave_request_success(base_url, auth_employee):
    list_resp = httpx.get(f"{base_url}/employee/requests/leave", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    leaves = data.get("leaves", [])

    if not leaves:
        pytest.skip("No leave requests available to test PUT")

    leave_id = leaves[0]["leave_id"]
    payload = {
        "leave_type": "Casual",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
        "reason": "Updated",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/leave/{leave_id}",
        json=payload,
        headers=auth_employee,
    )

    assert r.status_code in [200, 400]
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


def test_put_leave_request_not_pending(base_url, auth_employee, auth_hr):
    payload = {
        "leave_type": "Medical",
        "from_date": datetime.now().isoformat(),
        "to_date": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/leave", json=payload, headers=auth_employee
    )

    assert create.status_code in [200, 201]
    req_id = assert_json(create)["request_id"]
    leave_id = assert_json(create)["leave_id"]

    httpx.put(
        f"{base_url}/hr/request/{req_id}",
        json={"action": "accept"},
        headers=auth_hr,
    )

    r = httpx.put(
        f"{base_url}/employee/requests/leave/{leave_id}",
        json={
            "leave_type": "Updated",
            "from_date": datetime.now().isoformat(),
            "to_date": datetime.now().isoformat(),
        },
        headers=auth_employee,
    )

    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Only pending requests can be modified"


def test_delete_leave_request_success(base_url, auth_employee):
    list_resp = httpx.get(f"{base_url}/employee/requests/leave", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    leaves = data.get("leaves", [])

    if not leaves:
        pytest.skip("No leave requests available to test DELETE")

    leave_id = leaves[0]["leave_id"]
    r = httpx.delete(
        f"{base_url}/employee/requests/leave/{leave_id}", headers=auth_employee
    )

    assert r.status_code in [200, 400]
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
    list_resp = httpx.get(
        f"{base_url}/employee/requests/reimbursement", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reimbursements = data.get("reimbursements", [])

    if not reimbursements:
        pytest.skip("No reimbursements available to test GET")

    reimbursement_id = reimbursements[0]["reimbursement_id"]
    r = httpx.get(
        f"{base_url}/employee/requests/reimbursement/{reimbursement_id}",
        headers=auth_employee,
    )

    assert r.status_code == 200
    response_data = assert_json(r)
    keys = {
        "request_id",
        "reimbursement_id",
        "expense_type",
        "amount",
        "date_expense",
        "remark",
        "status",
    }
    assert keys.issubset(response_data.keys())


def test_get_reimbursement_by_id_not_found(base_url, auth_employee):
    r = httpx.get(
        f"{base_url}/employee/requests/reimbursement/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Reimbursement not found"


def test_put_reimbursement_not_pending(base_url, auth_employee, auth_hr):
    payload = {
        "expense_type": "Travel",
        "amount": 500,
        "date_expense": datetime.now().isoformat(),
    }
    create = httpx.post(
        f"{base_url}/employee/requests/reimbursement",
        json=payload,
        headers=auth_employee,
    )

    assert create.status_code in [200, 201]
    req_id = assert_json(create)["request_id"]
    reimbursement_id = assert_json(create)["reimbursement_id"]

    httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "accept"}, headers=auth_hr
    )

    r = httpx.put(
        f"{base_url}/employee/requests/reimbursement/{reimbursement_id}",
        json={
            "expense_type": "Updated Meals",
            "amount": 100,
            "date_expense": datetime.now().isoformat(),
        },
        headers=auth_employee,
    )

    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Only pending requests can be modified"


def test_put_reimbursement_success(base_url, auth_employee):
    list_resp = httpx.get(
        f"{base_url}/employee/requests/reimbursement", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reimbursements = data.get("reimbursements", [])

    if not reimbursements:
        pytest.skip("No reimbursements available to test PUT")

    reimbursement_id = reimbursements[0]["reimbursement_id"]
    payload = {
        "expense_type": "Meals",
        "amount": 200,
        "date_expense": datetime.now().isoformat(),
        "remark": "Lunch update",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/reimbursement/{reimbursement_id}",
        json=payload,
        headers=auth_employee,
    )
    assert r.status_code in [200, 400]

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
    list_resp = httpx.get(
        f"{base_url}/employee/requests/reimbursement", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reimbursements = data.get("reimbursements", [])

    if not reimbursements:
        pytest.skip("No reimbursements available to test DELETE")

    reimbursement_id = reimbursements[0]["reimbursement_id"]
    r = httpx.delete(
        f"{base_url}/employee/requests/reimbursement/{reimbursement_id}",
        headers=auth_employee,
    )

    assert r.status_code in [200, 400]
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
    list_resp = httpx.get(
        f"{base_url}/employee/requests/transfer", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    transfers = data.get("transfers", [])

    if not transfers:
        pytest.skip("No transfer requests available to test GET")

    transfer_id = transfers[0]["transfer_id"]
    r = httpx.get(
        f"{base_url}/employee/requests/transfer/{transfer_id}", headers=auth_employee
    )

    assert r.status_code == 200
    response_data = assert_json(r)
    keys = {
        "request_id",
        "transfer_id",
        "current_department",
        "request_department",
        "reason",
        "status",
    }
    assert keys.issubset(response_data.keys())


def test_get_transfer_not_found(base_url, auth_employee):
    r = httpx.get(
        f"{base_url}/employee/requests/transfer/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"


def test_put_transfer_not_pending(base_url, auth_employee, auth_hr):
    payload = {
        "current_department": "Sales",
        "request_department": "HR",
    }
    create = httpx.post(
        f"{base_url}/employee/requests/transfer", json=payload, headers=auth_employee
    )
    assert create.status_code in [200, 201]
    req_id = assert_json(create)["request_id"]
    transfer_id = assert_json(create)["transfer_id"]

    httpx.put(
        f"{base_url}/hr/request/{req_id}", json={"action": "accept"}, headers=auth_hr
    )

    r = httpx.put(
        f"{base_url}/employee/requests/transfer/{transfer_id}",
        json={
            "current_department": "Sales",
            "request_department": "Marketing",
            "reason": "Updated reason",
        },
        headers=auth_employee,
    )

    assert r.status_code == 400
    assert assert_json(r).get("detail") == "Only pending requests can be modified"


def test_put_transfer_success(base_url, auth_employee):
    list_resp = httpx.get(
        f"{base_url}/employee/requests/transfer", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    transfers = data.get("transfers", [])

    if not transfers:
        pytest.skip("No transfer requests available to test PUT")

    transfer_id = transfers[0]["transfer_id"]
    payload = {
        "current_department": "Existing",
        "request_department": "New Dept",
        "reason": "Update reason",
    }

    r = httpx.put(
        f"{base_url}/employee/requests/transfer/{transfer_id}",
        json=payload,
        headers=auth_employee,
    )

    assert r.status_code in [200, 400]
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
    list_resp = httpx.get(
        f"{base_url}/employee/requests/transfer", headers=auth_employee
    )
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    transfers = data.get("transfers", [])

    if not transfers:
        pytest.skip("No transfer requests available to test DELETE")

    transfer_id = transfers[0]["transfer_id"]
    r = httpx.delete(
        f"{base_url}/employee/requests/transfer/{transfer_id}", headers=auth_employee
    )

    assert r.status_code in [200, 400]
    if r.status_code == 200:
        assert assert_json(r).get("message") == "Transfer request deleted"


def test_delete_transfer_not_found(base_url, auth_employee):
    r = httpx.delete(
        f"{base_url}/employee/requests/transfer/999999", headers=auth_employee
    )

    assert r.status_code == 404
    assert assert_json(r).get("detail") == "Transfer request not found"