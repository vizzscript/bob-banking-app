"""
auth.py
-------
Authentication helpers: login verification, session management, and the
login_required decorator used to protect routes.
"""

from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash

from database import query_db
from models import row_to_customer


# ── Key stored in Flask session ────────────────────────────────────────────
SESSION_KEY = "customer_id"


# ── Login ──────────────────────────────────────────────────────────────────

def authenticate(username: str, password: str):
    """Verify *username* / *password* against the database.

    Returns a ``Customer`` dataclass on success, or ``None`` on failure.
    The same ``None`` is returned whether the username does not exist or the
    password is wrong — this prevents user-enumeration attacks.
    """
    if not username or not password:
        return None

    row = query_db(
        "SELECT * FROM customers WHERE username = ?",
        (username.strip(),),
        one=True,
    )
    customer = row_to_customer(row)
    if customer is None:
        return None

    if not check_password_hash(customer.password_hash, password):
        return None

    return customer


# ── Session helpers ────────────────────────────────────────────────────────

def login_user(customer_id: int) -> None:
    """Store the customer's ID in the signed session cookie."""
    session.clear()                     # guard against session fixation
    session[SESSION_KEY] = customer_id


def logout_user() -> None:
    """Remove the customer's ID from the session."""
    session.pop(SESSION_KEY, None)


def get_current_user():
    """Return the logged-in ``Customer`` or ``None`` if not authenticated.

    Reads the customer ID from the session and performs a DB lookup so that
    revoked / deleted accounts are handled correctly on every request.
    """
    customer_id = session.get(SESSION_KEY)
    if customer_id is None:
        return None

    row = query_db(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,),
        one=True,
    )
    return row_to_customer(row)


# ── Route decorator ────────────────────────────────────────────────────────

def login_required(f):
    """Decorator that redirects unauthenticated requests to the login page."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if get_current_user() is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated
