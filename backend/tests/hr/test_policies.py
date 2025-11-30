import httpx
import pytest


def assert_json(resp):
    """Validate that the response contains JSON and return the parsed data."""
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# CREATE POLICY (POST /api/hr/policy/create)


def test_policy_create_success(base_url, auth_hr):
    payload = {
        "title": "Leave Policy",
        "content": "Employees can take 20 leaves annually.",
    }

    r = httpx.post(f"{base_url}/hr/policy/create", json=payload, headers=auth_hr)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "Policy created"
    assert "id" in data["policy"]


def test_policy_create_missing_field(base_url, auth_hr):
    payload = {"title": "Only title"}

    r = httpx.post(f"{base_url}/hr/policy/create", json=payload, headers=auth_hr)

    assert r.status_code == 500


def test_policy_create_unauthorized(base_url):
    payload = {"title": "Test", "content": "Test content"}

    r = httpx.post(f"{base_url}/hr/policy/create", json=payload)

    assert r.status_code in [401, 403]


# GET POLICY DETAIL (GET /api/hr/policy/{id})


def test_policy_detail_success(base_url, auth_employee):
    list_resp = httpx.get(f"{base_url}/hr/policies", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    policies = data.get("policies", [])

    if not policies:
        pytest.skip("No policies available to test GET detail")

    pol_id = policies[0]["id"]

    r = httpx.get(f"{base_url}/hr/policy/{pol_id}", headers=auth_employee)
    assert r.status_code == 200

    response_data = assert_json(r)
    assert "policy" in response_data
    assert {"id", "title", "content"}.issubset(response_data["policy"].keys())


def test_policy_detail_not_found(base_url, auth_employee):
    r = httpx.get(f"{base_url}/hr/policy/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Policy not found"


def test_policy_detail_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/policy/1")
    assert r.status_code in [401, 403]


# UPDATE POLICY (PUT /api/hr/policy/{id})


def test_policy_update_success(base_url, auth_hr, auth_employee):
    list_resp = httpx.get(f"{base_url}/hr/policies", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    policies = data.get("policies", [])

    if not policies:
        pytest.skip("No policies available to test UPDATE")

    pol_id = policies[0]["id"]

    payload = {"title": "Updated Policy", "content": "Updated content text."}

    r = httpx.put(f"{base_url}/hr/policy/{pol_id}", json=payload, headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Policy updated"


def test_policy_update_not_found(base_url, auth_hr):
    payload = {"title": "X", "content": "Y"}

    r = httpx.put(f"{base_url}/hr/policy/999999", json=payload, headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Policy not found"


def test_policy_update_unauthorized(base_url):
    payload = {"title": "Test", "content": "Test"}

    r = httpx.put(f"{base_url}/hr/policy/1", json=payload)
    assert r.status_code in [401, 403]


# DELETE POLICY (DELETE /api/hr/policy/{id})


def test_policy_delete_success(base_url, auth_hr, auth_employee):
    list_resp = httpx.get(f"{base_url}/hr/policies", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    policies = data.get("policies", [])

    if not policies:
        pytest.skip("No policies available for DELETE test")

    pol_id = policies[0]["id"]

    r = httpx.delete(f"{base_url}/hr/policy/{pol_id}", headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Policy deleted"


def test_policy_delete_not_found(base_url, auth_hr):
    r = httpx.delete(f"{base_url}/hr/policy/999999", headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Policy not found"


def test_policy_delete_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/hr/policy/1")
    assert r.status_code in [401, 403]


# LIST ALL POLICIES (GET /api/employee/policies)


def test_policy_list_employee_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/hr/policies", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)
    assert "policies" in data
    assert isinstance(data["policies"], list)


def test_policy_list_employee_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/policies")
    assert r.status_code in [401, 403]
