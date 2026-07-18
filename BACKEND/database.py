"""
database.py
-----------
Centralised SQLite connection management.

All other modules import get_db() to obtain a per-request connection.
Flask's teardown_appcontext hook calls close_db() at the end of each request
so connections are never leaked.
"""

import os
import sqlite3

from flask import g

# Absolute path to the database file, sitting next to this module.
DB_PATH = os.path.join(os.path.dirname(__file__), "bank.db")


def get_db():
    """Return the open SQLite connection for the current request context.

    Creates the connection on first call within a request and stores it on
    Flask's ``g`` object so subsequent calls in the same request reuse it.
    Row factory is set to ``sqlite3.Row`` so columns can be accessed by name.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        # Enforce foreign-key constraints for every connection.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):  # noqa: ARG001
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(sql, args=(), one=False):
    """Execute *sql* with *args* and return result rows.

    Parameters
    ----------
    sql:  SQL string with ``?`` placeholders.
    args: Tuple of values to bind.
    one:  If True, return a single Row or None instead of a list.
    """
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(sql, args=()):
    """Execute a write statement (INSERT / UPDATE / DELETE).

    Commits automatically and returns the ``lastrowid`` of the statement.
    """
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def init_app(app):
    """Register the teardown hook with the Flask application."""
    app.teardown_appcontext(close_db)
