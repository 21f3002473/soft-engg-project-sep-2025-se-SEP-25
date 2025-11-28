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
    """Login once and return a valid Bearer token for PM."""
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code == 200
    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "product_manager"