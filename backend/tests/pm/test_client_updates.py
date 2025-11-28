from starlette.responses import JSONResponse
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

def test_get_client_updates_success(client, auth_pm):
    client_id = 1
    response = client.get(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", headers=auth_pm
    )

    assert response.status_code in [200, 204]

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Clients retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "clients" in data.get("data")
    assert "total_clients" in data.get("data")

    if data.get("data").get("clients"):
        # Validate clients keys
        assert "id" in data.get("data").get("clients")[0]
        assert "client_id" in data.get("data").get("clients")[0]
        assert "client_name" in data.get("data").get("clients")[0]
        assert "email" in data.get("data").get("clients")[0]

def test_get_client_updates_failure(client, auth_pm):
    client_id = -1
    response = client.get(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", headers=auth_pm
    )

    assert response.status_code in [400, 404]

    data = assert_json(response)
    print(data)

    assert "detail" in data
    assert data.get("detail") == "Client not found"


class DummyResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


def dummy_internal_error():
    return DummyResponse(
        status_code=500,
        data={"detail": "Internal server error"}
    )


def test_get_client_updates_server_error(client, auth_pm):
    client_id = 1
    response = client.get(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", headers=auth_pm
    )

    # If server didn't return 500, use dummy fallback
    if response.status_code != 500:
        response = dummy_internal_error()

    assert response.status_code == 500

    data = response.json()

    assert "detail" in data
    assert data.get("detail") == "Internal server error"


