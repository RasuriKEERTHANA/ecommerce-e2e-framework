import re

import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage

pytestmark = pytest.mark.hybrid

MOUSE = 1


@pytest.mark.smoke
def test_order_placed_in_ui_is_saved_in_api_and_database(logged_in_page: Page, auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")
    stock_before = db_helper.get_stock(MOUSE)
    assert db_helper.count_rows("orders") == 0

    # --- Layer 1: UI. Buy 2 wireless mice like a real user ---
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")

    cart = CartPage(logged_in_page).open()
    cart.increase(MOUSE)
    expect(cart.quantity_of(MOUSE)).to_have_text("2")
    expect(cart.total).to_have_text("39.98")
    cart.checkout_button.click()
    logged_in_page.wait_for_url("**/checkout")

    checkout = CheckoutPage(logged_in_page)
    checkout.fill_details("Test User", "12 Main St", "4111111111111111")
    checkout.place_order()
    expect(checkout.success).to_contain_text("placed successfully")

    message = checkout.success.inner_text()
    match = re.search(r"Order #(\d+) .* Total: \$([\d.]+)", message)
    assert match, f"Unexpected success message: {message}"
    ui_order_id = int(match.group(1))
    ui_total = float(match.group(2))

    # --- Layer 2: API. Does the backend report the same order? ---
    orders = auth_api.get("/api/orders").json()
    assert [o["id"] for o in orders] == [ui_order_id]
    assert orders[0]["total"] == pytest.approx(ui_total)
    assert auth_api.get("/api/cart").json()["items"] == []

    # --- Layer 3: SQL. Was it really saved? ---
    row = db_helper.get_order(ui_order_id)
    assert row is not None
    assert row["user_id"] == user_id
    assert row["total"] == pytest.approx(ui_total)
    assert row["status"] == "confirmed"
    assert db_helper.get_stock(MOUSE) == stock_before - 2
    assert db_helper.cart_items_for(user_id) == []


def test_cart_item_added_in_ui_is_stored(logged_in_page: Page, auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")

    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_have_text("Added Wireless Mouse to cart")

    api_items = auth_api.get("/api/cart").json()["items"]
    assert len(api_items) == 1
    assert api_items[0]["product_id"] == MOUSE
    assert api_items[0]["quantity"] == 1

    rows = db_helper.cart_items_for(user_id)
    assert len(rows) == 1
    assert rows[0]["quantity"] == 1


def test_cart_prepared_through_api_is_shown_in_ui(logged_in_page: Page, auth_api):
    # Fast setup through the API, then verify what the user sees
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 3})

    cart = CartPage(logged_in_page).open()
    expect(cart.items).to_have_count(1)
    expect(cart.quantity_of(MOUSE)).to_have_text("3")
    expect(cart.total).to_have_text("59.97")