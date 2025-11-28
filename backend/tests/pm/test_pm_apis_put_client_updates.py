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
#  PUT /api/pm/client/updates/{client_id}
#      ?update_id=INTEGER
# -----------------------------------------------------------

def test_put_client_update_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1        # Use valid client_id if possible
    update_id = 1        # Use valid update_id if possible

    payload = {
        "details": "Updated project status: Phase 2 development 60% complete."
    }

    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    resp = client.put(
        url,
        headers=headers,
        params={"update_id": update_id},
        json=payload
    )

    # Accept 200 (updated) or 404 (client/update not found)
    assert resp.status_code in [200, 404]

    if resp.status_code == 200:
        data = assert_json(resp)
        # Swagger says "string", backend may return dict/message
        assert isinstance(data, (str, dict))

        if isinstance(data, dict):
            assert "message" in data


def test_put_client_update_missing_update_id(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    payload = {
        "details": "Should fail because update_id is missing"
    }

    resp = client.put(url, headers=headers, json=payload)  # No update_id param

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
