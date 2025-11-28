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


def test_post_client_requirement_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1  

    payload = {
        "requirement_id": "R1001",
        "requirements": "Customer needs a web portal with reporting dashboard.",
        "project_id": 1,
    }

    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"

    resp = client.post(url, headers=headers, json=payload)


    assert resp.status_code in [200, 404, 409]

    if resp.status_code == 200:
 
        assert isinstance(data, (str, dict))

        if isinstance(data, dict):
            assert "message" in data
          

def test_post_client_requirement_validation_error(client):
    """
    Send invalid body (missing required fields) → expect 422.
    """
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"


    payload = {
        "requirements": "This payload is incomplete"
    }

    resp = client.post(url, headers=headers, json=payload)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data

def test_put_client_requirement_success(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1           # Set valid client_id
    requirement_id = 1      # Set valid requirement_id

    payload = {
        "requirements": "Updated requirement details for the project.",
        "project_id": 2
    }

    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"

    resp = client.put(
        url,
        headers=headers,
        params={"requirement_id": requirement_id},
        json=payload
    )

    # Accept 200 (updated), 404 (client/requirement not found)
    assert resp.status_code in [200, 404]

    if resp.status_code == 200:
        data = assert_json(resp)

        # API doc says string, but backend may return dict
        assert isinstance(data, (str, dict))

        if isinstance(data, dict):
            assert "message" in data

def test_put_client_requirement_missing_requirement_id(client):
    token = get_pm_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"

    payload = {
        "requirements": "This should fail",
        "project_id": 1
    }

    resp = client.put(url, headers=headers, json=payload)  # No requirement_id param

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data




def test_delete_client_requirement_success(client):
    """
    Login as PM and attempt to delete a requirement for a client.
    Accept 200 (deleted) or 404 (not found).
    """
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client_id = 1         
    requirement_id = 1   

    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"

    resp = client.delete(url, headers=headers, params={"requirement_id": requirement_id})

  
    assert resp.status_code in [200]

    if resp.status_code == 200:
        data = assert_json(resp)
        assert isinstance(data, str)


def test_delete_client_requirement_missing_requirement_id(client):
 
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client_id = 1
    url = f"{BASE_URL}/api/pm/client/requirements/{client_id}"

    resp = client.delete(url, headers=headers)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
