import pytest
from app.database import User
from app.database.connection import engine
from app.database.hr_models import HRPolicy, PerformanceReview
from sqlmodel import Session


@pytest.fixture
def session():
    with Session(engine) as s:
        yield s


@pytest.fixture
def sample_employee(session):
    emp = User(name="John Doe", email="john@test.com", role="Engineer")
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@pytest.fixture
def sample_policy(session):
    p = HRPolicy(title="Policy A", content="Content here")
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@pytest.fixture
def sample_review(session, sample_employee):
    r = PerformanceReview(user_id=sample_employee.id, rating=4, comments="Good")
    session.add(r)
    session.commit()
    session.refresh(r)
    return r
