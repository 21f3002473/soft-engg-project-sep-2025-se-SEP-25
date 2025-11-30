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

EMP_USER_EMAIL = os.getenv("EMPLOYEE_USER_EMAIL")
EMP_USER_PASSWORD = os.getenv("EMPLOYEE_USER_PASSWORD")




# --------------------------
#  /api/pm/employees (GET)
# --------------------------
def test_get_pm_employees(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/employees", headers=auth_pm)

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Employees retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "employees" in data.get("data")
    assert "total_employees" in data.get("data")

    if data.get("data").get("employees"):
        # Validate employees keys
        assert "id" in data.get("data").get("employees")[0]
        assert "name" in data.get("data").get("employees")[0]
        assert "email" in data.get("data").get("employees")[0]
        assert "role" in data.get("data").get("employees")[0]


def test_get_pm_employees_failure(client):
    response = client.get(f"{BASE_URL}/api/pm/employees", headers={})
    assert response.status_code == 401

def get_employees(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/employees/", headers=auth_pm)

    assert response.status_code in [200]
    print(response.json())
    return response.json().get("data").get("employees")

