import httpx


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


#   GET /employee/account


def test_account_get_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/account", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)

    # Basic fields expected in AccountOut
    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "role" in data


def test_account_get_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/account")
    assert r.status_code in (401, 403)


#   PUT /employee/account


def test_account_update_success(base_url, auth_employee):
    payload = {"name": "New Automated Test Name"}

    r = httpx.put(
        f"{base_url}/employee/account",
        json=payload,
        headers=auth_employee,
    )

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Account updated successfully"


def test_account_update_validation_error(base_url, auth_employee):
    payload = {"email": 12345}

    r = httpx.put(
        f"{base_url}/employee/account",
        json=payload,
        headers=auth_employee,
    )

    assert r.status_code == 422


def test_account_update_unauthorized(base_url):
    payload = {"name": "Not allowed"}
    r = httpx.put(f"{base_url}/employee/account", json=payload)
    assert r.status_code in (401, 403)



#   DELETE /employee/account


def test_account_logout_success(base_url, auth_employee):
    r = httpx.delete(f"{base_url}/employee/account", headers=auth_employee)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Logged out successfully"


def test_account_logout_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/employee/account")
    assert r.status_code in (401, 403)
