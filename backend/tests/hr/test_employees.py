import os
from dotenv import load_dotenv
import httpx
import pytest


load_dotenv()

BASE_URL = os.getenv("BASE_URL")

def assert_json(resp):
    """Validate that the response contains JSON and return the parsed data."""
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# CREATE EMPLOYEE (POST /api/hr/employee/create)

def test_hr_employee_create_success(base_url, auth_hr):
    payload = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "position": "Developer",
        "salary": 50000
    }

    r = httpx.post(f"{base_url}/api/hr/employee/create", json=payload, headers=auth_hr)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "Employee created"
    assert "employee" in data
    assert "id" in data["employee"]


def test_hr_employee_create_missing_field(base_url, auth_hr):
    payload = {"name": "Missing email"}

    r = httpx.post(f"{base_url}/api/hr/employee/create", json=payload, headers=auth_hr)

    assert r.status_code == 422


def test_hr_employee_create_unauthorized(base_url):
    payload = {
        "name": "Unauthorized",
        "email": "x@example.com",
        "position": "Dev",
        "salary": 1000
    }

    r = httpx.post(f"{base_url}/api/hr/employee/create", json=payload)

    assert r.status_code in [401, 403]


# GET EMPLOYEE DETAIL (GET /api/hr/employee/{id})

def test_hr_employee_detail_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/api/hr/employees", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    employees = data.get("employees", [])

    if not employees:
        pytest.skip("No Employees available to test GET detail")

    emp_id = employees[0]["id"]

    r = httpx.get(f"{base_url}/api/hr/employee/{emp_id}", headers=auth_hr)
    assert r.status_code == 200

    response_data = assert_json(r)
    assert "employee" in response_data
    assert {"id", "name", "email"}.issubset(response_data["employee"].keys())


def test_hr_employee_detail_not_found(base_url, auth_hr):
    r = httpx.get(f"{base_url}/api/hr/employee/999999", headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_detail_unauthorized(base_url):
    r = httpx.get(f"{base_url}/api/hr/employee/1")
    assert r.status_code in [401, 403]


# UPDATE EMPLOYEE (PUT /api/hr/employee/{id})

def test_hr_employee_update_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/api/hr/employees", headers=auth_hr)
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
        "salary": 99999
    }

    r = httpx.put(f"{base_url}/api/hr/employee/{emp_id}", json=payload, headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Employee updated"


def test_hr_employee_update_not_found(base_url, auth_hr):
    payload = {"name": "Anything", "email": "x@y.com", "position": "Dev", "salary": 10}

    r = httpx.put(f"{base_url}/api/hr/employee/999999", json=payload, headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_update_unauthorized(base_url):
    payload = {"name": "No Auth", "email": "no@auth.com", "position": "X", "salary": 1}

    r = httpx.put(f"{base_url}/api/hr/employee/1", json=payload)

    assert r.status_code in [401, 403]


# DELETE EMPLOYEE (DELETE /api/hr/employee/{id})

def test_hr_employee_delete_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/api/hr/employees", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    employees = data.get("employees", [])

    if not employees:
        pytest.skip("No Employees available to test DELETE")

    emp_id = employees[0]["id"]

    r = httpx.delete(f"{base_url}/api/hr/employee/{emp_id}", headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Employee deleted"


def test_hr_employee_delete_not_found(base_url, auth_hr):
    r = httpx.delete(f"{base_url}/api/hr/employee/999999", headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Employee not found"


def test_hr_employee_delete_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/api/hr/employee/1")

    assert r.status_code in [401, 403]


# LIST ALL EMPLOYEES (GET /api/hr/employees)

def test_hr_employee_list_success(base_url, auth_hr):
    r = httpx.get(f"{base_url}/api/hr/employees", headers=auth_hr)

    assert r.status_code == 200
    data = assert_json(r)
    assert "employees" in data
    assert isinstance(data["employees"], list)


def test_hr_employee_list_unauthorized(base_url):
    r = httpx.get(f"{base_url}/api/hr/employees")
    assert r.status_code in [401, 403]

