ALLOWED_TABLES = {"users", "products", "cart_items", "orders"}


class DbHelper:
    """Read-only SQL shortcuts for checking what the app saved."""

    def __init__(self, conn):
        self.conn = conn

    def scalar(self, sql: str, params=()):
        """Run a query and return the first column of the first row."""
        return self.conn.execute(sql, params).fetchone()[0]

    def count_rows(self, table: str) -> int:
        # SQL cannot take a table name as a ? parameter, so we whitelist instead
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Unknown table: {table}")
        return self.scalar(f"SELECT COUNT(*) FROM {table}")

    def get_user_id(self, email: str) -> int:
        return self.scalar("SELECT id FROM users WHERE email = ?", (email,))

    def get_stock(self, product_id: int) -> int:
        return self.scalar("SELECT stock FROM products WHERE id = ?", (product_id,))

    def get_order(self, order_id: int):
        return self.conn.execute(
            "SELECT id, user_id, total, status, created_at FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()

    def count_orders_for(self, user_id: int) -> int:
        return self.scalar("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))

    def cart_items_for(self, user_id: int):
        """Cart rows joined with product names (a JOIN across two tables)."""
        return self.conn.execute(
            """SELECT c.product_id, p.name, c.quantity
               FROM cart_items c JOIN products p ON p.id = c.product_id
               WHERE c.user_id = ?
               ORDER BY c.product_id""",
            (user_id,),
        ).fetchall()