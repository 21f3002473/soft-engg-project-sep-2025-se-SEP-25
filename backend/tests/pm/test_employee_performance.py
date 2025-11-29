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


# -------------------------------------------------
#  /api/pm/employee/performance/{employee_id} (GET)
# --------------------------------------------------
def test_get_employee_performance_success(client, auth_pm):
    employee_id = 1
    response = client.get(
        f"{BASE_URL}/api/pm/employee/performance/{employee_id}", headers=auth_pm
    )

    assert response.status_code in [200, 204]

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Employee performance retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "employee" in data.get("data")
    assert "current_stats" in data.get("data")
    assert "performance_trends" in data.get("data")

    if data.get("data").get("employee"):
        # Validate employee keys
        assert "id" in data.get("data").get("employee")
        assert "name" in data.get("data").get("employee")
        assert "email" in data.get("data").get("employee")
        assert "role" in data.get("data").get("employee")

    if data.get("data").get("current_stats"):
        # Validate current_stats keys
        assert "completed" in data.get("data").get("current_stats")
        assert "in_progress" in data.get("data").get("current_stats")
        assert "pending" in data.get("data").get("current_stats")
        assert "total" in data.get("data").get("current_stats")
        assert "completed_percentage" in data.get("data").get("current_stats")
        assert "in_progress_percentage" in data.get("data").get("current_stats")
        assert "pending_percentage" in data.get("data").get("current_stats")

    if data.get("data").get("performance_trends"):
        # Validate performance_trends keys
        assert "month" in data.get("data").get("performance_trends")[0]
        assert "score" in data.get("data").get("performance_trends")[0]


def test_get_pm_employees_performance_failure(client, auth_pm):
    employee_id = 1
    response = client.get(
        f"{BASE_URL}/api/pm/employee/performance/{employee_id}", headers={}
    )
    assert response.status_code == 401
