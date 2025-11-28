import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
PM_USER_EMAIL = os.getenv("PM_USER_EMAIL")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD")


@pytest.fixture
def client():
    """Simple HTTP client wrapper using requests."""
    return requests


def assert_json(response):
    """Validate that the response contains JSON and return the parsed data."""
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# --------------------------
#  LOGIN FIXTURE (returns token)
# --------------------------
@pytest.fixture
def pm_token(client):
    """Login once and return a valid Bearer token for PM."""
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code == 200
    data = assert_json(response)
    return data.get("access_token")




# --------------------------
#  /api/pm/clients (GET)
# --------------------------
def test_get_pm_client(client, pm_token):
    response = client.get(
        f"{BASE_URL}/api/pm/clients",
        headers={"Authorization": f"Bearer {pm_token}"}
    )

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)
