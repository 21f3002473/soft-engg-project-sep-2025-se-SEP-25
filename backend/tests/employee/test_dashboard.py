from datetime import datetime, timedelta

import pytest
import requests

BASE_URL = "http://localhost:8000/api"


@pytest.fixture
def client():
    return requests


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# 1) /employee/dashboard  (DashboardResource)


def test_get_dashboard_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get(f"{BASE_URL}/employee/dashboard", headers=headers)
    assert response.status_code == 200

    data = assert_json(response)

    assert set(data.keys()) == {"message", "stats", "tasks", "announcements", "user"}
    assert "pending_tasks" in data["stats"]
    assert "completed_tasks" in data["stats"]
    assert "requests" in data["stats"]
    assert "courses_completed" in data["stats"]
    assert isinstance(data["tasks"], list)
    assert isinstance(data["announcements"], list)
    assert isinstance(data["user"], dict)


def test_get_dashboard_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/dashboard")
    assert response.status_code in [401, 403]


def test_get_dashboard_internal_error(client, monkeypatch):
    def bad_query(*args, **kwargs):
        raise Exception("DB error")

    monkeypatch.setattr("sqlmodel.Session.exec", bad_query)

    headers = {"Authorization": "Bearer faketoken"}

    response = client.get(f"{BASE_URL}/employee/dashboard", headers=headers)
    assert response.status_code == 500

    data = assert_json(response)
    assert data.get("detail") == "Internal server error"


# 2) /employee/todo  (AllToDoResource)


def test_get_all_todos_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get(f"{BASE_URL}/employee/todo", headers=headers)
    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, list)


def test_get_all_todos_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/todo")
    assert response.status_code in [401, 403]


def test_post_todo_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    payload = {"task": "Buy office supplies"}

    response = client.post(f"{BASE_URL}/employee/todo", json=payload, headers=headers)
    assert response.status_code in [200, 201]

    data = assert_json(response)

    assert "message" in data
    assert "task_id" in data


def test_post_todo_missing_task(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.post(f"{BASE_URL}/employee/todo", json={}, headers=headers)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Task field is required"


def test_post_todo_unauthorized(client):
    payload = {"task": "Some task"}
    response = client.post(f"{BASE_URL}/employee/todo", json=payload)

    assert response.status_code in [401, 403]


# 3) /employee/todo/{task_id}  (ToDoResource)


def test_get_todo_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    task_id = 1

    response = client.get(f"{BASE_URL}/employee/todo/{task_id}", headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {"id", "task", "status", "deadline", "date_created"}


def test_get_todo_not_found(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get(f"{BASE_URL}/employee/todo/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Task not found"


def test_put_todo_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    task_id = 1
    payload = {"task": "Updated task", "status": "completed"}

    response = client.put(
        f"{BASE_URL}/employee/todo/{task_id}", json=payload, headers=headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Task updated successfully"


def test_put_todo_invalid_status(client):
    headers = {"Authorization": "Bearer faketoken"}
    payload = {"status": "INVALID_STATUS"}

    response = client.put(f"{BASE_URL}/employee/todo/1", json=payload, headers=headers)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_todo_not_found(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.put(
        f"{BASE_URL}/employee/todo/999999", json={"task": "test"}, headers=headers
    )
    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Task not found"


def test_delete_todo_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    task_id = 1

    response = client.delete(f"{BASE_URL}/employee/todo/{task_id}", headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Task deleted successfully"


def test_delete_todo_not_found(client):
    headers = {"Authorization": "Bearer faketoken"}

    response = client.delete(f"{BASE_URL}/employee/todo/999999", headers=headers)
    assert response.status_code == 404

    data = assert_json(response)
    assert data.get("detail") == "Task not found"


# 4) /employee/annoucements  (AnnouncementEmployeeResource)


def test_get_employee_announcements_success(client):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get(f"{BASE_URL}/employee/annoucements", headers=headers)

    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, list)


def test_get_employee_announcements_unauthorized(client):
    response = client.get(f"{BASE_URL}/employee/annoucements")
    assert response.status_code in [401, 403]


# 5) /hr/annoucement/{user_id}  (AnnouncementAdminListCreateResource)


def test_get_hr_announcements_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/annoucement/1", headers=headers)

    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, list)


def test_get_hr_announcements_unauthorized(client):
    response = client.get(f"{BASE_URL}/hr/annoucement/1")
    assert response.status_code in [401, 403]


def test_post_hr_announcement_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"announcement": "Office will remain closed on Friday"}

    response = client.post(
        f"{BASE_URL}/hr/annoucement/1", json=payload, headers=headers
    )

    assert response.status_code in [200, 201]

    data = assert_json(response)
    assert data.get("message") == "Announcement created"
    assert "id" in data


def test_post_hr_announcement_missing_field(client):
    headers = {"Authorization": "Bearer hr_token"}

    response = client.post(f"{BASE_URL}/hr/annoucement/1", json={}, headers=headers)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "announcement field is required"


# 6) /hr/annoucement/edit/{ann_id}  (AnnouncementAdminDetailResource)


def test_get_hr_announcement_detail_success(client):
    headers = {"Authorization": "Bearer hr_token"}

    response = client.get(f"{BASE_URL}/hr/annoucement/edit/1", headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {"id", "announcement", "created_at", "user_id"}


def test_get_hr_announcement_detail_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    response = client.get(f"{BASE_URL}/hr/annoucement/edit/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"


def test_put_hr_announcement_success(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"announcement": "Updated message"}

    response = client.put(
        f"{BASE_URL}/hr/annoucement/edit/1", json=payload, headers=headers
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Announcement updated"


def test_put_hr_announcement_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}
    payload = {"announcement": "Test"}

    response = client.put(
        f"{BASE_URL}/hr/annoucement/edit/999999", json=payload, headers=headers
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"


def test_delete_hr_announcement_success(client):
    headers = {"Authorization": "Bearer hr_token"}

    response = client.delete(f"{BASE_URL}/hr/annoucement/edit/1", headers=headers)
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Announcement deleted"


def test_delete_hr_announcement_not_found(client):
    headers = {"Authorization": "Bearer hr_token"}

    response = client.delete(f"{BASE_URL}/hr/annoucement/edit/999999", headers=headers)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"
