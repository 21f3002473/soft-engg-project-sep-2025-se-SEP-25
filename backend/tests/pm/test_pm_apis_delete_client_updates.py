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



def test_delete_client_update_success(client):
    """
    Login as PM and attempt to delete an update for a client.
    Accept 200 (deleted) or 404 (not found) depending on DB state.
    """
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client_id = 1      
    update_id = 1      

    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    resp = client.delete(url, headers=headers, params={"update_id": update_id})

    assert resp.status_code in [200, 404]

    if resp.status_code == 200:
        data = assert_json(resp)
      
        assert isinstance(data, str)


def test_delete_client_update_missing_update_id(client):
  
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/updates/{client_id}"

    resp = client.delete(url, headers=headers)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
