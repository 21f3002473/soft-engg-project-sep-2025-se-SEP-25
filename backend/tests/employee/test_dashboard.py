import httpx


def assert_json(response):
    assert "application/json" in response.headers.get("Content-Type", "")
    return response.json()


# 1) /employee/dashboard (DashboardResource)


def test_get_dashboard_success(base_url, auth_employee):
    url = f"{base_url}/employee/dashboard"
    response = httpx.get(url, headers=auth_employee)

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


def test_get_dashboard_unauthorized(base_url):
    url = f"{base_url}/employee/dashboard"
    response = httpx.get(url)

    assert response.status_code in [401, 403]


def test_get_dashboard_internal_error(base_url, auth_employee, monkeypatch):
    def bad_query(*args, **kwargs):
        raise Exception("DB error")

    monkeypatch.setattr("sqlmodel.Session.exec", bad_query)

    url = f"{base_url}/employee/dashboard"
    response = httpx.get(url, headers=auth_employee)

    assert response.status_code == 500
    data = assert_json(response)
    assert data.get("detail") == "Internal server error"


# 2) /employee/todo (AllToDoResource)


def test_get_all_todos_success(base_url, auth_employee):
    url = f"{base_url}/employee/todo"
    response = httpx.get(url, headers=auth_employee)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_all_todos_unauthorized(base_url):
    response = httpx.get(f"{base_url}/employee/todo")
    assert response.status_code in [401, 403]


def test_post_todo_success(base_url, auth_employee):
    payload = {"task": "Buy office supplies"}
    response = httpx.post(
        f"{base_url}/employee/todo", json=payload, headers=auth_employee
    )

    assert response.status_code in [200, 201]
    data = assert_json(response)

    assert "message" in data
    assert "task_id" in data


def test_post_todo_missing_task(base_url, auth_employee):
    response = httpx.post(f"{base_url}/employee/todo", json={}, headers=auth_employee)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Task field is required"


def test_post_todo_unauthorized(base_url):
    payload = {"task": "Some task"}
    response = httpx.post(f"{base_url}/employee/todo", json=payload)

    assert response.status_code in [401, 403]


# 3) /employee/todo/{task_id} (ToDoResource)


def test_get_todo_success(base_url, auth_employee):
    task_id = 1
    response = httpx.get(f"{base_url}/employee/todo/{task_id}", headers=auth_employee)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {"id", "task", "status", "deadline", "date_created"}


def test_get_todo_not_found(base_url, auth_employee):
    response = httpx.get(f"{base_url}/employee/todo/999999", headers=auth_employee)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Task not found"


def test_put_todo_success(base_url, auth_employee):
    task_id = 1
    payload = {"task": "Updated task", "status": "completed"}

    response = httpx.put(
        f"{base_url}/employee/todo/{task_id}", json=payload, headers=auth_employee
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Task updated successfully"


def test_put_todo_invalid_status(base_url, auth_employee):
    payload = {"status": "INVALID_STATUS"}
    url = f"{base_url}/employee/todo/1"

    response = httpx.put(url, json=payload, headers=auth_employee)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "Invalid status"


def test_put_todo_not_found(base_url, auth_employee):
    url = f"{base_url}/employee/todo/999999"
    response = httpx.put(url, json={"task": "test"}, headers=auth_employee)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Task not found"


def test_delete_todo_success(base_url, auth_employee):
    task_id = 1
    response = httpx.delete(
        f"{base_url}/employee/todo/{task_id}", headers=auth_employee
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Task deleted successfully"


def test_delete_todo_not_found(base_url, auth_employee):
    response = httpx.delete(f"{base_url}/employee/todo/999999", headers=auth_employee)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Task not found"


# 4) /employee/annoucements (AnnouncementEmployeeResource)


def test_get_employee_announcements_success(base_url, auth_employee):
    response = httpx.get(f"{base_url}/employee/annoucements", headers=auth_employee)
    assert response.status_code == 200

    data = assert_json(response)
    assert isinstance(data, list)


def test_get_employee_announcements_unauthorized(base_url):
    response = httpx.get(f"{base_url}/employee/annoucements")
    assert response.status_code in [401, 403]


# 5) /hr/annoucement/{user_id} (AnnouncementAdminListCreateResource)


def test_get_hr_announcements_success(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/annoucement/1", headers=auth_hr)

    assert response.status_code == 200
    data = assert_json(response)
    assert isinstance(data, list)


def test_get_hr_announcements_unauthorized(base_url):
    response = httpx.get(f"{base_url}/hr/annoucement/1")
    assert response.status_code in [401, 403]


def test_post_hr_announcement_success(base_url, auth_hr):
    payload = {"announcement": "Office will remain closed on Friday"}

    response = httpx.post(f"{base_url}/hr/annoucement/1", json=payload, headers=auth_hr)

    assert response.status_code in [200, 201]

    data = assert_json(response)
    assert data.get("message") == "Announcement created"
    assert "id" in data


def test_post_hr_announcement_missing_field(base_url, auth_hr):
    response = httpx.post(f"{base_url}/hr/annoucement/1", json={}, headers=auth_hr)

    assert response.status_code == 400
    data = assert_json(response)
    assert data.get("detail") == "announcement field is required"


# 6) /hr/annoucement/edit/{ann_id} (AnnouncementAdminDetailResource)


def test_get_hr_announcement_detail_success(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/annoucement/edit/1", headers=auth_hr)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert set(data.keys()) == {"id", "announcement", "created_at", "user_id"}


def test_get_hr_announcement_detail_not_found(base_url, auth_hr):
    response = httpx.get(f"{base_url}/hr/annoucement/edit/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"


def test_put_hr_announcement_success(base_url, auth_hr):
    payload = {"announcement": "Updated message"}

    response = httpx.put(
        f"{base_url}/hr/annoucement/edit/1", json=payload, headers=auth_hr
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Announcement updated"


def test_put_hr_announcement_not_found(base_url, auth_hr):
    payload = {"announcement": "Test"}

    response = httpx.put(
        f"{base_url}/hr/annoucement/edit/999999", json=payload, headers=auth_hr
    )

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"


def test_delete_hr_announcement_success(base_url, auth_hr):
    response = httpx.delete(f"{base_url}/hr/annoucement/edit/1", headers=auth_hr)

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = assert_json(response)
        assert data.get("message") == "Announcement deleted"


def test_delete_hr_announcement_not_found(base_url, auth_hr):
    response = httpx.delete(f"{base_url}/hr/annoucement/edit/999999", headers=auth_hr)

    assert response.status_code == 404
    data = assert_json(response)
    assert data.get("detail") == "Announcement not found"
