import pytest
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def client():
    """HTTP client used for all external API requests."""
    with httpx.Client(base_url=API_BASE_URL) as c:
        yield c


@pytest.fixture
def sample_employee_payload():
    return {
        "name": "John Doe",
        "email": "john@test.com",
        "role": "Engineer"
    }


@pytest.fixture
def sample_policy_payload():
    return {
        "title": "Policy A",
        "content": "Content here"
    }


@pytest.fixture
def sample_review_payload():
    return {
        "user_id": 1,
        "rating": 4,
        "comments": "Good"
    }
import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
HR_USER_EMAIL = os.getenv("HR_USER_EMAIL")
HR_USER_PASSWORD = os.getenv("HR_USER_PASSWORD")


@pytest.fixture(scope="session")
def hr_token():
    """Automatically logs in PM & returns token"""
    login_url = f"{BASE_URL}/user/login"
    payload = {"email": HR_USER_EMAIL, "password": HR_USER_PASSWORD}

    with httpx.Client() as client:
        res = client.post(login_url, json=payload)

    assert res.status_code == 200, "HR login failed"

    return res.json()["access_token"]


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL + "/api"


@pytest.fixture
def auth_hr(hr_token):
    """Returns headers for hr authenticated requests"""
    return {"Authorization": f"Bearer {hr_token}"}
