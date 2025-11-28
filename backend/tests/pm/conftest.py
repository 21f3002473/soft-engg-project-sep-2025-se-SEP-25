import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

PM_USER_EMAIL = os.getenv("PM_USER_EMAIL")
PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD")


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
def base_url():
    return BASE_URL + "/api"



@pytest.fixture
def auth_pm(pm_token):
    """Returns headers for pm authenticated requests"""
    return {"Authorization": f"Bearer {pm_token}"}
