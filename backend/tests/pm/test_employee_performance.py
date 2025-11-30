import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


from test_employee import get_employees


#  /api/pm/employee/performance/{employee_id} (GET)
def test_get_employee_performance_success(client, auth_pm):
    if get_employees(client, auth_pm) == []:
        employee_id = -1
    else:
        employee_id = get_employees(client, auth_pm)[-1].get("id")

    response = client.get(
        f"{BASE_URL}/api/pm/employee/performance/{employee_id}", headers=auth_pm
    )

    assert response.status_code in [200, 204, 404]

    if response.status_code == 200:
        data = assert_json(response)
        print(data)

        assert isinstance(data, dict)

        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        assert data.get("message") == "Employee performance retrieved successfully"
        assert isinstance(data.get("data"), dict)

        assert "employee" in data.get("data")
        assert "current_stats" in data.get("data")
        assert "performance_trends" in data.get("data")

        if data.get("data").get("employee"):
            assert "id" in data.get("data").get("employee")
            assert "name" in data.get("data").get("employee")
            assert "email" in data.get("data").get("employee")
            assert "role" in data.get("data").get("employee")

        if data.get("data").get("current_stats"):
            assert "completed" in data.get("data").get("current_stats")
            assert "in_progress" in data.get("data").get("current_stats")
            assert "pending" in data.get("data").get("current_stats")
            assert "total" in data.get("data").get("current_stats")
            assert "completed_percentage" in data.get("data").get("current_stats")
            assert "in_progress_percentage" in data.get("data").get("current_stats")
            assert "pending_percentage" in data.get("data").get("current_stats")

        if data.get("data").get("performance_trends"):
            assert "month" in data.get("data").get("performance_trends")[0]
            assert "score" in data.get("data").get("performance_trends")[0]


def test_get_pm_employees_performance_failure(client):
    employee_id = -1
    response = client.get(
        f"{BASE_URL}/api/pm/employee/performance/{employee_id}", headers={}
    )
    assert response.status_code == 401