import pytest
from jsonschema import validate

from utils.schemas import ERROR_SCHEMA, LOGIN_SCHEMA

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_login_success(api):
    response = api.login("test@example.com", "Password123")
    assert response.status_code == 200
    body = response.json()
    validate(body, LOGIN_SCHEMA)
    assert body["user"]["email"] == "test@example.com"
    assert body["token"].startswith("token-")


def test_login_wrong_password(api):
    response = api.login("test@example.com", "WrongPass")
    assert response.status_code == 401
    validate(response.json(), ERROR_SCHEMA)
    assert response.json()["detail"] == "Invalid email or password"


def test_login_unknown_email(api):
    response = api.login("nobody@example.com", "Password123")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "body",
    [{"email": "test@example.com"}, {"password": "Password123"}, {}],
    ids=["missing-password", "missing-email", "empty-body"],
)
def test_login_missing_fields_returns_422(api, body):
    response = api.request("POST", "/api/login", json=body)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "method, path",
    [("GET", "/api/cart"), ("POST", "/api/orders"), ("GET", "/api/orders")],
    ids=["get-cart", "post-orders", "get-orders"],
)
def test_protected_endpoints_require_token(api, method, path):
    response = api.request(method, path)
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid token"


@pytest.mark.parametrize(
    "header_value",
    ["Bearer token-999", "Bearer abc", "Token token-1", "Bearer token-"],
    ids=["unknown-user", "garbage", "wrong-scheme", "empty-id"],
)
def test_invalid_tokens_are_rejected(api, header_value):
    response = api.get("/api/cart", headers={"Authorization": header_value})
    assert response.status_code == 401