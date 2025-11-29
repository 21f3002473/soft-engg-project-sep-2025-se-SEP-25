def test_list_employees(client):
    response = client.get("/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_get_employee(client, sample_employee_payload):
    # CREATE
    create = client.post("/employees", json=sample_employee_payload)
    assert create.status_code in [200, 201]

    emp_id = create.json().get("id")
    assert emp_id is not None

    # GET
    get_res = client.get(f"/employees/{emp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == sample_employee_payload["email"]


def test_get_employee_invalid(client):
    res = client.get("/employees/999999")
    assert res.status_code == 404


def test_update_employee(client, sample_employee_payload):
    # create first
    create = client.post("/employees", json=sample_employee_payload)
    emp_id = create.json()["id"]

    payload = {"name": "Updated", "email": "upd@test.com"}

    res = client.put(f"/employees/{emp_id}", json=payload)
    assert res.status_code == 200
    assert res.json()["name"] == "Updated"


def test_delete_employee(client, sample_employee_payload):
    create = client.post("/employees", json=sample_employee_payload)
    emp_id = create.json()["id"]

    delete = client.delete(f"/employees/{emp_id}")
    assert delete.status_code == 200
    assert delete.json().get("message") == "Employee deleted"
import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@pytest.fixture
def client():
    """Simple HTTP client wrapper using requests."""
    return requests


def assert_json(response):
    """Validate that the response contains JSON and return the parsed data."""
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()
