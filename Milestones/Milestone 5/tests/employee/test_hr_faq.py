import httpx
import pytest


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# HR FAQ CREATE  (POST /hr/faq)
def test_hr_faq_create_success(base_url, auth_hr):
    payload = {
        "question": "What is the leave policy?",
        "answer": "Employees get 20 days of leave.",
    }

    r = httpx.post(f"{base_url}/hr/faq", json=payload, headers=auth_hr)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "FAQ created successfully"
    assert "id" in data


def test_hr_faq_create_missing_field(base_url, auth_hr):
    payload = {"question": "Missing answer"}

    r = httpx.post(f"{base_url}/hr/faq", json=payload, headers=auth_hr)

    assert r.status_code == 422


def test_hr_faq_create_unauthorized(base_url):
    payload = {"question": "Test?", "answer": "Test!"}

    r = httpx.post(f"{base_url}/hr/faq", json=payload)

    assert r.status_code in [401, 403]


# FAQ DETAIL GET (GET /hr/faq/{id}) — Employee allowed
def test_faq_detail_get_success(base_url, auth_employee):
    list_resp = httpx.get(f"{base_url}/employee/hr-faqs", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    faqs = data.get("faqs", [])

    if not faqs:
        pytest.skip("No FAQs available to test GET detail")

    faq_id = faqs[0]["id"]
    r = httpx.get(f"{base_url}/hr/faq/{faq_id}", headers=auth_employee)

    assert r.status_code == 200
    response_data = assert_json(r)
    assert "faq" in response_data
    assert {"id", "question", "answer"}.issubset(response_data["faq"].keys())


def test_faq_detail_not_found(base_url, auth_employee):
    r = httpx.get(f"{base_url}/hr/faq/999999", headers=auth_employee)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_detail_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/faq/1")
    assert r.status_code in [401, 403]


# UPDATE FAQ (PUT /hr/faq/{id})
def test_faq_update_success(base_url, auth_employee, auth_hr):
    list_resp = httpx.get(f"{base_url}/employee/hr-faqs", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    faqs = data.get("faqs", [])

    if not faqs:
        pytest.skip("No FAQs available to test PUT")

    faq_id = faqs[0]["id"]
    payload = {"question": "Updated Q?", "answer": "Updated A."}

    r = httpx.put(f"{base_url}/hr/faq/{faq_id}", json=payload, headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "FAQ updated successfully"


def test_faq_update_not_found(base_url, auth_hr):
    payload = {"question": "Anything?", "answer": "Anything!"}

    r = httpx.put(f"{base_url}/hr/faq/999999", json=payload, headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_update_unauthorized(base_url):
    payload = {"question": "No auth", "answer": "No auth answer"}

    r = httpx.put(f"{base_url}/hr/faq/1", json=payload)
    assert r.status_code in [401, 403]


# DELETE FAQ (DELETE /hr/faq/{id})
def test_faq_delete_success(base_url, auth_employee, auth_hr):
    list_resp = httpx.get(f"{base_url}/employee/hr-faqs", headers=auth_employee)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    faqs = data.get("faqs", [])

    if not faqs:
        pytest.skip("No FAQs available to test DELETE")

    faq_id = faqs[0]["id"]
    r = httpx.delete(f"{base_url}/hr/faq/{faq_id}", headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "FAQ deleted successfully"


def test_faq_delete_not_found(base_url, auth_hr):
    r = httpx.delete(f"{base_url}/hr/faq/999999", headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "FAQ not found"


def test_faq_delete_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/hr/faq/1")
    assert r.status_code in [401, 403]


# LIST ALL FAQS (GET /employee/hr-faqs)
def test_employee_list_faqs_success(base_url, auth_employee):
    r = httpx.get(f"{base_url}/employee/hr-faqs", headers=auth_employee)

    assert r.status_code == 200
    data = assert_json(r)
    assert "faqs" in data
    assert isinstance(data["faqs"], list)


def test_employee_list_faqs_unauthorized(base_url):
    r = httpx.get(f"{base_url}/employee/hr-faqs")
    assert r.status_code in [401, 403]
