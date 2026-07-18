# SecureBank — Banking Web Application

A full-stack banking web application built with **Python Flask**, **SQLite**, and **Bootstrap 5**.

---

## Features

| Feature | Route |
|---|---|
| Customer Login | `GET/POST /login` |
| Dashboard with balance | `GET /dashboard` |
| Deposit funds | `GET/POST /deposit` |
| Withdraw funds | `GET/POST /withdraw` |
| Logout | `GET /logout` |

---

## Project Structure

```
bob-banking-app/
├── FRONTEND/
│   ├── templates/          ← Jinja2 HTML pages (base, login, dashboard, deposit, withdraw, error)
│   └── static/css/         ← Bootstrap overrides (custom.css)
├── BACKEND/
│   ├── app.py              ← Flask app entry point + all routes
│   ├── auth.py             ← Login, logout, session guard decorator
│   ├── account.py          ← get_balance(), deposit(), withdraw()
│   ├── database.py         ← Per-request SQLite connection via Flask g
│   ├── models.py           ← Customer, Account, Transaction dataclasses
│   ├── seed.py             ← Creates tables + inserts test customer
│   ├── requirements.txt
│   └── tests/
│       ├── test_auth.py        ← 7 unit tests
│       ├── test_account.py     ← 13 unit tests
│       └── test_routes.py      ← 17 integration tests
├── IMPLEMENTATION_PLAN.md
└── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vizzscript/bob-banking-app.git
cd bob-banking-app

# 2. Create and activate virtual environment
cd BACKEND
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed the database (run once)
python seed.py

# 5. Start the Flask development server
python app.py
```

Open your browser at **http://127.0.0.1:5000**

**Demo credentials:** `john_doe` / `password123` (starting balance: £1,000.00)

---

## Running Tests

```bash
cd BACKEND
source venv/bin/activate
python -m pytest tests/ -v
```

Expected: **37 passed**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5 + Bootstrap 5 + Bootstrap Icons |
| Backend | Python 3.12 + Flask 3.0 |
| Database | SQLite (via Python stdlib `sqlite3`) |
| Auth | Werkzeug `pbkdf2:sha256` password hashing |
| Tests | pytest 8.2 |

---

## Security Notes

- Passwords stored as **Werkzeug hashed values** — never plain text
- **Session fixation** prevented (`session.clear()` before login)
- **User enumeration** prevented — identical error for wrong username vs wrong password
- All protected routes enforce **server-side session checks** via `@login_required`
- `SECRET_KEY` reads from environment variable in production

---

## Production Checklist

- [ ] Set `SECRET_KEY` via environment variable
- [ ] Replace Flask dev server with **Gunicorn** or **Waitress**
- [ ] Serve static files via **Nginx**
- [ ] Enable **HTTPS** via reverse proxy
- [ ] Set `FLASK_DEBUG=0`
- [ ] Migrate database to **PostgreSQL** for multi-user load
