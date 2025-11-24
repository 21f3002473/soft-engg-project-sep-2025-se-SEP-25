import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.fixture
def client():
    return requests

def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()

# --------------------------
#  /api/user/login (GET)
# --------------------------

def test_get_user_login(client):
    response = client.get(f"{BASE_URL}/user/login")

    assert response.status_code == 200

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message"}
    assert set(data.keys()) == expected_keys

    assert data.get("message") == "User login endpoint"

# --------------------------
#  /api/user/login (POST)
# --------------------------

def test_post_admin_login(client):
    payload = {"email": "root@gmail.com", "password": "root@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "root"

# --------------------------
#  /api/user/login (POST)
# --------------------------

def test_post_pm_login(client):
    payload = {"email": "pm@gmail.com", "password": "pm@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "product_manager"

# --------------------------
#  /api/user/login (POST)
# --------------------------

def test_post_hr_login(client):
    payload = {"email": "hr@gmail.com", "password": "hr@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "human_resource"

# --------------------------
#  /api/user/login (POST)
# --------------------------

def test_post_employee_login(client):
    payload = {"email": "emp@gmail.com", "password": "emp@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [200, 201]

    data = assert_json(response)

    # Expected set of keys
    expected_keys = {"message", "access_token", "token_type", "role"}
    assert set(data.keys()) == expected_keys

    # Expected values
    assert data.get("message") == "User logged in successfully"
    assert data.get("token_type") == "bearer"
    assert data.get("role") == "employee"

# --------------------------
#  /api/user/login (POST)
# --------------------------

def test_post_bad_login(client):
    payload = {"email": "root@gmail.com", "password": "root1@gmail.com"}
    response = client.post(f"{BASE_URL}/user/login", json=payload)

    assert response.status_code in [401, 403]

    data = assert_json(response)

    assert "detail" in data
    assert data.get("detail") == "Invalid email or password"
