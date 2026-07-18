# Banking Web Application — Implementation Plan

> **Planning Level Document Only**
> This document covers architecture, design, and roadmap. It does not include database schemas, SQL scripts, API contracts, or step-by-step implementation code.

---

## 1. Solution Overview

### Objective
Build a lightweight, browser-based banking web application that allows customers to securely log in, view their account balance, and perform basic financial transactions (deposit and withdrawal).

### Scope
| In Scope | Out of Scope |
|---|---|
| Customer login and session management | Admin portal or multi-role access |
| Dashboard with balance summary | Inter-account transfers |
| Deposit and withdrawal operations | Notifications or email alerts |
| Logout and session termination | Loan, credit, or investment features |
| Persistent data via SQLite | External payment gateway integration |

### Users
- **Banking Customer** — the sole user persona. An existing customer who authenticates and manages their own account.

### Functional Requirements
1. A customer must be able to log in with valid credentials.
2. An authenticated customer must see a personalised dashboard showing their name and current balance.
3. A customer must be able to deposit a positive amount into their account.
4. A customer must be able to withdraw an amount up to their available balance.
5. A customer must be able to log out, which invalidates their session.
6. Unauthenticated users must not access any protected page.

### Non-Functional Requirements
- **Security** — Passwords must be stored as hashed values; sessions must be server-side.
- **Usability** — UI must be responsive and usable on both desktop and mobile browsers via Bootstrap.
- **Simplicity** — The stack must be easy to run locally without external services.
- **Maintainability** — Clear separation of concerns between frontend, backend, and data layers.
- **Performance** — All operations (login, deposit, withdraw) complete within a single page interaction.

### Assumptions
- A small, fixed set of customer accounts is pre-seeded in the database (no self-registration flow).
- SQLite is sufficient for the single-user / low-concurrency workshop context.
- Bootstrap is loaded from a CDN; no build toolchain (Webpack, npm) is required for the frontend.
- The application runs on `localhost` during development; no HTTPS configuration is planned at this stage.
- A single account per customer is assumed (no multi-account management).

---

## 2. High-Level Architecture

### Architecture Diagram

```
+------------------------------------------------------------------+
|                         BROWSER (Client)                          |
|                                                                    |
|   +--------------------------------------------------------------+|
|   |            FRONTEND  (FRONTEND/)                              ||
|   |   HTML templates + Bootstrap CSS/JS                           ||
|   |   Pages: Login - Dashboard - Deposit - Withdraw               ||
|   +-----------------------------+--------------------------------+|
+-----------------------------+--------------------------------------+
                              |  HTTP Request (form POST / GET)
                              v
+------------------------------------------------------------------+
|                    BACKEND  (BACKEND/)                             |
|                                                                    |
|   +--------------+   +--------------+   +-------------------+    |
|   |  Auth Module  |   |  Dashboard   |   |  Transaction      |    |
|   |  /login       |   |  /dashboard  |   |  /deposit         |    |
|   |  /logout      |   |              |   |  /withdraw        |    |
|   +--------------+   +--------------+   +-------------------+    |
|                             |                                      |
|                    Flask App Core (app.py)                         |
|                    Session Management                              |
+-----------------------------+--------------------------------------+
                              |  SQL queries via SQLite3
                              v
+------------------------------------------------------------------+
|                    DATABASE  (BACKEND/)                            |
|               SQLite file  (bank.db)                              |
|               Tables: customers, accounts, transactions            |
+------------------------------------------------------------------+
```

### Request Lifecycle

| Step | Actor | Action |
|---|---|---|
| 1 | Browser | User submits a form or navigates to a URL |
| 2 | Flask Router | Matches URL to the correct route function |
| 3 | Auth Guard | Checks server-side session for a valid login |
| 4 | Business Logic | Performs the operation (balance lookup, deposit, withdraw) |
| 5 | Database Layer | Reads or writes data in `bank.db` |
| 6 | Template Engine | Flask renders a Jinja2 HTML template with result data |
| 7 | Browser | Displays the rendered page to the customer |

---

## 3. Component Design

### Frontend Responsibilities (`FRONTEND/`)
- Provide all HTML page templates rendered by the Flask Jinja2 engine.
- Use **Bootstrap** for responsive layout, form styling, buttons, alerts, and navigation.
- Display server-injected data (balance, transaction feedback, error messages) passed from Flask.
- Handle only presentation logic — no business rules, no direct database access.

### Backend Responsibilities (`BACKEND/`)
- Expose HTTP routes for every user action: login, dashboard view, deposit, withdraw, logout.
- Enforce authentication via Flask session; redirect unauthenticated requests to the login page.
- Contain all business logic: credential validation, balance checks, transaction application.
- Serve as the only layer that reads from or writes to the database.

### Database Responsibilities
- Persist customer credentials (hashed), account balances, and transaction history.
- Managed exclusively by the backend; the frontend has no direct database access.
- Stored as a single SQLite file (`bank.db`) inside the `BACKEND/` folder for portability.

---

## 4. Folder Structure

```
bob-banking-app/
|
+-- IMPLEMENTATION_PLAN.md
+-- STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
+-- FRONTEND/
|   +-- templates/
|   |   +-- base.html
|   |   +-- login.html
|   |   +-- dashboard.html
|   |   +-- deposit.html
|   |   +-- withdraw.html
|   |   +-- error.html
|   +-- static/css/
|       +-- custom.css
+-- BACKEND/
    +-- app.py
    +-- auth.py
    +-- account.py
    +-- database.py
    +-- models.py
    +-- seed.py
    +-- requirements.txt
    +-- tests/
        +-- test_auth.py
        +-- test_account.py
        +-- test_routes.py
```

---

## 5. Module Breakdown

### Authentication Module
- **Purpose** — Identify the customer and establish a secure session.
- **Entry point** — `GET /` and `POST /login` routes.
- **Session guard** — A `login_required` decorator applied to all protected routes.

### Dashboard Module
- **Purpose** — Provide the customer's landing page after login.
- **Entry point** — `GET /dashboard` route.

### Account Management Module
- **Purpose** — Centralise all read and write operations on account data.
- **Scope** — Used internally by the Transaction module.

### Transactions Module
- **Purpose** — Handle the business logic for deposits and withdrawals.
- **Entry points** — `GET/POST /deposit` and `GET/POST /withdraw`.

---

## 6. Implementation Roadmap

| Phase | Description | Effort |
|---|---|---|
| 1 | Project Scaffolding | Low |
| 2 | Database & Seed Setup | Low-Medium |
| 3 | Authentication | Medium |
| 4 | Dashboard | Low |
| 5 | Transactions | Medium |
| 6 | Integration & Testing | Low-Medium |

### Dependency Chain

```
Phase 1 (Scaffolding)
    +-- Phase 2 (Database)
            +-- Phase 3 (Authentication)
                    +-- Phase 4 (Dashboard)
                            +-- Phase 5 (Transactions)
                                    +-- Phase 6 (Integration)
```

---

*End of Implementation Plan*
