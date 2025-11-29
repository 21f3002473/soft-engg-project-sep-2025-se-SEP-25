import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

EMPLOYEE_EMAIL = os.getenv("EMPLOYEE_USER_EMAIL")
EMPLOYEE_PASSWORD = os.getenv("EMPLOYEE_USER_PASSWORD")

HR_EMAIL = os.getenv("HR_USER_EMAIL")
HR_PASSWORD = os.getenv("HR_USER_PASSWORD")


@pytest.fixture(scope="session")
def employee_token():
    """Automatically logs in employee & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": EMPLOYEE_EMAIL, "password": EMPLOYEE_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "Employee login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def hr_token():
    """Automatically logs in HR & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": HR_EMAIL, "password": HR_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "HR login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL + "/api"


@pytest.fixture
def auth_employee(employee_token):
    """Returns headers for employee authenticated requests"""
    return {"Authorization": f"Bearer {employee_token}"}


@pytest.fixture
def auth_hr(hr_token):
    """Returns headers for HR authenticated requests"""
    return {"Authorization": f"Bearer {hr_token}"}


print(BASE_URL)
print(EMPLOYEE_EMAIL)
print(EMPLOYEE_PASSWORD)
print(HR_EMAIL)
print(HR_PASSWORD)
