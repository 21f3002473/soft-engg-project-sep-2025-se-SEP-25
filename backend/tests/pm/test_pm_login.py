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



def test_get_pm_dashboard_success(client):
    """
    Steps:
    1. Login as PM to get a valid access token.
    2. Call /api/pm/dashboard with Authorization header.
    """

    login_payload = {
        "email": PM_USER_EMAIL,
        "password": PM_USER_PASSWORD
    }

    login_resp = client.post(f"{BASE_URL}/user/login", json=login_payload)

    assert login_resp.status_code in [200, 201]

    login_data = assert_json(login_resp)

    assert "access_token" in login_data

    token = login_data["access_token"]


    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get(f"{BASE_URL}/api/pm/dashboard", headers=headers)

    assert resp.status_code == 200

    data = assert_json(resp)


    assert isinstance(data, dict) or isinstance(data, list)
    assert data is not None
