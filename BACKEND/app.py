"""
app.py
------
Flask application entry point.

Configures the app, registers the DB teardown hook, and defines all routes.
Templates are served from FRONTEND/templates/; static files from FRONTEND/static/.

Run locally:
    cd BACKEND
    python app.py
"""

import os

from flask import Flask, redirect, render_template, request, url_for

import account as account_module
import auth as auth_module
import database
from account import InsufficientFundsError, InvalidAmountError

# ── Resolve cross-folder paths ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "FRONTEND")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

# ── Create Flask app ───────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
)

# Secret key signs the session cookie.
# In production, set the SECRET_KEY environment variable to a random value.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

# Register DB teardown so connections are closed after every request.
database.init_app(app)


# ══════════════════════════════════════════════════════════════════════════
# Authentication routes
# ══════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def index():
    """Root URL — redirect to login (or dashboard if already authenticated)."""
    if auth_module.get_current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """GET: render login form.  POST: validate credentials and start session."""
    # Already logged in — go straight to dashboard.
    if auth_module.get_current_user():
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        return render_template("login.html")

    # ── POST: process form submission ──────────────────────────────────────
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Backend presence check (supplements HTML `required` attribute).
    if not username or not password:
        return render_template(
            "login.html",
            error="Please enter both username and password.",
        )

    customer = auth_module.authenticate(username, password)
    if customer is None:
        return render_template(
            "login.html",
            error="Invalid username or password. Please try again.",
        )

    auth_module.login_user(customer.id)
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    """End the session and return to login."""
    auth_module.logout_user()
    return redirect(url_for("login"))


# ══════════════════════════════════════════════════════════════════════════
# Dashboard route
# ══════════════════════════════════════════════════════════════════════════

@app.route("/dashboard")
@auth_module.login_required
def dashboard():
    """Show the customer's name and current balance."""
    customer = auth_module.get_current_user()
    balance = account_module.get_balance(customer.id)
    return render_template(
        "dashboard.html",
        customer_name=customer.full_name,
        balance=f"{balance:,.2f}",
    )


# ══════════════════════════════════════════════════════════════════════════
# Transaction routes
# ══════════════════════════════════════════════════════════════════════════

@app.route("/deposit", methods=["GET", "POST"])
@auth_module.login_required
def deposit():
    """GET: render deposit form.  POST: apply deposit and show result."""
    customer = auth_module.get_current_user()

    if request.method == "GET":
        balance = account_module.get_balance(customer.id)
        return render_template("deposit.html", balance=f"{balance:,.2f}")

    # ── POST ───────────────────────────────────────────────────────────────
    raw_amount = request.form.get("amount", "")
    try:
        new_balance = account_module.deposit(customer.id, raw_amount)
        return render_template(
            "deposit.html",
            balance=f"{new_balance:,.2f}",
            success=f"Deposit successful. New balance: £{new_balance:,.2f}",
        )
    except InvalidAmountError as exc:
        balance = account_module.get_balance(customer.id)
        return render_template(
            "deposit.html",
            balance=f"{balance:,.2f}",
            error=str(exc),
        )


@app.route("/withdraw", methods=["GET", "POST"])
@auth_module.login_required
def withdraw():
    """GET: render withdraw form.  POST: apply withdrawal and show result."""
    customer = auth_module.get_current_user()

    if request.method == "GET":
        balance = account_module.get_balance(customer.id)
        return render_template("withdraw.html", balance=f"{balance:,.2f}")

    # ── POST ───────────────────────────────────────────────────────────────
    raw_amount = request.form.get("amount", "")

    if not raw_amount or not raw_amount.strip():
        balance = account_module.get_balance(customer.id)
        return render_template("withdraw.html", balance=f"{balance:,.2f}", error="Amount is required")

    try:
        amount_value = float(raw_amount)
    except ValueError:
        balance = account_module.get_balance(customer.id)
        return render_template("withdraw.html", balance=f"{balance:,.2f}", error="Amount must be greater than zero")

    if amount_value <= 0:
        balance = account_module.get_balance(customer.id)
        return render_template("withdraw.html", balance=f"{balance:,.2f}", error="Amount must be greater than zero")

    current_balance = account_module.get_balance(customer.id)
    if amount_value > current_balance:
        return render_template("withdraw.html", balance=f"{current_balance:,.2f}", error="Insufficient funds")

    try:
        new_balance = account_module.withdraw(customer.id, raw_amount)
        return render_template(
            "withdraw.html",
            balance=f"{new_balance:,.2f}",
            success=f"Withdrawal successful. New balance: £{new_balance:,.2f}",
        )
    except (InvalidAmountError, InsufficientFundsError) as exc:
        balance = account_module.get_balance(customer.id)
        return render_template(
            "withdraw.html",
            balance=f"{balance:,.2f}",
            error=str(exc),
        )


# ══════════════════════════════════════════════════════════════════════════
# Error handlers
# ══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):  # noqa: ARG001
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(500)
def server_error(error):  # noqa: ARG001
    return render_template("error.html", code=500, message="An unexpected error occurred."), 500


# ══════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)
