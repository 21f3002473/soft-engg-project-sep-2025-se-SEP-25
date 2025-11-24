import json

import pytest
import requests

BASE_URL = "http://localhost:8000/api"


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# 1) /employee/learning (LearningResource)


def test_get_learning_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    response = client.get(f"{BASE_URL}/employee/learning", headers=headers)

    assert response.status_code == 200
    data = assert_json(response)

    assert "message" in data
    assert "personalized" in data
    assert "recommended" in data
    assert isinstance(data["personalized"], list)
    assert isinstance(data["recommended"], list)


def test_get_learning_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/learning")
    assert response.status_code in [401, 403]


def test_get_learning_internal_error(client, monkeypatch):
    def bad_query(*a, **kw):
        raise Exception("DB error")

    monkeypatch.setattr("sqlmodel.Session.exec", bad_query)

    headers = {"Authorization": "Bearer employee_token"}
    response = client.get(f"{BASE_URL}/employee/learning", headers=headers)

    assert response.status_code == 500
    data = assert_json(response)
    assert data.get("detail") == "Internal server error"


# 2) /hr/course (CourseAdminListCreateResource)


def test_get_courses_admin_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course", headers=headers)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_courses_admin_unauthorized(client):
    response = client.get(f"{BASE_URL}/hr/course")
    assert response.status_code in [401, 403]


def test_post_courses_admin_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {
        "course_name": "Deep Learning",
        "course_link": "https://example.com/dl",
        "topics": "Neural Networks, CNN",
    }

    response = client.post(f"{BASE_URL}/hr/course", json=payload, headers=headers)
    assert response.status_code in [200, 201]

    data = assert_json(response)
    assert data.get("message") == "Course created"
    assert "id" in data


def test_post_courses_admin_missing_name(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.post(f"{BASE_URL}/hr/course", json={}, headers=headers)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "course_name is required"


# 3) /hr/course/{course_id}  (CourseAdminDetailResource)


def test_get_course_detail_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course/1", headers=headers)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {"id", "course_name", "course_link", "topics"}


def test_get_course_detail_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


def test_put_course_detail_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"course_name": "Updated course"}

    response = client.put(f"{BASE_URL}/hr/course/1", json=payload, headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Course updated"


def test_put_course_detail_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.put(
        f"{BASE_URL}/hr/course/999999",
        json={"course_name": "test"},
        headers=headers,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


def test_delete_course_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.delete(f"{BASE_URL}/hr/course/1", headers=headers)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Course deleted"


def test_delete_course_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.delete(f"{BASE_URL}/hr/course/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


# 4) /hr/course/assign/{user_id}  (CourseAssignmentListResource)


def test_get_course_assignments_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course/assign/1", headers=headers)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_course_assignments_unauthorized(client):
    response = client.get(f"{BASE_URL}/hr/course/assign/1")
    assert response.status_code in [401, 403]


def test_post_assign_course_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"course_id": 1}

    response = client.post(
        f"{BASE_URL}/hr/course/assign/1",
        json=payload,
        headers=headers,
    )

    assert response.status_code in [200, 201]
    data = assert_json(response)

    assert data.get("message") == "Course assigned"
    assert "id" in data


def test_post_assign_missing_fields(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.post(f"{BASE_URL}/hr/course/assign/1", json={}, headers=headers)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "user_id and course_id required"


def test_post_assign_course_already_exists(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"course_id": 1}

    client.post(f"{BASE_URL}/hr/course/assign/1", json=payload, headers=headers)

    response = client.post(
        f"{BASE_URL}/hr/course/assign/1", json=payload, headers=headers
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Course already assigned to this user"


# 5) /hr/course/assign/edit/{assign_id}  (CourseAssignmentDetailResource)


def test_get_assignment_detail_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course/assign/edit/1", headers=headers)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {
            "id",
            "user_id",
            "course_id",
            "course_name",
            "status",
        }


def test_get_assignment_detail_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/course/assign/edit/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


def test_put_assignment_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"status": "completed"}

    response = client.put(
        f"{BASE_URL}/hr/course/assign/edit/1",
        json=payload,
        headers=headers,
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Assignment updated"


def test_put_assignment_invalid_status(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"status": "INVALID"}

    response = client.put(
        f"{BASE_URL}/hr/course/assign/edit/1",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_assignment_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.put(
        f"{BASE_URL}/hr/course/assign/edit/999999",
        json={"status": "pending"},
        headers=headers,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


def test_delete_assignment_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.delete(f"{BASE_URL}/hr/course/assign/edit/1", headers=headers)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Assignment removed"


def test_delete_assignment_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.delete(
        f"{BASE_URL}/hr/course/assign/edit/999999", headers=headers
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


# 6) /employee/courses (CourseAssignmentEmployeeResource)


def test_get_employee_course_assignments_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    response = client.get(f"{BASE_URL}/employee/courses", headers=headers)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_employee_course_assignments_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/courses")
    assert response.status_code in [401, 403]


# 7) /employee/course/{course_id} (EmployeeCourseUpdateByCourseIdResource)


def test_put_employee_course_status_success(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"status": "completed"}

    response = client.put(
        f"{BASE_URL}/employee/course/1",
        json=payload,
        headers=headers,
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Course status updated"


def test_put_employee_course_status_missing_field(client):
    headers = {"Authorization": "Bearer employee_token"}

    response = client.put(
        f"{BASE_URL}/employee/course/1",
        json={},
        headers=headers,
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "status field is required"


def test_put_employee_course_status_invalid(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"status": "INVALID"}

    response = client.put(
        f"{BASE_URL}/employee/course/1",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_employee_course_status_not_found(client):
    headers = {"Authorization": "Bearer employee_token"}
    payload = {"status": "pending"}

    response = client.put(
        f"{BASE_URL}/employee/course/999999",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course assignment not found"


# 8) /employee/recommendations (CourseRecommendationResource)


def test_get_recommendations_success(client, monkeypatch):
    # Mock Gemini API
    class MockResponse:
        status_code = 200

        def json(self):
            return {
                "candidates": [{"content": {"parts": [{"text": '["Python Basics"]'}]}}]
            }

    async def mock_post(*a, **kw):
        return MockResponse()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    headers = {"Authorization": "Bearer employee_token"}
    response = client.get(f"{BASE_URL}/employee/recommendations", headers=headers)

    assert response.status_code == 200
    data = assert_json(response)

    assert "assigned_courses" in data
    assert "recommended_courses" in data
    assert isinstance(data["recommended_courses"], list)


def test_get_recommendations_error(client, monkeypatch):

    async def mock_post_error(*a, **kw):
        raise Exception("API failure")

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post_error)

    headers = {"Authorization": "Bearer employee_token"}
    response = client.get(f"{BASE_URL}/employee/recommendations", headers=headers)

    assert response.status_code == 500
    data = assert_json(response)
    assert data.get("detail") == "Internal server error"


def test_get_recommendations_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/recommendations")
    assert response.status_code in [401, 403]
