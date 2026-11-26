from fastapi import FastAPI, HTTPException
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