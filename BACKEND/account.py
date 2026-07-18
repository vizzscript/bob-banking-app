"""
account.py
----------
Business logic for reading balances and applying transactions.

All database access goes through database.py — no raw sqlite3 calls here.
Route handlers in app.py call these functions; they never query the DB directly.
"""

from datetime import datetime, timezone

from database import execute_db, query_db
from models import row_to_account


class InsufficientFundsError(Exception):
    """Raised when a withdrawal amount exceeds the available balance."""


class InvalidAmountError(Exception):
    """Raised when an amount is not a positive number."""


# ── Internal helper ────────────────────────────────────────────────────────

def _get_account(customer_id: int):
    """Fetch the Account record for *customer_id*.

    Returns an Account dataclass or raises RuntimeError if none exists.
    """
    row = query_db(
        "SELECT * FROM accounts WHERE customer_id = ?",
        (customer_id,),
        one=True,
    )
    account = row_to_account(row)
    if account is None:
        raise RuntimeError(f"No account found for customer_id={customer_id}")
    return account


def _validate_amount(amount) -> float:
    """Convert *amount* to float and assert it is positive.

    Raises InvalidAmountError with a user-facing message on failure.
    """
    try:
        value = float(amount)
    except (TypeError, ValueError):
        raise InvalidAmountError("Please enter a valid numeric amount.")
    if value <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")
    return value


# ── Public API ─────────────────────────────────────────────────────────────

def get_balance(customer_id: int) -> float:
    """Return the current balance for the given customer."""
    return _get_account(customer_id).balance


def deposit(customer_id: int, amount) -> float:
    """Add *amount* to the customer's balance.

    Parameters
    ----------
    customer_id : ID of the logged-in customer.
    amount      : Raw value from request.form — will be validated here.

    Returns the updated balance as a float.
    Raises InvalidAmountError if the amount is not valid.
    """
    value = _validate_amount(amount)
    account = _get_account(customer_id)

    new_balance = round(account.balance + value, 2)

    execute_db(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (new_balance, account.id),
    )
    execute_db(
        "INSERT INTO transactions (account_id, transaction_type, amount, created_at) "
        "VALUES (?, 'deposit', ?, ?)",
        (account.id, value, datetime.now(timezone.utc).isoformat()),
    )
    return new_balance


def withdraw(customer_id: int, amount) -> float:
    """Subtract *amount* from the customer's balance.

    Parameters
    ----------
    customer_id : ID of the logged-in customer.
    amount      : Raw value from request.form — will be validated here.

    Returns the updated balance as a float.
    Raises InvalidAmountError if the amount is not valid.
    Raises InsufficientFundsError if the balance would go below zero.
    """
    value = _validate_amount(amount)
    account = _get_account(customer_id)

    if value > account.balance:
        raise InsufficientFundsError(
            f"Insufficient funds. Your current balance is £{account.balance:,.2f}."
        )

    new_balance = round(account.balance - value, 2)

    execute_db(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (new_balance, account.id),
    )
    execute_db(
        "INSERT INTO transactions (account_id, transaction_type, amount, created_at) "
        "VALUES (?, 'withdrawal', ?, ?)",
        (account.id, value, datetime.now(timezone.utc).isoformat()),
    )
    return new_balance
