import os

import pytest
import requests
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
def test_get_pm_projects(client, auth_pm):
    response = client.get(
        f"{BASE_URL}/api/pm/projects", headers=auth_pm
    )

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Projects retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "projects" in data.get("data")
    assert "total_projects" in data.get("data")

    if data.get("data").get("projects"):
        # Validate projects keys
        assert "id" in data.get("data").get("projects")[0]
        assert "client_id" in data.get("data").get("projects")[0]
        assert "project_id" in data.get("data").get("projects")[0]
        assert "project_name" in data.get("data").get("projects")[0]
        assert "description" in data.get("data").get("projects")[0]

