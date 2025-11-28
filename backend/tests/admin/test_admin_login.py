import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

ROOT_USER_EMAIL = os.getenv("ROOT_USER_EMAIL")
ROOT_USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# ----------------------------------------
#  /api/user/login (POST) - Admin login
# ----------------------------------------


def test_post_admin_login(client):
    payload = {"email": ROOT_USER_EMAIL, "password": ROOT_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    print(data)
    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "root"


def admin_token(client):
    payload = {"email": ROOT_USER_EMAIL, "password": ROOT_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)
    data = response.json()
    return data.get("access_token")
