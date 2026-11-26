from database import get_connection, init_db

PRODUCTS = [
    ("Wireless Mouse", "Electronics", 19.99, 50),
    ("Mechanical Keyboard", "Electronics", 79.99, 30),
    ("USB-C Cable", "Electronics", 9.99, 100),
    ("Running Shoes", "Footwear", 59.99, 25),
    ("Leather Sandals", "Footwear", 34.99, 15),
    ("Cotton T-Shirt", "Clothing", 14.99, 80),
    ("Denim Jacket", "Clothing", 69.99, 10),
    ("Water Bottle", "Accessories", 12.99, 60),
    ("Backpack", "Accessories", 44.99, 20),
    ("Out Of Stock Item", "Accessories", 24.99, 0),  # for negative tests
]

USERS = [
    ("test@example.com", "Password123", "Test User"),
    ("second@example.com", "Password123", "Second User"),
]


def seed():
    init_db()
    conn = get_connection()
    conn.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        PRODUCTS,
    )
    conn.executemany(
        "INSERT INTO users (email, password, name) VALUES (?, ?, ?)", USERS
    )
    conn.commit()
    conn.close()
    print("Database seeded.")


if __name__ == "__main__":
    seed()