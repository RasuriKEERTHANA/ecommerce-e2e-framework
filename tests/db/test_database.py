import sqlite3

import pytest

pytestmark = pytest.mark.db

MOUSE = 1
OUT_OF_STOCK = 10


def test_seed_row_counts(db_helper):
    assert db_helper.count_rows("users") == 2
    assert db_helper.count_rows("products") == 10
    assert db_helper.count_rows("cart_items") == 0
    assert db_helper.count_rows("orders") == 0


def test_out_of_stock_product_has_zero_stock(db_helper):
    assert db_helper.get_stock(OUT_OF_STOCK) == 0


def test_duplicate_email_is_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
            ("test@example.com", "x", "Duplicate"),
        )
    db.rollback()


def test_order_creates_row_with_correct_values(auth_api, db_helper):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    order_id = auth_api.post("/api/orders").json()["order_id"]

    row = db_helper.get_order(order_id)
    assert row is not None
    assert row["user_id"] == db_helper.get_user_id("test@example.com")
    assert row["total"] == pytest.approx(39.98)
    assert row["status"] == "confirmed"
    assert row["created_at"] is not None


def test_order_reduces_stock(auth_api, db_helper):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    auth_api.post("/api/orders")
    assert db_helper.get_stock(MOUSE) == 48  # seed stock is 50


def test_order_clears_cart_rows(auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    assert len(db_helper.cart_items_for(user_id)) == 1  # row exists before the order
    auth_api.post("/api/orders")
    assert db_helper.cart_items_for(user_id) == []


def test_cart_row_matches_added_item(auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 2})
    rows = db_helper.cart_items_for(user_id)
    assert len(rows) == 1
    assert rows[0]["name"] == "Wireless Mouse"
    assert rows[0]["quantity"] == 2


def test_cart_update_is_saved(auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.put(f"/api/cart/{MOUSE}", json={"quantity": 5})
    assert db_helper.cart_items_for(user_id)[0]["quantity"] == 5


def test_removed_item_row_is_deleted(auth_api, db_helper):
    user_id = db_helper.get_user_id("test@example.com")
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.delete(f"/api/cart/{MOUSE}")
    assert db_helper.cart_items_for(user_id) == []


def test_rejected_add_leaves_cart_unchanged(auth_api, db_helper):
    response = auth_api.post("/api/cart", json={"product_id": OUT_OF_STOCK, "quantity": 1})
    assert response.status_code == 400
    assert db_helper.count_rows("cart_items") == 0


def test_failed_order_creates_no_row(auth_api, db_helper):
    response = auth_api.post("/api/orders")  # cart is empty
    assert response.status_code == 400
    assert db_helper.count_rows("orders") == 0


def test_orders_belong_to_the_right_user(auth_api, db_helper):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.post("/api/orders")
    first = db_helper.get_user_id("test@example.com")
    second = db_helper.get_user_id("second@example.com")
    assert db_helper.count_orders_for(first) == 1
    assert db_helper.count_orders_for(second) == 0


def test_no_orphan_orders(auth_api, db_helper):
    auth_api.post("/api/cart", json={"product_id": MOUSE, "quantity": 1})
    auth_api.post("/api/orders")
    orphans = db_helper.scalar(
        """SELECT COUNT(*) FROM orders o
           LEFT JOIN users u ON u.id = o.user_id
           WHERE u.id IS NULL"""
    )
    assert orphans == 0