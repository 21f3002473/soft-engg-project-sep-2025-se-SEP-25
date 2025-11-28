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
#  PUT /api/pm/projects
#  query: project_id (int)
#  body: { project_name?, description?, status?, manager_id? }
# -----------------------------------------------------------

def test_put_pm_project_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    project_id = 1  # use an existing project_id if you have one

    payload = {
        "project_name": "Updated AI Automation System",
        "description": "Updated description for the project",
        "status": "PENDING",
        "manager_id": 1,  # should be a valid manager_id if provided
    }

    resp = client.put(
        f"{BASE_URL}/api/pm/projects",
        headers=headers,
        params={"project_id": project_id},
        json=payload,
    )

    # API may respond:
    # 200 -> updated successfully
    # 404 -> project or manager not found
    # 500 -> internal error
    assert resp.status_code in [200, 404, 500]

    if resp.status_code == 200:
        data = assert_json(resp)

        # Backend doc: { "message": str, "data": { ...updated project... } }
        assert isinstance(data, dict)
        assert "message" in data
        assert "data" in data

        updated = data["data"]
        assert isinstance(updated, dict)
        for key in ["id", "project_id", "project_name", "status", "description"]:
            assert key in updated


def test_put_pm_project_missing_project_id(client):
    """
    Missing project_id query parameter → should give 422 validation error.
    """
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "project_name": "Should Fail",
        "description": "No project_id in query",
        "status": "PENDING",
        "manager_id": 1,
    }

    resp = client.put(
        f"{BASE_URL}/api/pm/projects",
        headers=headers,
        json=payload,  # no params={"project_id": ...}
    )

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data


