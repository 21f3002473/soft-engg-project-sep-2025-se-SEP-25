
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
    """Login as PM and return JWT access token."""
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    resp = client.post(f"{BASE_URL}/user/login", json=payload)

    assert resp.status_code in [200, 201]

    data = assert_json(resp)
    assert "access_token" in data
    return data["access_token"]



def test_get_pm_dashboard_success(client):
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"{BASE_URL}/api/pm/dashboard", headers=headers)

    assert resp.status_code == 200

    data = assert_json(resp)

  
    assert data is not None
    assert isinstance(data, (dict, list))
