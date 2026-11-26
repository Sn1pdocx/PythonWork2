import sqlite3
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash

DB_NAME = Path(__file__).parent / "guitar_shop.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            type TEXT NOT NULL,
            strings INTEGER NOT NULL CHECK(strings > 0),
            color TEXT NOT NULL,
            price INTEGER NOT NULL CHECK(price >= 0),
            stock INTEGER NOT NULL CHECK(stock >= 0)
        )
    """)

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if user is None:
        password = getpass("Create admin password: ")

        while not password.strip():
            password = getpass("Password cannot be empty: ")

        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash(password))
        )

        guitars = [
            ("Ibanez", "RG550", "Electric", 6, "Yellow", 45000, 3),
            ("Fender", "Stratocaster", "Electric", 6, "Sunburst", 38000, 2),
            ("Gibson", "Les Paul", "Electric", 6, "Cherry", 65000, 1),
            ("Yamaha", "FG800", "Acoustic", 6, "Natural", 13500, 5),
            ("Schecter", "Omen-8", "Electric", 8, "Black", 32000, 1)
        ]

        conn.executemany("""
            INSERT INTO items
            (brand, model, type, strings, color, price, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, guitars)

        print("Admin account created.")
        print("Guitar catalog created.")

    conn.commit()
    conn.close()

    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
