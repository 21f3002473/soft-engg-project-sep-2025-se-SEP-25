from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_policies():
    response = client.get("/policies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_policy_valid(sample_policy):
    response = client.get(f"/policies/{sample_policy.id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_policy.id


def test_get_policy_invalid():
    response = client.get("/policies/999")
    assert response.status_code == 404


def test_create_policy_valid():
    payload = {"title": "Leave Policy", "content": "Some rules"}
    response = client.post("/policies", json=payload)
    assert response.status_code in [200, 201]
    assert response.json()["title"] == "Leave Policy"


def test_create_policy_missing_title():
    response = client.post("/policies", json={"content": "Rules"})
    assert response.status_code == 422


def test_update_policy_valid(sample_policy):
    payload = {"title": "Updated Title"}
    response = client.put(f"/policies/{sample_policy.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_policy_invalid_id():
    response = client.put("/policies/999", json={"title": "Test"})
    assert response.status_code == 404


def test_delete_policy_valid(sample_policy):
    response = client.delete(f"/policies/{sample_policy.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Policy deleted"


def test_delete_policy_invalid():
    response = client.delete("/policies/999")
    assert response.status_code == 404
