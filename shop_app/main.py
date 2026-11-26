
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from database import get_connection

app = FastAPI(title="Test Shop API")


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/login")
def login(body: LoginRequest):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, email, name FROM users WHERE email = ? AND password = ?",
        (body.email, body.password),
    ).fetchone()
    conn.close()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": f"token-{user['id']}", "user": dict(user)}


@app.get("/api/products")
def list_products(search: str | None = None, category: str | None = None):
    query = "SELECT id, name, category, price, stock FROM products WHERE 1=1"
    params = []
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    if category:
        query += " AND category = ?"
        params.append(category)
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, category, price, stock FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)
# ---------- Auth helper ----------
def current_user_id(authorization: str | None = Header(default=None)) -> int:
    """Reads 'Authorization: Bearer token-<id>' and returns the user id."""
    if not authorization or not authorization.startswith("Bearer token-"):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        user_id = int(authorization.removeprefix("Bearer token-"))
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    conn = get_connection()
    user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user is None:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return user_id


# ---------- Cart ----------
class CartItemRequest(BaseModel):
    product_id: int
    quantity: int


def read_cart(conn, user_id: int):
    rows = conn.execute(
        """SELECT p.id AS product_id, p.name, p.price, c.quantity,
                  ROUND(p.price * c.quantity, 2) AS line_total
           FROM cart_items c JOIN products p ON p.id = c.product_id
           WHERE c.user_id = ?""",
        (user_id,),
    ).fetchall()
    items = [dict(r) for r in rows]
    total = round(sum(i["line_total"] for i in items), 2)
    return {"items": items, "total": total}


@app.post("/api/cart")
def add_to_cart(body: CartItemRequest, user_id: int = Depends(current_user_id)):
    if body.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    conn = get_connection()
    product = conn.execute(
        "SELECT id, stock FROM products WHERE id = ?", (body.product_id,)
    ).fetchone()
    if product is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    existing = conn.execute(
        "SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, body.product_id),
    ).fetchone()
    new_qty = body.quantity + (existing["quantity"] if existing else 0)
    if new_qty > product["stock"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough stock")
    if existing:
        conn.execute("UPDATE cart_items SET quantity = ? WHERE id = ?", (new_qty, existing["id"]))
    else:
        conn.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, body.product_id, body.quantity),
        )
    conn.commit()
    cart = read_cart(conn, user_id)
    conn.close()
    return cart


@app.get("/api/cart")
def get_cart(user_id: int = Depends(current_user_id)):
    conn = get_connection()
    cart = read_cart(conn, user_id)
    conn.close()
    return cart


@app.delete("/api/cart/{product_id}")
def remove_from_cart(product_id: int, user_id: int = Depends(current_user_id)):
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM cart_items WHERE user_id = ? AND product_id = ?",
        (user_id, product_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not in cart")
    cart = read_cart(conn, user_id)
    conn.close()
    return cart


# ---------- Orders ----------
@app.post("/api/orders", status_code=201)
def create_order(user_id: int = Depends(current_user_id)):
    conn = get_connection()
    cart = read_cart(conn, user_id)
    if not cart["items"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Cart is empty")
    cur = conn.execute(
        "INSERT INTO orders (user_id, total, status) VALUES (?, ?, 'confirmed')",
        (user_id, cart["total"]),
    )
    order_id = cur.lastrowid
    for item in cart["items"]:
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )
    conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"order_id": order_id, "total": cart["total"], "status": "confirmed"}


@app.get("/api/orders")
def list_orders(user_id: int = Depends(current_user_id)):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, total, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]