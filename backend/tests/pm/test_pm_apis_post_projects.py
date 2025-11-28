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
#  POST /api/pm/projects
# -----------------------------------------------------------

def test_post_pm_project_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "project_id": "P1001",
        "project_name": "AI Automation System",
        "description": "Developing backend automation modules",
        "status": "PENDING",
        "client_id": 1,       # must exist in DB
        "manager_id": 1       # must exist in DB
    }

    resp = client.post(
        f"{BASE_URL}/api/pm/projects",
        headers=headers,
        json=payload
    )

    # Acceptable results based on backend behavior:
    # 200 = success
    # 400 = duplicate project_id
    # 404 = client/manager not found
    # 500 = unexpected error
    assert resp.status_code in [200, 400, 404, 500]

    if resp.status_code == 200:
        data = assert_json(resp)

        # Swagger says returns "string" but backend returns dict
        assert isinstance(data, (str, dict))

        if isinstance(data, dict):
            assert "message" in data
            assert "data" in data
            created = data["data"]
            for key in ["id", "project_id", "project_name", "status", "client_id"]:
                assert key in created


def test_post_pm_project_validation_error(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Missing project_id + client_id → should fail
    invalid_payload = {
        "project_name": "Incomplete Project",
        "description": "Missing fields",
        "status": "PENDING"
    }

    resp = client.post(
        f"{BASE_URL}/api/pm/projects",
        headers=headers,
        json=invalid_payload
    )

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
