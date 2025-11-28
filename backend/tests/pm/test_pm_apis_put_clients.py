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



def test_put_pm_client_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id_to_update = 1  

    payload = {
        "client_name": "Updated Client Pvt Ltd",
        "email": "updatedclient@test.com",
        "detail_base64": "dXBkYXRlZCBkZXRhaWw=", 
    }

    resp = client.put(
        f"{BASE_URL}/api/pm/clients",
        headers=headers,
        params={"client_id": client_id_to_update},
        json=payload,
    )

   
    assert resp.status_code in [200, 404]

    if resp.status_code == 200:
        data = assert_json(resp)

       
        assert "message" in data
        
        assert isinstance(data["message"], str)

        if "data" in data:
            client_data = data["data"]
            assert isinstance(client_data, dict)
            assert client_data.get("client_name") == payload["client_name"]
            assert client_data.get("email") == payload["email"]


def test_put_pm_client_missing_id(client):
    """
    Missing client_id in query -> 422 Validation Error
    (after successful authentication).
    """
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "client_name": "No ID Client",
        "email": "noid@test.com",
        "detail_base64": "bm8gaWQ=",  
    }

    resp = client.put(
        f"{BASE_URL}/api/pm/clients",
        headers=headers,
        json=payload,  
    )

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
