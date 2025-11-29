from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_get_all_reviews():
    response = client.get("/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_reviews_by_user_valid(sample_review):
    response = client.get(f"/reviews/user/{sample_review.user_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_reviews_by_user_invalid():
    response = client.get("/reviews/user/999")
    assert response.status_code == 200
    assert response.json() == []


def test_create_review_valid(sample_employee):
    payload = {"user_id": sample_employee.id, "rating": 5, "comments": "Good"}
    response = client.post("/reviews", json=payload)
    assert response.status_code in [200, 201]
    assert response.json()["rating"] == 5


def test_create_review_user_not_found():
    payload = {"user_id": 999, "rating": 4}
    response = client.post("/reviews", json=payload)
    assert response.status_code == 404


def test_update_review_valid(sample_review):
    response = client.put(
        f"/reviews/{sample_review.id}",
        json={"rating": 5}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5


def test_update_review_invalid():
    response = client.put("/reviews/999", json={"rating": 3})
    assert response.status_code == 404


def test_delete_review_valid(sample_review):
    response = client.delete(f"/reviews/{sample_review.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Review deleted"


def test_delete_review_invalid():
    response = client.delete("/reviews/999")
    assert response.status_code == 404
