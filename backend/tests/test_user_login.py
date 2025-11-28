import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

ROOT_USER_EMAIL = os.getenv("ROOT_USER_EMAIL")
ROOT_USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD")

PM_USER_EMAIL = os.getenv("PM_USER_EMAIL")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD")

HR_USER_EMAIL = os.getenv("HR_USER_EMAIL")
HR_USER_PASSWORD = os.getenv("HR_USER_PASSWORD")

EMPLOYEE_USER_EMAIL = os.getenv("EMPLOYEE_USER_EMAIL")
EMPLOYEE_USER_PASSWORD = os.getenv("EMPLOYEE_USER_PASSWORD")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# --------------------------
#  /api/user/login (GET)
# --------------------------


def test_get_user_login(client):
    response = client.get(f"{BASE_URL}/user/login")

    assert response.status_code == 200

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message"}
    assert set(data.keys()) == expected_keys

    assert data.get("message") == "User login endpoint"


# ----------------------------------------
#  /api/user/login (POST) - Admin login
# ----------------------------------------


def test_post_admin_login(client):
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


# ----------------------------------------
#  /api/user/login (POST) - PM login
# ----------------------------------------


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


# ----------------------------------------
#  /api/user/login (POST) - HR login
# ----------------------------------------


def test_post_hr_login(client):
    payload = {"email": HR_USER_EMAIL, "password": HR_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "human_resource"


# ----------------------------------------
#  /api/user/login (POST) - Employee login
# ----------------------------------------


def test_post_employee_login(client):
    payload = {"email": EMPLOYEE_USER_EMAIL, "password": EMPLOYEE_USER_PASSWORD}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "employee"


# -----------------------------------
#  /api/user/login (POST) - Bad login
# -----------------------------------


def test_post_bad_login(client):
    payload = {"email": "root@gmail.com", "password": "root1@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [401, 403]

    data = assert_json(response)

    assert "detail" in data
    assert data.get("detail") == "Invalid email or password"
