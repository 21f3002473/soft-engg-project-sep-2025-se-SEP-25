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
