# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** This guide is derived from `IMPLEMENTATION_PLAN.md`.
> Instructions are written in plain English, describing **what to do and why** — not the actual code.

---

## 1. Environment Setup

### 1.1 Prerequisites
- Python 3.9 or higher
- pip (bundled with Python)
- A code editor (VS Code recommended)

### 1.2 Create the Folder Structure
Create `FRONTEND/templates/`, `FRONTEND/static/css/`, and `BACKEND/` at the project root.

### 1.3 Python Virtual Environment
```bash
cd BACKEND
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 1.4 Install Dependencies
```bash
pip install -r requirements.txt
```

### 1.5 Verify Flask Runs
Create a minimal `app.py` returning "Hello, Bank!" and confirm `http://127.0.0.1:5000` loads.

---

## 2. Backend Implementation

Work through backend files in this order: `database.py` → `models.py` → `seed.py` → `auth.py` → `account.py` → `app.py`.

### 2.1 `database.py` — Database Layer
- Open a per-request SQLite connection using Flask `g`.
- Register a `teardown_appcontext` hook to close connections.
- Provide `query_db()` and `execute_db()` helpers used by all other modules.

### 2.2 `models.py` — Data Models
Define plain Python dataclasses for `Customer`, `Account`, and `Transaction`.

### 2.3 `seed.py` — Database Seed
1. Connect to `bank.db`.
2. Create tables (`customers`, `accounts`, `transactions`) if they do not exist.
3. Check for an existing test customer to avoid duplicate inserts.
4. Insert one test customer with a **hashed** password and a starting balance of £1,000.

Run once before starting the app: `python seed.py`

### 2.4 `auth.py` — Authentication
- `authenticate(username, password)` — returns a `Customer` on success, `None` on failure.
- `login_user(customer_id)` — clears session then stores customer ID.
- `logout_user()` — removes customer ID from session.
- `get_current_user()` — looks up the customer from the session on every request.
- `login_required` decorator — redirects to `/login` if no valid session exists.

### 2.5 `account.py` — Business Logic
- `get_balance(customer_id)` — returns current balance.
- `deposit(customer_id, amount)` — validates amount, adds to balance, records transaction.
- `withdraw(customer_id, amount)` — validates amount, checks sufficiency, subtracts from balance, records transaction.
- Raises `InvalidAmountError` and `InsufficientFundsError` for invalid operations.

### 2.6 `app.py` — Flask Routes

| Route | Method | Behaviour |
|---|---|---|
| `/` | GET | Redirect to login or dashboard |
| `/login` | GET | Render login form |
| `/login` | POST | Validate credentials, start session |
| `/dashboard` | GET | Show name + balance (protected) |
| `/deposit` | GET | Render deposit form (protected) |
| `/deposit` | POST | Apply deposit, show result (protected) |
| `/withdraw` | GET | Render withdraw form (protected) |
| `/withdraw` | POST | Apply withdrawal, show result (protected) |
| `/logout` | GET | Clear session, redirect to login |

---

## 3. Frontend Implementation

### 3.1 `base.html` — Shared Layout
- Full HTML structure with Bootstrap 5 CDN.
- Navbar with conditional links: Dashboard / Deposit / Withdraw / Logout when logged in; Login when not.
- `{% block content %}` placeholder for child pages.

### 3.2 `login.html`
- Centred Bootstrap card with username + password inputs.
- `{% if error %}` block renders a `alert-danger` message.

### 3.3 `dashboard.html`
- Greeting with `{{ customer_name }}`.
- Balance card showing `{{ balance }}`.
- Deposit and Withdraw action buttons.

### 3.4 `deposit.html`
- Current balance badge, numeric amount input (`min=0.01`, `step=0.01`).
- `{% if success %}` and `{% if error %}` alert blocks.

### 3.5 `withdraw.html`
- Available balance badge before the input form.
- Same alert blocks as deposit plus specific insufficient-funds messaging.

---

## 4. Integration Steps

1. Pass `template_folder` and `static_folder` pointing to `FRONTEND/` when creating the Flask app.
2. Ensure each `render_template()` call passes variable names that exactly match `{{ }}` placeholders in the HTML.
3. Use Flask `g` + `teardown_appcontext` for request-scoped DB connections.
4. Match HTML form `action` URLs and input `name` attributes to Flask route paths and `request.form` keys.

---

## 5. Validation Rules

### Login
- Backend: reject blank username or password before querying the DB.
- Use identical error message for wrong username vs wrong password (prevents user enumeration).

### Deposit
- Frontend: `type=number`, `min=0.01`, `step=0.01`, `required`.
- Backend: convert to float (catch `ValueError`), assert value > 0.

### Withdrawal
- Same as deposit plus: assert `amount <= current_balance`, else raise `InsufficientFundsError`.

### Session Guard
- All routes except `/login` and `/logout` must be wrapped with `@login_required`.

---

## 6. Testing

### Unit Tests (`tests/test_auth.py`, `tests/test_account.py`)
- Use in-memory SQLite; never touch the real `bank.db`.
- Test correct login, wrong password, unknown user, blank fields.
- Test deposit increases balance, records transaction row.
- Test withdrawal decreases balance, fails on overdraft, leaves balance unchanged on failure.

### Integration Tests (`tests/test_routes.py`)
- Use Flask test client with an in-memory DB.
- Cover: login success/failure, protected route redirect, deposit POST, withdrawal POST, logout.

### Run Tests
```bash
cd BACKEND && source venv/bin/activate
python -m pytest tests/ -v
# Expected: 37 passed
```

---

## 7. Deployment

### Local (Development)
```bash
cd BACKEND
source venv/bin/activate
python seed.py          # first run only
python app.py           # starts on http://127.0.0.1:5000
```

### Production Checklist
- Set `SECRET_KEY` via environment variable.
- Replace Flask dev server with **Gunicorn** or **Waitress**.
- Place behind **Nginx** reverse proxy for HTTPS and static file serving.
- Set `FLASK_DEBUG=0`.
- Migrate to **PostgreSQL** for concurrent workloads.

---

*End of Step-by-Step Implementation Guide*
