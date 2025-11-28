import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@pytest.fixture
def client():
    """Simple HTTP client wrapper using requests."""
    return requests


def assert_json(response):
    """Validate that the response contains JSON and return the parsed data."""
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()

# --------------------------
#  /api/pm/clients (GET)
# --------------------------
def test_get_pm_dashboard_success(client, auth_pm):
    response = client.get(
        f"{BASE_URL}/api/pm/dashboard", headers=auth_pm
    )

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Dashboard data retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "user" in data.get("data")
    assert "ClientList" in data.get("data")
    assert "projects" in data.get("data")
    assert "stats" in data.get("data")


    if data.get("data").get("user"):
        # Validate user keys
        assert "id" in data.get("data").get("user")
        assert "name" in data.get("data").get("user")
        assert "email" in data.get("data").get("user")
        assert "role" in data.get("data").get("user")

    if data.get("data").get("stats"):
        # Validate stats keys
        assert "total_projects" in data.get("data").get("stats")
        assert "active_projects" in data.get("data").get("stats")
        assert "completed_projects" in data.get("data").get("stats")
        assert "pending_projects" in data.get("data").get("stats")
