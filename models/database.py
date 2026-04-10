import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "budget.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                color     TEXT    NOT NULL DEFAULT '#607D8B',
                icon      TEXT    NOT NULL DEFAULT 'category',
                type      TEXT    NOT NULL DEFAULT 'all'
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                amount      REAL    NOT NULL,
                type        TEXT    NOT NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                description TEXT,
                date        TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS investments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                color      TEXT    NOT NULL DEFAULT '#009688',
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS investment_transactions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                investment_id INTEGER NOT NULL REFERENCES investments(id) ON DELETE CASCADE,
                amount        REAL    NOT NULL,
                operation     TEXT    NOT NULL CHECK(operation IN ('deposit', 'withdrawal')),
                note          TEXT,
                date          TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        _seed_default_categories(conn)


def _seed_default_categories(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if existing > 0:
        return

    defaults = [
        ("Alimentação",   "#E53935", "restaurant",    "expense"),
        ("Transporte",    "#FB8C00", "directions_car","expense"),
        ("Moradia",       "#8E24AA", "home",           "expense"),
        ("Saúde",         "#00897B", "health_and_safety", "expense"),
        ("Lazer",         "#1E88E5", "sports_esports", "expense"),
        ("Educação",      "#F4511E", "school",         "expense"),
        ("Outros gastos", "#546E7A", "more_horiz",     "expense"),
        ("Salário",       "#43A047", "payments",       "income"),
        ("Freelance",     "#00ACC1", "work",           "income"),
        ("Outros ganhos", "#7CB342", "attach_money",   "income"),
    ]
    conn.executemany(
        "INSERT INTO categories (name, color, icon, type) VALUES (?, ?, ?, ?)",
        defaults,
    )
