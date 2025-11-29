import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_list_employees():
    response = client.get("/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_employee_valid(sample_employee):
    response = client.get(f"/employees/{sample_employee.id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_employee.id


def test_get_employee_invalid():
    response = client.get("/employees/999")
    assert response.status_code == 404


def test_update_employee_valid(sample_employee):
    payload = {"name": "New Name", "email": "new@test.com"}
    response = client.put(f"/employees/{sample_employee.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["email"] == "new@test.com"


def test_update_employee_invalid_id():
    response = client.put("/employees/999", json={"name": "Test"})
    assert response.status_code == 404


def test_update_employee_invalid_fields(sample_employee):
    response = client.put(f"/employees/{sample_employee.id}", json={"password": "hack"})
    assert response.status_code == 200
    assert "password" not in response.json()


def test_delete_employee_valid(sample_employee):
    response = client.delete(f"/employees/{sample_employee.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted"


def test_delete_employee_invalid():
    response = client.delete("/employees/999")
    assert response.status_code == 404
