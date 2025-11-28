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


def test_get_client_requirements_success(client, auth_pm):
    client_id = 1
    response = client.get(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}", headers=auth_pm
    )

    assert response.status_code in [200, 204]

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Requirements retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "client" in data.get("data")
    assert "requirements" in data.get("data")
    assert "total_requirements" in data.get("data")

    if data.get("data").get("requirements"):
        # Validate requirements keys
        assert "id" in data.get("data").get("requirements")[0]
        assert "requirement_id" in data.get("data").get("requirements")[0]
        assert "description" in data.get("data").get("requirements")[0]
        assert "project_id" in data.get("data").get("requirements")[0]
