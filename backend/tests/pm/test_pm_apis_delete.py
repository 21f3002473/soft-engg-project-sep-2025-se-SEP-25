# import pytest
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# BASE_URL = "http://localhost:8000"

# PM_USER_EMAIL = os.getenv("PM_USER_EMAIL", "pm@gmail.com")
# PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD", "pm@gmail.com")


# @pytest.fixture
# def client():
#     return requests


# def assert_json(response):
#     assert "application/json" in response.headers.get("Content-Type", "")
#     return response.json()


# # -------------------------------------------------
# #   DELETE /api/pm/clients?client_id=INTEGER
# # -------------------------------------------------

# def test_delete_pm_client_success(client):
#     """
#     Steps:
#     1. Login as PM → get access token.
#     2. Call DELETE /api/pm/clients with client_id in query.
#     """

#     # Step 1: Login & get token
#     login_payload = {
#         "email": PM_USER_EMAIL,
#         "password": PM_USER_PASSWORD
#     }

#     login_resp = client.post(f"{BASE_URL}/user/login", json=login_payload)

#     assert login_resp.status_code in [200, 201]

#     login_data = assert_json(login_resp)
#     assert "access_token" in login_data

#     token = login_data["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     # -------------------------------------------
#     # Step 2: DELETE client                        ← change client_id as required
#     # -------------------------------------------

#     client_id_to_delete = 1   # <-- SET A VALID CLIENT ID IN YOUR DB

#     delete_resp = client.delete(
#         f"{BASE_URL}/api/pm/clients",
#         headers=headers,
#         params={"client_id": client_id_to_delete}
#     )

#     # API spec: Success → 200
#     assert delete_resp.status_code == 200

#     data = assert_json(delete_resp)

#     # Successful Response schema from Swagger seems to be a string
#     assert isinstance(data, str)


# # -------------------------------------------------
# #   NEGATIVE TEST → 422 VALIDATION ERROR
# # -------------------------------------------------

# def test_delete_pm_client_missing_id(client):
#     """
#     Calling DELETE without client_id → should give 422 Validation Error.
#     """

#     delete_resp = client.delete(f"{BASE_URL}/api/pm/clients")

#     # 422 expected
#     assert delete_resp.status_code == 422

#     data = assert_json(delete_resp)
#     assert "detail" in data

# tests/pm/test_pm_apis_delete.py

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


# -------------------------------------------------
#   DELETE /api/pm/clients?client_id=INTEGER
# -------------------------------------------------

def test_delete_pm_client_success(client):
    """
    Login as PM and attempt to delete a client.
    We accept 200 (deleted) OR 404 (client not found).
    """
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client_id_to_delete = 1  # change if you know a valid id

    resp = client.delete(
        f"{BASE_URL}/api/pm/clients",
        headers=headers,
        params={"client_id": client_id_to_delete},
    )

    # OK if client exists or not
    assert resp.status_code in [200]

    if resp.status_code == 200:
        data = assert_json(resp)
        assert isinstance(data, str)


def test_delete_pm_client_missing_id(client):
    """
    Login as PM but *do not* provide client_id → should trigger 422 validation error.
    """
    token = get_pm_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.delete(f"{BASE_URL}/api/pm/clients", headers=headers)

    assert resp.status_code == 422

    data = assert_json(resp)
    assert "detail" in data
