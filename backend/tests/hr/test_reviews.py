def test_get_all_reviews(client):
    res = client.get("/reviews")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_create_review(client, sample_employee_payload):
    # ensure user exists
    emp = client.post("/employees", json=sample_employee_payload)
    user_id = emp.json()["id"]

    payload = {"user_id": user_id, "rating": 5, "comments": "Good"}
    create = client.post("/reviews", json=payload)
    assert create.status_code in [200, 201]
    assert create.json()["rating"] == 5


def test_get_reviews_by_user(client, sample_employee_payload):
    emp = client.post("/employees", json=sample_employee_payload)
    user_id = emp.json()["id"]

    res = client.get(f"/reviews/user/{user_id}")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_create_review_user_not_found(client):
    res = client.post("/reviews", json={"user_id": 99999, "rating": 4})
    assert res.status_code == 404


def test_update_review(client, sample_employee_payload):
    emp = client.post("/employees", json=sample_employee_payload)
    user_id = emp.json()["id"]

    review = client.post("/reviews", json={"user_id": user_id, "rating": 3})
    rev_id = review.json()["id"]

    update = client.put(f"/reviews/{rev_id}", json={"rating": 5})
    assert update.status_code == 200
    assert update.json()["rating"] == 5


def test_delete_review(client, sample_employee_payload):
    emp = client.post("/employees", json=sample_employee_payload)
    user_id = emp.json()["id"]

    review = client.post("/reviews", json={"user_id": user_id, "rating": 3})
    rev_id = review.json()["id"]

    delete = client.delete(f"/reviews/{rev_id}")
    assert delete.status_code == 200
    assert delete.json()["message"] == "Review deleted"
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
