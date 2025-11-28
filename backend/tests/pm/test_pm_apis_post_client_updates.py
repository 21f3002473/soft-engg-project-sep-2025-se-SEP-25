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
#  POST /api/pm/client/updates/{client_id}
#  → Create a new update for a client project
# -----------------------------------------------------------

def test_post_client_update_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1  # use a valid client_id if available

    payload = {
        "update_id": "U1001",
        "project_id": 1,
        "details": "Initial project kick-off completed and requirements finalized.",
    }

    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    resp = client.post(url, headers=headers, json=payload)

    # 200 = created, 404 = client/project not found, 409 = duplicate (if implemented)
    assert resp.status_code in [200, 404, 409]

    if resp.status_code == 200:
        data = assert_json(resp)
        # Swagger says "string", but backend may return dict/message
        assert isinstance(data, (str, dict))

        if isinstance(data, dict):
            assert "message" in data


# -----------------------------------------------------------
#  NEGATIVE TEST → 422 VALIDATION ERROR
# -----------------------------------------------------------

def test_post_client_update_validation_error(client):
    """
    Send invalid body (missing required fields) → expect 422.
    """
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    # Missing 'update_id' and 'project_id'
    payload = {
        "details": "This payload is incomplete"
    }

    resp = client.post(url, headers=headers, json=payload)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
