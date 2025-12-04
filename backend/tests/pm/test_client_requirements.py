import os

import pytest
import requests
from dotenv import load_dotenv
from test_1_projects import create_project, get_projects

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


from test_clients import create_client


#  /api/pm/client/requirements/{client_id} (GET)
def test_get_client_requirements_success(client, auth_pm):
    client_id = create_client(client, auth_pm)
    response = client.get(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}", headers=auth_pm
    )

    assert response.status_code in [200, 204]

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    assert data.get("message") == "Requirements retrieved successfully"
    assert isinstance(data.get("data"), dict)

    assert "client" in data.get("data")
    assert "requirements" in data.get("data")
    assert "total_requirements" in data.get("data")

    if data.get("data").get("requirements"):
        assert "id" in data.get("data").get("requirements")[0]
        assert "requirement_id" in data.get("data").get("requirements")[0]
        assert "description" in data.get("data").get("requirements")[0]
        assert "project_id" in data.get("data").get("requirements")[0]


#  /api/pm/client/requirements/{client_id} (POST)
def test_post_client_requirements_success(client, auth_pm):
    import random

    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    project_id = projects[-1].get("id")
    requirement_id = random.randint(1000, 9999)
    payload = {
        "requirement_id": "R" + str(requirement_id),
        "requirements": "add a new requirement",
        "project_id": project_id,
    }
    response = client.post(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}",
        json=payload,
        headers=auth_pm,
    )

    assert response.status_code in [200]

    data = assert_json(response)
    print(data)

    assert isinstance(data, dict)

    expected_keys = {"message", "data"}
    assert set(data.keys()) == expected_keys

    assert data.get("message") == "Requirement created successfully"
    assert isinstance(data.get("data"), dict)

    assert "id" in data.get("data")
    assert "requirement_id" in data.get("data")
    assert "description" in data.get("data")
    assert "project_id" in data.get("data")


def create_client_requirement(client, auth_pm):
    import random

    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    project_id = projects[-1].get("id")
    requirement_id = random.randint(1000, 9999)
    payload = {
        "requirement_id": "R" + str(requirement_id),
        "requirements": "add a new requirement",
        "project_id": project_id,
    }
    response = client.post(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}",
        json=payload,
        headers=auth_pm,
    )

    return response.json().get("data").get("id")


#  /api/pm/client/requirements/{client_id}/?requirement_id={requirement_id} (PUT)
def test_put_client_requirements_success(client, auth_pm):
    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    project_id = projects[-1].get("id")
    requirement_id = create_client_requirement(client, auth_pm)
    payload = {"requirements": "update requirement", "project_id": project_id}
    response = client.put(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}/?requirement_id={requirement_id}",
        json=payload,
        headers=auth_pm,
    )

    assert response.status_code in [200]

    if response.status_code == 200:
        data = assert_json(response)
        print(data)

        assert isinstance(data, dict)

        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        assert data.get("message") == "Requirement updated successfully"
        assert isinstance(data.get("data"), dict)

        assert "id" in data.get("data")
        assert "requirement_id" in data.get("data")
        assert "description" in data.get("data")


#  /api/pm/client/requirements/{client_id}/?requirement_id={requirement_id} (DELETE)
def test_delete_client_requirement_success(client, auth_pm):
    projects = get_projects(client, auth_pm)
    client_id = projects[-1].get("client_id")
    requirement_id = create_client_requirement(client, auth_pm)
    response = client.delete(
        f"{BASE_URL}/api/pm/client/requirements/{client_id}/?requirement_id={requirement_id}",
        headers=auth_pm,
    )
    assert response.status_code in [200]
    if response.status_code == 200:
        data = assert_json(response)
        print(data)

        assert isinstance(data, dict)

        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        assert data.get("message") == "Requirement deleted successfully"
        assert isinstance(data.get("data"), dict)

        assert "id" in data.get("data")
