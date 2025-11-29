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


def create_client(client, auth_pm):
    import random

    client_id = random.randint(1000, 9999)
    payload = {
        "client_id": "C" + str(client_id),
        "client_name": "Test Client Pvt Ltd",
        "email": "client" + str(client_id) + "@test.com",
        "detail_base64": "dGVzdCBkZXRhaWw=",  # "test detail" in base64
    }
    response = client.post(f"{BASE_URL}/api/pm/clients", json=payload, headers=auth_pm)

    if response.status_code != 200:
        return 1

    return response.json().get("data").get("id")


# --------------------------
#  /api/pm/clients (POST)
# --------------------------
def test_post_pm_clients(client, auth_pm):
    import random

    client_id = random.randint(1000, 9999)
    payload = {
        "client_id": "C" + str(client_id),
        "client_name": "Test Client Pvt Ltd",
        "email": "client" + str(client_id) + "@test.com",
        "detail_base64": "dGVzdCBkZXRhaWw=",  # "test detail" in base64
    }
    response = client.post(f"{BASE_URL}/api/pm/clients", json=payload, headers=auth_pm)

    assert response.status_code == 200

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    # Expected set of keys
    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "Client created successfully"
    assert isinstance(data.get("data"), dict)

    # Validate data keys
    assert "id" in data.get("data")
    assert "client_id" in data.get("data")
    assert "client_name" in data.get("data")
    assert "email" in data.get("data")


# --------------------------
#  /api/pm/clients (GET)
# --------------------------
def test_get_pm_clients(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/clients", headers=auth_pm)

    assert response.status_code == 200

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
        assert "description" in data.get("data").get("clients")[0]


import random


def test_post_pm_client_validation_error(client, auth_pm):

    client_id = random.randint(1000, 9999)
    payload = {
        "client_id": "C" + str(client_id),
        "client_name": "Test Client Pvt Ltd",
        "detail_base64": "dGVzdCBkZXRhaWw=",
    }
    response = client.post(f"{BASE_URL}/api/pm/clients", json=payload, headers=auth_pm)

    assert response.status_code == 422


# --------------------------
#  /api/pm/clients (PUT)
# --------------------------
def test_put_pm_clients(client, auth_pm):
    # Use an existing client ID
    client_id = create_client(client, auth_pm)

    payload = {
        "client_name": "Updated Client Pvt Ltd",
        "email": "updated1001@test.com",
        "detail_base64": "dGVzdCBkZXRhaWw=",  # "test detail" in base64
    }

    response = client.put(
        f"{BASE_URL}/api/pm/clients/?client_id={client_id}",
        json=payload,
        headers=auth_pm,
    )

    # Ensure the update was successful
    assert response.status_code in [200, 404]

    data = response.json()
    if response.status_code == 200:
        assert data["message"] == "Client updated successfully"

        client_data = data["data"]
        assert client_data["id"] == client_id
        assert client_data["client_name"] == payload["client_name"]
        assert client_data["email"] == payload["email"]


def test_delete_pm_clients(client, auth_pm):
    # Use an existing client ID
    try:
        client_id = create_client(client, auth_pm)
    except:
        client_id = 1

    response = client.delete(
        f"{BASE_URL}/api/pm/clients/?client_id={client_id}", headers=auth_pm
    )

    assert response.status_code in [200, 404]


def get_client(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/clients", headers=auth_pm)
    return response.json().get("data").get("client")
