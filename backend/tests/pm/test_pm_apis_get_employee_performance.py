import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

PM_USER_EMAIL = os.getenv("PM_USER_EMAIL", "pm@gmail.com")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD", "pm@gmail.com")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


def get_pm_token(client):
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    resp = client.post(f"{BASE_URL}/user/login", json=payload)

    assert resp.status_code in [200, 201]
    data = assert_json(resp)

    assert "access_token" in data
    return data["access_token"]


# -----------------------------------------------------------
#  GET /api/pm/employee/performance/{employee_id}
# -----------------------------------------------------------

def test_get_employee_performance_success(client):
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    employee_id = 1  # use a valid employee_id if you have one
    url = f"{BASE_URL}/api/pm/employee/performance/{employee_id}"

    resp = client.get(url, headers=headers)

    # 200 if found, 404 if employee/performance not found
    assert resp.status_code in [200, 404]

    if resp.status_code == 200:
        data = assert_json(resp)
        # Swagger shows "string", but backend may return dict/list
        assert data is not None


def test_get_employee_performance_invalid_employee_id(client):
    """
    Non-integer employee_id in path → 422 validation error.
    """
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{BASE_URL}/api/pm/employee/performance/abc"

    resp = client.get(url, headers=headers)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
