def test_list_policies(client):
    res = client.get("/policies")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_create_and_get_policy(client, sample_policy_payload):
    create = client.post("/policies", json=sample_policy_payload)
    assert create.status_code in [200, 201]

    policy_id = create.json()["id"]

    get = client.get(f"/policies/{policy_id}")
    assert get.status_code == 200
    assert get.json()["title"] == sample_policy_payload["title"]


def test_create_policy_missing_title(client):
    res = client.post("/policies", json={"content": "Some rule"})
    assert res.status_code == 422


def test_update_policy(client, sample_policy_payload):
    create = client.post("/policies", json=sample_policy_payload)
    policy_id = create.json()["id"]

    res = client.put(f"/policies/{policy_id}", json={"title": "Updated"})
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"


def test_delete_policy(client, sample_policy_payload):
    create = client.post("/policies", json=sample_policy_payload)
    policy_id = create.json()["id"]

    res = client.delete(f"/policies/{policy_id}")
    assert res.status_code == 200
    assert res.json()["message"] == "Policy deleted"
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
