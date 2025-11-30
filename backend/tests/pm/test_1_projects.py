import os

import pytest
import requests
from dotenv import load_dotenv
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


def create_project(client, auth_pm):
    import random

    project_id = random.randint(1000, 9999)
    try:
        client_id = create_client(client, auth_pm)
    except:
        client_id = 1
    payload = {
        "project_id": "P" + str(project_id),
        "project_name": "Test Project Pvt Ltd",
        "description": "Test Project Pvt Ltd",
        "status": "PENDING",
        "client_id": client_id,
        "manager_id": 1,
    }
    response = client.post(f"{BASE_URL}/api/pm/projects", json=payload, headers=auth_pm)
    if response.status_code != 200:
        return 1
    return response.json().get("data").get("id")


# --------------------------
#  /api/pm/projects (POST)
# --------------------------


def test_post_pm_projects(client, auth_pm):
    import random

    project_id = random.randint(1000, 9999)

    try:
        client_id = create_client(client, auth_pm)
    except:
        client_id = 1
    payload = {
        "project_id": "P" + str(project_id),
        "project_name": "Test Project Pvt Ltd",
        "description": "Test Project Pvt Ltd",
        "status": "PENDING",
        "client_id": client_id,
        "manager_id": 1,
    }
    response = client.post(f"{BASE_URL}/api/pm/projects", json=payload, headers=auth_pm)

    data = assert_json(response)
    print(data)

    assert response.status_code in [200]

    if response.status_code == 200:
        assert isinstance(data, dict)

        # Expected set of keys
        expected_keys = {"message", "data"}
        assert set(data.keys()) == expected_keys

        # Expected values
        assert data.get("message") == "Project created successfully"
        assert isinstance(data.get("data"), dict)

        # Validate data keys
        assert "id" in data.get("data")
        assert "project_id" in data.get("data")
        assert "project_name" in data.get("data")
        assert "status" in data.get("data")
        assert "client_id" in data.get("data")


# --------------------------
#  /api/pm/projects (PUT)
# --------------------------


def test_put_pm_projects(client, auth_pm):
    project_id = create_project(client, auth_pm)
    payload = {
        "project_name": "Updated Project Pvt Ltd",
        "description": "Updated Project Pvt Ltd",
        "status": "PENDING",
        "manager_id": 1,
    }
    response = client.put(
        f"{BASE_URL}/api/pm/projects/?project_id={project_id}",
        json=payload,
        headers=auth_pm,
    )

    # Ensure the update was successful
    assert response.status_code in [200]

    data = response.json()
    if response.status_code == 200:
        assert data["message"] == "Project updated successfully"

        project_data = data["data"]
        assert project_data["id"] == project_id
        assert project_data["project_name"] == payload["project_name"]
        assert project_data["status"] == payload["status"]
        assert project_data["description"] == payload["description"]


def test_delete_pm_projects(client, auth_pm):
    try:
        project_id = create_project(client, auth_pm)
    except:
        project_id = 1

    response = client.delete(
        f"{BASE_URL}/api/pm/projects/?project_id={project_id}", headers=auth_pm
    )

    assert response.status_code in [200]


# --------------------------
#  /api/pm/projects (GET)
# --------------------------


def test_get_pm_projects(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/projects", headers=auth_pm)

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


def test_get_pm_projects_failure(client, auth_pm):
    projects = get_projects(client, auth_pm)
    project_id = projects[0].get("id")
    response = client.get(f"{BASE_URL}/api/pm/projects", headers={})
    assert response.status_code == 401


def get_projects(client, auth_pm):
    response = client.get(f"{BASE_URL}/api/pm/projects/", headers=auth_pm)

    assert response.status_code in [200]
    if response.status_code == 200:
        return response.json().get("data").get("projects")
    return []
