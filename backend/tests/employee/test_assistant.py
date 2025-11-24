import httpx


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


#  SUCCESS — 200 OK


def test_assistant_success(base_url, auth_employee):
    payload = {"message": "Hello assistant"}

    r = httpx.post(
        f"{base_url}/employee/assistant", json=payload, headers=auth_employee
    )

    assert r.status_code == 200
    data = assert_json(r)

    assert "reply" in data
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0


#  422 — Missing Required Field


def test_assistant_missing_message_field(base_url, auth_employee):
    r = httpx.post(f"{base_url}/employee/assistant", json={}, headers=auth_employee)

    assert r.status_code == 422


# 401 / 403 Unauthorized


def test_assistant_unauthorized(base_url):
    payload = {"message": "Is WFH allowed?"}

    r = httpx.post(f"{base_url}/employee/assistant", json=payload)

    assert r.status_code in (401, 403)
