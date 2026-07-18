"""
models.py
---------
Plain Python dataclasses representing the application's core entities.

These are used to pass structured data between modules instead of raw
sqlite3.Row objects or bare tuples.  No ORM, no magic — just data holders.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Customer:
    """Represents a bank customer (authentication identity)."""

    id: int
    username: str
    password_hash: str
    full_name: str


@dataclass
class Account:
    """Represents the single account owned by a customer."""

    id: int
    customer_id: int
    balance: float


@dataclass
class Transaction:
    """A single deposit or withdrawal event recorded for audit purposes."""

    id: int
    account_id: int
    transaction_type: str          # 'deposit' or 'withdrawal'
    amount: float
    created_at: Optional[datetime] = None


def row_to_customer(row) -> Optional[Customer]:
    """Convert a sqlite3.Row (or None) from the customers table to a Customer."""
    if row is None:
        return None
    return Customer(
        id=row["id"],
        username=row["username"],
        password_hash=row["password_hash"],
        full_name=row["full_name"],
    )


def row_to_account(row) -> Optional[Account]:
    """Convert a sqlite3.Row (or None) from the accounts table to an Account."""
    if row is None:
        return None
    return Account(
        id=row["id"],
        customer_id=row["customer_id"],
        balance=float(row["balance"]),
    )
