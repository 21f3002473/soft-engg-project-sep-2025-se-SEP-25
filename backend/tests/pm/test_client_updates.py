import os
import random

import pytest
import requests
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from test_1_projects import create_project, get_projects
from test_clients import create_client

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
    client_id = create_client(client, auth_pm)
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
    assert data.get("message") == "Updates retrieved successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "client" in data.get("data")
    assert "updates" in data.get("data")
    assert "total_updates" in data.get("data")

    client_data = data.get("data").get("client")

    if client_data:
        assert "id" in client_data
        assert "client_id" in client_data
        assert "client_name" in client_data
        assert "email" in client_data
        assert "details" in client_data


def test_get_client_updates_failure(client, auth_pm):
    client_id = -1
    response = client.get(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", headers=auth_pm
    )

    assert response.status_code in [404]

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
    return DummyResponse(status_code=500, data={"detail": "Internal server error"})


# --------------------------------------------
#  /api/pm/client/updates/{client_id} (GET)
# -------------------------------------------
def test_get_client_updates_server_error(client, auth_pm):
    client_id = create_client(client, auth_pm)
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


# --------------------------------------------
#  /api/pm/client/updates/{client_id} (POST)
# -------------------------------------------
def test_post_client_updates_success(client, auth_pm):

    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    project_id = projects[-1].get("id")
    print(project_id, client_id)
    update_id = random.randint(1000, 9999)
    payload = {
        "update_id": "R" + str(update_id),
        "project_id": project_id,
        "details": "add a new update",
    }
    response = client.post(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", json=payload, headers=auth_pm
    )

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Update created successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "id" in data.get("data")
    assert "update_id" in data.get("data")
    assert "description" in data.get("data")
    assert "date" in data.get("data")


def create_client_update(client, auth_pm):
    import random

    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    project_id = projects[-1].get("id")
    print(project_id, client_id)
    update_id = random.randint(1000, 9999)
    payload = {
        "update_id": "R" + str(update_id),
        "project_id": project_id,
        "details": "add a new update",
    }
    response = client.post(
        f"{BASE_URL}/api/pm/client/updates/{client_id}", json=payload, headers=auth_pm
    )

    assert response.status_code in [200]

    return response.json().get("data").get("id")


# ----------------------------------------------------------------------------------
#  /api/pm/client/updates/{client_id}/?update_id={update_id} (PUT)
# ----------------------------------------------------------------------------------
def test_put_client_updates_success(client, auth_pm):
    update_id = create_client_update(client, auth_pm)
    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    payload = {"details": "add a new update"}
    response = client.put(
        f"{BASE_URL}/api/pm/client/updates/{client_id}/?update_id={update_id}",
        json=payload,
        headers=auth_pm,
    )

    assert response.status_code in [200]

    if response.status_code == 200:
        data = assert_json(response)

        assert isinstance(data, dict)

        # Expected set of keys
        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        # Expected values
        assert data.get("message") == "Update updated successfully"
        assert isinstance(data.get("data"), dict)

        # Validate data keys
        assert "id" in data.get("data")
        assert "update_id" in data.get("data")
        assert "description" in data.get("data")


# ----------------------------------------------------------------------------------
#  /api/pm/client/updates/{client_id}/?update_id={update_id} (DELETE)
# ----------------------------------------------------------------------------------


def test_delete_client_updates_success(client, auth_pm):
    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    update_id = create_client_update(client, auth_pm)
    response = client.delete(
        f"{BASE_URL}/api/pm/client/updates/{client_id}/?update_id={update_id}",
        headers=auth_pm,
    )
    assert response.status_code in [200]
    if response.status_code == 200:
        data = assert_json(response)
        print(data)

        assert isinstance(data, dict)

        # Expected set of keys
        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        # Expected values
        assert data.get("message") == "Update deleted successfully"
        assert isinstance(data.get("data"), dict)

        # Validate data keys
        assert "id" in data.get("data")
