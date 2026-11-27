import pytest
from jsonschema import validate

from utils.schemas import CART_SCHEMA

pytestmark = pytest.mark.api

MOUSE = 1
OUT_OF_STOCK = 10
DENIM_JACKET = 7  # stock = 10


def test_new_user_cart_is_empty(auth_api):
    response = auth_api.get("/api/cart")
    assert response.status_code == 200
    validate(response.json(), CART_SCHEMA)
    assert response.json() == {"items": [], "total": 0}


@pytest.mark.smoke
def test_add_item_to_cart(auth_api):
    response = auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    assert response.status_code == 200
    cart = response.json()
    validate(cart, CART_SCHEMA)
    assert cart["items"][0]["quantity"] == 2
    assert cart["total"] == pytest.approx(39.98)


def test_adding_same_product_twice_adds_quantities(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    cart = auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2}).json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 3


@pytest.mark.parametrize("quantity", [0, -1], ids=["zero", "negative"])
def test_invalid_quantity_returns_400(auth_api, quantity):
    response = auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": quantity})
    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity must be at least 1"


def test_add_unknown_product_returns_404(auth_api):
    response = auth_api.post("/api/cart", json={"product_id": 999, "quantity": 1})
    assert response.status_code == 404


def test_add_out_of_stock_product_returns_400(auth_api):
    response = auth_api.post("/api/cart", json={"product_id": OUT_OF_STOCK, "quantity": 1})
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough stock"


def test_add_more_than_stock_returns_400(auth_api):
    response = auth_api.post("/api/cart", json={"product_id": DENIM_JACKET, "quantity": 11})
    assert response.status_code == 400


def test_update_quantity(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    response = auth_api.put(f"/api/cart/{MOUSE}", json={"quantity": 5})
    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 5
    assert response.json()["total"] == pytest.approx(99.95)


def test_update_quantity_to_zero_returns_400(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    response = auth_api.put(f"/api/cart/{MOUSE}", json={"quantity": 0})
    assert response.status_code == 400


def test_update_item_not_in_cart_returns_404(auth_api):
    response = auth_api.put(f"/api/cart/{MOUSE}", json={"quantity": 2})
    assert response.status_code == 404


def test_remove_item(auth_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    response = auth_api.delete(f"/api/cart/{MOUSE}")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_remove_item_not_in_cart_returns_404(auth_api):
    response = auth_api.delete(f"/api/cart/{MOUSE}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not in cart"


def test_carts_are_separate_per_user(auth_api, second_api):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    assert second_api.get("/api/cart").json()["items"] == []