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
#  /api/user/login (POST)
# --------------------------


def test_post_pm_login(client):
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "product_manager"

@pytest.fixture
def pm_token(client):
    """Automatically logs in PM & returns token."""
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in (200, 201)

    data = assert_json(response)

    # data is already a dict, so just index it
    return data["access_token"]


