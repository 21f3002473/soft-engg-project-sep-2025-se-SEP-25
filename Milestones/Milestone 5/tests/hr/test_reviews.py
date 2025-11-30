import httpx
import pytest


def assert_json(resp):
    assert "application/json" in resp.headers.get("content-type", "").lower()
    return resp.json()


# CREATE REVIEW (POST /api/hr/review/create)
def test_review_create_success(base_url, auth_hr):
    payload = {"user_id": 1, "rating": 4, "comments": "Good performance overall."}

    r = httpx.post(f"{base_url}/hr/review/create", json=payload, headers=auth_hr)

    assert r.status_code in [200, 201]
    data = assert_json(r)
    assert data["message"] == "Review created"
    assert "id" in data["review"]


def test_review_create_sever_error(base_url, auth_hr):
    payload = {"user_id": 1}

    r = httpx.post(f"{base_url}/hr/review/create", json=payload, headers=auth_hr)

    assert r.status_code == 500


def test_review_create_unauthorized(base_url):
    payload = {"user_id": 1, "rating": 5, "comments": "Unauthorized"}

    r = httpx.post(f"{base_url}/hr/review/create", json=payload)

    assert r.status_code in [401, 403]


# GET REVIEW DETAIL (GET /api/hr/review/{id})
def test_review_detail_success(base_url, auth_hr):
    payload = {"user_id": 2, "rating": 4, "comments": "Good performance overall."}

    response_create = httpx.post(
        f"{base_url}/hr/review/create", json=payload, headers=auth_hr
    )
    list_resp = httpx.get(f"{base_url}/hr/reviews", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reviews = data.get("reviews", [])

    if not reviews:
        pytest.skip("No reviews available to test GET detail")

    rev_id = response_create.json()["review"]["id"]

    r = httpx.get(f"{base_url}/hr/reviews/{rev_id}", headers=auth_hr)

    assert r.status_code == 200
    response = assert_json(r)
    assert "reviews" in response


def test_review_detail_method_not_allowed(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/review/0", headers=auth_hr)

    assert r.status_code == 405
    assert assert_json(r)["detail"] == "Method Not Allowed"


def test_review_detail_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/reviews/1")
    assert r.status_code in [401, 403]


# UPDATE REVIEW (PUT /api/hr/review/{id})
def test_review_update_success(base_url, auth_hr):
    list_resp = httpx.get(f"{base_url}/hr/reviews", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reviews = data.get("reviews", [])

    if not reviews:
        pytest.skip("No reviews available to test UPDATE")

    rev_id = reviews[0]["id"]

    payload = {"rating": 3, "comments": "Updated review"}

    r = httpx.put(f"{base_url}/hr/review/{rev_id}", json=payload, headers=auth_hr)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Review updated"


def test_review_update_not_found(base_url, auth_hr):
    payload = {"rating": 1, "comments": "Test"}

    r = httpx.put(f"{base_url}/hr/review/999999", json=payload, headers=auth_hr)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Review not found"


def test_review_update_unauthorized(base_url):
    payload = {"rating": 5, "comments": "No auth"}

    r = httpx.put(f"{base_url}/hr/review/1", json=payload)

    assert r.status_code in [401, 403]


# DELETE REVIEW (DELETE /api/hr/review/{id})
def test_review_delete_success(base_url, auth_hr, auth_admin):
    list_resp = httpx.get(f"{base_url}/hr/reviews", headers=auth_hr)
    assert list_resp.status_code == 200
    data = assert_json(list_resp)
    reviews = data.get("reviews", [])

    if not reviews:
        pytest.skip("No reviews available for DELETE")

    rev_id = reviews[0]["id"]

    r = httpx.delete(f"{base_url}/hr/review/{rev_id}", headers=auth_admin)

    assert r.status_code == 200
    assert assert_json(r)["message"] == "Review deleted"


def test_review_delete_not_found(base_url, auth_admin):
    r = httpx.delete(f"{base_url}/hr/review/999999", headers=auth_admin)

    assert r.status_code == 404
    assert assert_json(r)["detail"] == "Review not found"


def test_review_delete_unauthorized(base_url):
    r = httpx.delete(f"{base_url}/hr/review/1")
    assert r.status_code in [401, 403]


# LIST ALL REVIEWS (GET /api/hr/reviews)
def test_review_list_success(base_url, auth_hr):
    r = httpx.get(f"{base_url}/hr/reviews", headers=auth_hr)

    assert r.status_code == 200
    data = assert_json(r)
    assert "reviews" in data
    assert isinstance(data["reviews"], list)


def test_review_list_unauthorized(base_url):
    r = httpx.get(f"{base_url}/hr/reviews")
    assert r.status_code in [401, 403]
