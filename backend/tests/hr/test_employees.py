import httpx
import pytest


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# GET EMPLOYEE DETAIL (GET /api/hr/employee/{id})
def test_hr_employee_detail_success(base_url, auth_pm, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/employees", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    employees = data.get("employees", [])

    if not employees:
        pytest.skip("No Employees available to test GET detail")

    emp_id = employees[-1]["id"]

    r = httpx.get(f"{base_url}/hr/employee/{emp_id}", headers=auth_pm)
    assert r.status_code == 200

    response_data = assert_json(r)
    assert "employee" in response_data
    assert {"id", "name", "email"}.issubset(response_data["employee"].keys())


def test_hr_employee_detail_not_found(base_url, auth_pm):
    r = httpx.get(f"{base_url}/hr/employee/999999", headers=auth_pm)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_detail_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/employee/1")
    assert r.status_code in [401, 403]


# UPDATE EMPLOYEE (PUT /api/hr/employee/{id})
def test_hr_employee_update_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/employees", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    employees = data.get("employees", [])

    if not employees:
        pytest.skip("No Employees available to test UPDATE")

    emp_id = employees[0]["id"]

    payload = {
        "name": "Updated Name",
        "email": employees[0]["email"],
        "position": "Updated Position",
        "salary": 99999,
    }

    r = httpx.put(f"{base_url}/hr/employee/{emp_id}", json=payload, headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Employee updated"


def test_hr_employee_update_not_found(base_url, auth_hr):
    payload = {"name": "Anything", "email": "x@y.com", "position": "Dev", "salary": 10}

    r = httpx.put(f"{base_url}/hr/employee/999999", json=payload, headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_update_unauthorized(base_url):
    payload = {"name": "No Auth", "email": "no@auth.com", "position": "X", "salary": 1}

    r = httpx.put(f"{base_url}/hr/employee/1", json=payload)

    assert r.status_code in [401, 403]


# DELETE EMPLOYEE (DELETE /api/hr/employee/{id})
def test_hr_employee_delete_success(base_url, auth_admin, auth_hr):
    from admin.test_admin_apis import create_user
    create_user(
        client=httpx,
        auth_admin=auth_admin,
        name="John Doe",
        role="employee"
    )
    list_resp = httpx.get(f"{base_url}/hr/employees", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    employees = data.get("employees", [])

    if not employees:
        pytest.skip("No Employees available to test DELETE")
    else:
        emp_id = employees[-1]["id"]
        r = httpx.delete(f"{base_url}/hr/employee/{emp_id}", headers=auth_admin)
        assert r.status_code == 200
        assert assert_json(r)["message"] == "Employee deleted"


def test_hr_employee_delete_not_found(base_url, auth_admin):
    r = httpx.delete(f"{base_url}/hr/employee/999999", headers=auth_admin)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_delete_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/hr/employee/1")

    assert r.status_code in [401, 403]


# LIST ALL EMPLOYEES (GET /api/hr/employees)
def test_hr_employee_list_success(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/employees", headers=auth_hr)

    assert r.status_code == 200
    data = assert_json(r)
    assert "employees" in data
    assert isinstance(data["employees"], list)


def test_hr_employee_list_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/employees")
    assert r.status_code in [401, 403]