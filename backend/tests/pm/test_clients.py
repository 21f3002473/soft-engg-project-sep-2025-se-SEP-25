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
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# --------------------------
#  /api/user/login (GET)
# --------------------------

from test_pm_login import pm_token


def test_get_pm_client(client, pm_token):
    headers = {"Authorization": f"Bearer {pm_token}"}
    response = client.get(f"{BASE_URL}/pm/clients", headers=headers)

    assert response.status_code == 200

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message"}
    assert set(data.keys()) == expected_keys

    assert data.get("message") == "User login endpoint"

    # ----------------------------------------
    #  /api/user/login (POST) - Admin login
    # ----------------------------------------

    # def test_post_admin_login(client):
    payload = {"email": ROOT_USER_EMAIL, "password": ROOT_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "root"
