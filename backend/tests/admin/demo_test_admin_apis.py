import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


BASE_URL = os.getenv("BASE_URL")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


from test_admin_login import test_post_admin_login


def admin_login_auth(token):
    return {"Authorization": f"Bearer {token}"}


# --------------------------
#  /api/admin/register (POST)
# --------------------------
def test_post_admin_register(client):
    import random

    admin_email = f"admin{random.randint(1, 1000)}@gmail.com"
    payload = {
        "name": "Admin",
        "email": admin_email,
        "password": "admin@gmail.com",
    }
    response = client.post(
        f"{BASE_URL}/api/admin/register",
        json=payload,
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code in [200, 201]

    data = assert_json(response)
    print(data)
    # assert "message" in data


# --------------------------
#  /api/admin/summary (GET)
# --------------------------
def test_get_admin_summary(client):
    response = client.get(
        f"{BASE_URL}/api/admin/summary",
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code == 200

    data = assert_json(response)
    print(data)
    assert isinstance(data, dict)

    # Validate expected keys
    expected_keys = ["userCount", "logsCount", "backupsCount", "currentAdmin"]
    assert set(expected_keys) == set(data.keys())

    # Validate currentAdmin
    assert isinstance(data.get("currentAdmin"), dict)
    assert ["id", "name", "email"] == list(data.get("currentAdmin").keys())


# ---------------------------
#  /api/admin/employees (GET)
# ---------------------------


def test_get_admin_employees(client):
    response = client.get(
        f"{BASE_URL}/api/admin/employees",
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, list)

    # Ensure at least 4 employees returned
    assert len(data) >= 4

    # Expected set of keys
    expected_keys = {"id", "name", "email", "role"}

    # Ensure every item has exactly these keys
    for item in data:
        assert set(item.keys()) == expected_keys

    # Validate roles for all employees
    valid_roles = {"root", "product_manager", "human_resource", "employee"}
    for item in data:
        assert item["role"] in valid_roles


# ----------------------------
#  /api/admin/employees (POST)
# ----------------------------


def test_post_admin_employees(client):
    import random

    email = f"john{random.randint(1, 1000)}@gmail.com"
    payload = {"name": "John Doe", "role": "HR", "email": email}
    response = client.post(
        f"{BASE_URL}/api/admin/employees",
        json=payload,
        headers=admin_login_auth(test_post_admin_login(client)),
    )

    assert response.status_code in [200, 201]

    data = assert_json(response)
    print(data)
    # Validate expected keys
    expected_keys = {"id", "name", "email", "role", "temporary_password"}
    assert set(expected_keys) == set(data.keys())


# -------------------------------
#  /api/admin/backup-config (GET)
# -------------------------------
def test_get_admin_backup_config(client):
    response = client.get(
        f"{BASE_URL}/api/admin/backup-config",
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code == 200

    data = assert_json(response)
    print(data)
    assert isinstance(data, dict)

    # Validate expected keys
    expected_keys = {"day", "type", "datetime"}
    assert set(expected_keys) == set(data.keys())


# -------------------------------
#  /api/admin/backup-config (PUT)
# -------------------------------


def test_put_admin_backup_config(client):
    payload = {"backups": [{"day": 1, "type": "full", "datetime": "2025-10-30T03:00"}]}

    response = client.put(
        f"{BASE_URL}/api/admin/backup-config",
        json=payload,
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code in [200, 204]

    if response.status_code != 204:
        data = assert_json(response)
    assert "message" in data
    assert data.get("message") == "Backup configuration updated"


# --------------------------
#  /api/admin/updates (GET)
# --------------------------
def test_get_admin_updates(client):
    response = client.get(
        f"{BASE_URL}/api/admin/updates",
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, dict)

    # Validate expected keys
    expected_keys = {"currentVersion", "updateAvailable", "lastChecked"}
    assert set(expected_keys) == set(data.keys())


# --------------------------
#  /api/admin/account (GET)
# --------------------------
def test_get_admin_account(client):
    response = client.get(
        f"{BASE_URL}/api/admin/account",
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, dict)

    # Validate expected keys
    expected_keys = {"id", "name", "email", "role"}
    assert set(expected_keys) == set(data.keys())


# --------------------------
#  /api/admin/account (PUT)
# --------------------------
def test_put_admin_account(client):
    payload = {
        "name": "Admin",
        "old_password": "admin@gmail.com",
        "new_password": "ad@gmail.com",
    }

    response = client.put(
        f"{BASE_URL}/api/admin/account",
        json=payload,
        headers=admin_login_auth(test_post_admin_login(client)),
    )
    assert response.status_code in [200, 204]

    if response.status_code != 204:
        data = assert_json(response)
        assert "message" in data
