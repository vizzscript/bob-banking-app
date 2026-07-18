"""
seed.py
-------
One-time script that creates the database tables and inserts a test customer.

Run from the BACKEND/ directory:

    python seed.py

Safe to run multiple times — it checks for existing data before inserting.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# Resolve the DB path relative to this file so it works from any cwd.
DB_PATH = os.path.join(os.path.dirname(__file__), "bank.db")

CREATE_CUSTOMERS = """
CREATE TABLE IF NOT EXISTS customers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    full_name     TEXT    NOT NULL
);
"""

CREATE_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    balance     REAL    NOT NULL DEFAULT 0.0
);
"""

CREATE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER  PRIMARY KEY AUTOINCREMENT,
    account_id       INTEGER  NOT NULL REFERENCES accounts(id),
    transaction_type TEXT     NOT NULL CHECK(transaction_type IN ('deposit','withdrawal')),
    amount           REAL     NOT NULL,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# Test credentials — change before any real deployment.
TEST_USERNAME = "john_doe"
TEST_PASSWORD = "password123"
TEST_FULL_NAME = "John Doe"
STARTING_BALANCE = 1000.00


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # ── Create tables ──────────────────────────────────────────────────────
    conn.execute(CREATE_CUSTOMERS)
    conn.execute(CREATE_ACCOUNTS)
    conn.execute(CREATE_TRANSACTIONS)
    conn.commit()
    print("✔  Tables created (or already exist).")

    # ── Check for existing test customer ───────────────────────────────────
    existing = conn.execute(
        "SELECT id FROM customers WHERE username = ?", (TEST_USERNAME,)
    ).fetchone()

    if existing:
        print(f"✔  Test customer '{TEST_USERNAME}' already exists — skipping insert.")
        conn.close()
        return

    # ── Insert test customer ───────────────────────────────────────────────
    hashed = generate_password_hash(TEST_PASSWORD)
    cursor = conn.execute(
        "INSERT INTO customers (username, password_hash, full_name) VALUES (?, ?, ?)",
        (TEST_USERNAME, hashed, TEST_FULL_NAME),
    )
    customer_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
        (customer_id, STARTING_BALANCE),
    )
    conn.commit()
    conn.close()

    print(f"✔  Test customer created:")
    print(f"   Username : {TEST_USERNAME}")
    print(f"   Password : {TEST_PASSWORD}")
    print(f"   Balance  : £{STARTING_BALANCE:,.2f}")


if __name__ == "__main__":
    seed()
