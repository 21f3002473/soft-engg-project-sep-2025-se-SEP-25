import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
HR_USER_EMAIL = os.getenv("HR_USER_EMAIL")
HR_USER_PASSWORD = os.getenv("HR_USER_PASSWORD")
PM_USER_EMAIL = os.getenv("PM_USER_EMAIL")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD")

ROOT_USER_EMAIL = os.getenv("ROOT_USER_EMAIL")
ROOT_USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD")

EMP_USER_EMAIL = os.getenv("EMPLOYEE_USER_EMAIL")
EMP_USER_PASSWORD = os.getenv("EMPLOYEE_USER_PASSWORD")


@pytest.fixture(scope="session")
def admin_token():
    """Automatically logs in Admin & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": ROOT_USER_EMAIL, "password": ROOT_USER_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "Admin login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def employee_token():
    """Automatically logs in employee & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": EMP_USER_EMAIL, "password": EMP_USER_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "employee login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def pm_token():
    """Automatically logs in PM & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": PM_USER_EMAIL, "password": PM_USER_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "PM login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def hr_token():
    """Automatically logs in HR & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": HR_USER_EMAIL, "password": HR_USER_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "HR login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL + "/api"


@pytest.fixture(scope="session")
def auth_hr(hr_token):
    """Returns headers for hr authenticated requests"""
    return {"Authorization": f"Bearer {hr_token}"}


@pytest.fixture(scope="session")
def auth_pm(pm_token):
    """Returns headers for pm authenticated requests"""
    return {"Authorization": f"Bearer {pm_token}"}


@pytest.fixture(scope="session")
def auth_admin(admin_token):
    """Returns headers for admin authenticated requests"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def auth_employee(employee_token):
    """Returns headers for employee authenticated requests"""
    return {"Authorization": f"Bearer {employee_token}"}


print(BASE_URL)
print(HR_USER_EMAIL, HR_USER_PASSWORD)
print(PM_USER_EMAIL, PM_USER_PASSWORD)
print(ROOT_USER_EMAIL, ROOT_USER_PASSWORD)
print(EMP_USER_EMAIL, EMP_USER_PASSWORD)
