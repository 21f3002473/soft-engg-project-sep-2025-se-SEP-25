
import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

PM_USER_EMAIL = os.getenv("PM_USER_EMAIL", "pm@gmail.com")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD", "pm@gmail.com")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


def get_pm_token(client):
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}
    resp = client.post(f"{BASE_URL}/user/login", json=payload)

    assert resp.status_code in [200, 201]

    data = assert_json(resp)
    assert "access_token" in data
    return data["access_token"]


def test_post_pm_client_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "client_id": "C1001",
        "client_name": "Test Client Pvt Ltd",
        "email": "client1001@test.com",
        "detail_base64": "dGVzdCBkZXRhaWw="   
    }

    resp = client.post(f"{BASE_URL}/api/pm/clients", json=payload, headers=headers)


    assert resp.status_code in [200, 409]

    if resp.status_code == 200:
        data = assert_json(resp)

        
        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        assert data["message"] == "Client created successfully"

        client_data = data["data"]
        assert isinstance(client_data, dict)

        
        assert "id" in client_data
        assert isinstance(client_data["id"], int)

        assert client_data["client_id"] == payload["client_id"]
        assert client_data["client_name"] == payload["client_name"]
        assert client_data["email"] == payload["email"]

    elif resp.status_code == 409:
        
        data = assert_json(resp)
        assert "message" in data


def test_post_pm_client_validation_error(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "client_name": "Incomplete Client"
       
    }

    resp = client.post(f"{BASE_URL}/api/pm/clients", json=payload, headers=headers)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
