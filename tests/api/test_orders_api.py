import pytest
from jsonschema import validate

from utils.schemas import CART_SCHEMA, ORDER_CREATED_SCHEMA, ORDER_SCHEMA

pytestmark = pytest.mark.api

MOUSE = 1


@pytest.mark.smoke
def test_create_order_returns_201(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    response = auth_api.post("/api/orders")
    assert response.status_code == 201
    body = response.json()
    validate(body, ORDER_CREATED_SCHEMA)
    assert body["total"] == pytest.approx(39.98)


def test_create_order_with_empty_cart_returns_400(auth_api):
    response = auth_api.post("/api/orders")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_order_empties_the_cart(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.post("/api/orders")
    cart = auth_api.get("/api/cart").json()
    validate(cart, CART_SCHEMA)
    assert cart["items"] == []


def test_order_reduces_product_stock(auth_api, api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    auth_api.post("/api/orders")
    assert api.get(f"/api/products/{MOUSE}").json()["stock"] == 48  # seed stock is 50


def test_order_appears_in_order_list(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    order_id = auth_api.post("/api/orders").json()["order_id"]
    orders = auth_api.get("/api/orders").json()
    assert len(orders) == 1
    validate(orders[0], ORDER_SCHEMA)
    assert orders[0]["id"] == order_id
    assert orders[0]["status"] == "confirmed"


def test_orders_are_separate_per_user(auth_api, second_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.post("/api/orders")
    assert second_api.get("/api/orders").json() == []