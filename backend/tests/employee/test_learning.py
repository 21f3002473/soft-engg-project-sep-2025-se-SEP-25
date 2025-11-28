import httpx
import pytest

def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# 1) /employee/learning (LearningResource)


def test_get_learning_success(base_url, auth_employee):
    response = httpx.get(f"{base_url}/employee/learning", headers=auth_employee)

    assert response.status_code == 200
    data = assert_json(response)

    assert "message" in data
    assert "personalized" in data
    assert "recommended" in data
    assert isinstance(data["personalized"], list)
    assert isinstance(data["recommended"], list)


def test_get_learning_unauthorized(base_url):
    response = httpx.get(f"{base_url}/employee/learning")
    assert response.status_code in [401, 403]


# 2) /hr/course (CourseAdminListCreateResource)


def test_get_courses_admin_success(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/course", headers=auth_hr)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_courses_admin_unauthorized(base_url):
    response = httpx.get(f"{base_url}/hr/course")
    assert response.status_code in [401, 403]


def test_post_courses_admin_success(base_url, auth_hr):
    payload = {
        "course_name": "Deep Learning",
        "course_link": "https://example.com/dl",
        "topics": "Neural Networks, CNN",
    }

    response = httpx.post(f"{base_url}/hr/course", json=payload, headers=auth_hr)
    assert response.status_code in [200, 201]

    data = assert_json(response)
    assert data.get("message") == "Course created"
    assert "id" in data


def test_post_courses_admin_missing_name(base_url, auth_hr):
    response = httpx.post(f"{base_url}/hr/course", json={}, headers=auth_hr)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "course_name is required"


# 3) /hr/course/{course_id} (CourseAdminDetailResource)


def test_get_course_detail_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course", headers=auth_hr)
    assert list_resp.status_code == 200
    courses = assert_json(list_resp)

    if not courses:
        pytest.skip("No courses available to test GET detail")

    course_id = courses[0]["id"]
    response = httpx.get(f"{base_url}/hr/course/{course_id}", headers=auth_hr)

    assert response.status_code == 200
    data = assert_json(response)
    assert set(data.keys()) == {"id", "course_name", "course_link", "topics"}


def test_get_course_detail_not_found(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/course/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


def test_put_course_detail_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course", headers=auth_hr)
    assert list_resp.status_code == 200
    courses = assert_json(list_resp)

    if not courses:
        pytest.skip("No courses available to test PUT")

    course_id = courses[0]["id"]
    payload = {"course_name": "Updated course"}

    response = httpx.put(
        f"{base_url}/hr/course/{course_id}", json=payload, headers=auth_hr
    )
    assert response.status_code == 200

    data = assert_json(response)
    assert data.get("message") == "Course updated"


def test_put_course_detail_not_found(base_url, auth_hr):
    response = httpx.put(
        f"{base_url}/hr/course/999999",
        json={"course_name": "test"},
        headers=auth_hr,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


def test_delete_course_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course", headers=auth_hr)
    assert list_resp.status_code == 200
    courses = assert_json(list_resp)

    if not courses:
        pytest.skip("No courses available to test DELETE")

    course_id = courses[0]["id"]
    response = httpx.delete(f"{base_url}/hr/course/{course_id}", headers=auth_hr)

    assert response.status_code == 200
    data = assert_json(response)
    assert data.get("message") == "Course deleted"


def test_delete_course_not_found(base_url, auth_hr):
    response = httpx.delete(f"{base_url}/hr/course/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course not found"


# 4) /hr/course/assign/{user_id} (CourseAssignmentListResource)


def test_get_course_assignments_success(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_course_assignments_unauthorized(base_url):
    response = httpx.get(f"{base_url}/hr/course/assign/4")
    assert response.status_code in [401, 403]


def test_post_assign_course_success(base_url, auth_hr):
    course_payload = {
        "course_name": "Test Course for Assignment",
        "course_link": "https://example.com/test-course",
        "topics": "Testing, Assignment",
    }
    course_resp = httpx.post(
        f"{base_url}/hr/course", json=course_payload, headers=auth_hr
    )
    assert course_resp.status_code in [200, 201]
    course_data = assert_json(course_resp)
    course_id = course_data.get("id")

    assign_payload = {"course_id": course_id}

    response = httpx.post(
        f"{base_url}/hr/course/assign/4",
        json=assign_payload,
        headers=auth_hr,
    )

    assert response.status_code in [200, 201]
    data = assert_json(response)
    assert data.get("message") == "Course assigned"
    assert "id" in data


def test_post_assign_missing_fields(base_url, auth_hr):
    response = httpx.post(f"{base_url}/hr/course/assign/4", json={}, headers=auth_hr)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "user_id and course_id required"


def test_post_assign_course_already_exists(base_url, auth_hr):
    course_payload = {
        "course_name": "Duplicate Assignment Test Course",
        "course_link": "https://example.com/dup-course",
        "topics": "Duplicate, Testing",
    }
    course_resp = httpx.post(
        f"{base_url}/hr/course", json=course_payload, headers=auth_hr
    )
    assert course_resp.status_code in [200, 201]
    course_data = assert_json(course_resp)
    course_id = course_data.get("id")

    assign_payload = {"course_id": course_id}

    httpx.post(f"{base_url}/hr/course/assign/4", json=assign_payload, headers=auth_hr)

    response = httpx.post(
        f"{base_url}/hr/course/assign/4", json=assign_payload, headers=auth_hr
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Course already assigned to this user"


# 5) /hr/course/assign/edit/{assign_id} (CourseAssignmentDetailResource)


def test_get_assignment_detail_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)
    assert list_resp.status_code == 200
    assignments = assert_json(list_resp)

    if not assignments:
        pytest.skip("No assignments available to test GET detail")

    assign_id = assignments[0]["id"]
    response = httpx.get(
        f"{base_url}/hr/course/assign/edit/{assign_id}", headers=auth_hr
    )

    assert response.status_code == 200
    data = assert_json(response)
    assert set(data.keys()) == {
        "id",
        "user_id",
        "course_id",
        "course_name",
        "status",
    }


def test_get_assignment_detail_not_found(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/course/assign/edit/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


def test_put_assignment_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)
    assert list_resp.status_code == 200
    assignments = assert_json(list_resp)

    if not assignments:
        pytest.skip("No assignments available to test PUT")

    assign_id = assignments[0]["id"]
    payload = {"status": "completed"}

    response = httpx.put(
        f"{base_url}/hr/course/assign/edit/{assign_id}",
        json=payload,
        headers=auth_hr,
    )

    assert response.status_code == 200
    data = assert_json(response)
    assert data.get("message") == "Assignment updated"


def test_put_assignment_invalid_status(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)
    assert list_resp.status_code == 200
    assignments = assert_json(list_resp)

    if not assignments:
        pytest.skip("No assignments available to test invalid status update")

    assign_id = assignments[0]["id"]
    payload = {"status": "INVALID"}

    response = httpx.put(
        f"{base_url}/hr/course/assign/edit/{assign_id}",
        json=payload,
        headers=auth_hr,
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_assignment_not_found(base_url, auth_hr):
    response = httpx.put(
        f"{base_url}/hr/course/assign/edit/999999",
        json={"status": "pending"},
        headers=auth_hr,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


def test_delete_assignment_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)
    assert list_resp.status_code == 200
    assignments = assert_json(list_resp)

    if not assignments:
        pytest.skip("No assignments available to test DELETE")

    assign_id = assignments[0]["id"]
    response = httpx.delete(
        f"{base_url}/hr/course/assign/edit/{assign_id}", headers=auth_hr
    )

    assert response.status_code == 200
    data = assert_json(response)
    assert data.get("message") == "Assignment removed"


def test_delete_assignment_not_found(base_url, auth_hr):
    response = httpx.delete(f"{base_url}/hr/course/assign/edit/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Assignment not found"


# 6) /employee/courses (CourseAssignmentEmployeeResource)


def test_get_employee_course_assignments_success(base_url, auth_employee):
    response = httpx.get(f"{base_url}/employee/courses", headers=auth_employee)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_employee_course_assignments_unauthorized(base_url):
    response = httpx.get(f"{base_url}/employee/courses")
    assert response.status_code in [401, 403]


# 7) /employee/course/{course_id} (EmployeeCourseUpdateByCourseIdResource)


def test_put_employee_course_status_success(base_url, auth_employee):
    payload = {"status": "completed"}

    response = httpx.put(
        f"{base_url}/employee/course/1",
        json=payload,
        headers=auth_employee,
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Course status updated"


def test_put_employee_course_status_missing_field(base_url, auth_employee, auth_hr):
    employee_courses_resp = httpx.get(
        f"{base_url}/employee/courses", headers=auth_employee
    )
    assert employee_courses_resp.status_code == 200
    employee_courses = assert_json(employee_courses_resp)

    response = {}
    if not employee_courses:
        course_payload = {
            "course_name": "Missing Field Test Course",
            "course_link": "https://example.com/missing-field-test",
            "topics": "Testing",
        }
        course_resp = httpx.post(
            f"{base_url}/hr/course", json=course_payload, headers=auth_hr
        )
        assert course_resp.status_code in [200, 201]
        course_data = assert_json(course_resp)
        course_id = course_data.get("id")
        print("no assigned course", course_id)
        assign_payload = {"course_id": course_id}
        httpx.post(
            f"{base_url}/hr/course/assign/4", json=assign_payload, headers=auth_hr
        )

        response = httpx.put(
            f"{base_url}/employee/course/{course_id}",
            json={},
            headers=auth_employee,
        )
    else:
        course_id = employee_courses[0].get("course_id")
        print("there are assigned course", course_id)
        response = httpx.put(
            f"{base_url}/employee/course/{course_id}",
            json={},
            headers=auth_employee,
        )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "status field is required"


def test_put_assignment_invalid_status(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/course/assign/4", headers=auth_hr)
    assert list_resp.status_code == 200
    assignments = assert_json(list_resp)

    if not assignments:
        pytest.skip("No assignments exist to test invalid status update")

    assign_id = assignments[0]["id"]
    payload = {"status": "INVALID"}

    response = httpx.put(
        f"{base_url}/hr/course/assign/edit/{assign_id}",
        json=payload,
        headers=auth_hr,
    )

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_employee_course_status_not_found(base_url, auth_employee):
    payload = {"status": "pending"}

    response = httpx.put(
        f"{base_url}/employee/course/999999",
        json=payload,
        headers=auth_employee,
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Course assignment not found"


# 8) /employee/recommendations (CourseRecommendationResource)


def test_get_recommendations_success(base_url, auth_employee):
    response = httpx.get(f"{base_url}/employee/recommendations", headers=auth_employee)

    assert response.status_code == 200
    data = assert_json(response)

    assert "assigned_courses" in data
    assert "recommended_courses" in data
    assert isinstance(data["recommended_courses"], list)


def test_get_recommendations_unauthorized(base_url):
    response = httpx.get(f"{base_url}/employee/recommendations")
    assert response.status_code in [401, 403]
