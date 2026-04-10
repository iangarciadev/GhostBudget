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

            CREATE TABLE IF NOT EXISTS ideal_months (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS ideal_month_items (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                ideal_month_id  INTEGER NOT NULL REFERENCES ideal_months(id) ON DELETE CASCADE,
                category_id     INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                amount          REAL    NOT NULL,
                type            TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
                created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        _seed_default_categories(conn)
        _migrate_colors(conn)


def _seed_default_categories(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if existing > 0:
        return

    defaults = [
        ("Alimentação",   "#FFE53935", "restaurant",       "expense"),
        ("Transporte",    "#FFFB8C00", "directions_car",   "expense"),
        ("Moradia",       "#FF8E24AA", "home",             "expense"),
        ("Saúde",         "#FF00897B", "health_and_safety","expense"),
        ("Lazer",         "#FF1E88E5", "sports_esports",   "expense"),
        ("Educação",      "#FFF4511E", "school",           "expense"),
        ("Outros gastos", "#FF546E7A", "more_horiz",       "expense"),
        ("Salário",       "#FF43A047", "payments",         "income"),
        ("Freelance",     "#FF00ACC1", "work",             "income"),
        ("Outros ganhos", "#FF7CB342", "attach_money",     "income"),
    ]
    conn.executemany(
        "INSERT INTO categories (name, color, icon, type) VALUES (?, ?, ?, ?)",
        defaults,
    )


def _migrate_colors(conn: sqlite3.Connection) -> None:
    """Convert any stored 6-digit hex colors (#RRGGBB) to 8-digit ARGB (#FFRRGGBB)."""
    rows = conn.execute("SELECT id, color FROM categories").fetchall()
    for row in rows:
        color = row["color"]
        if color.startswith("#") and len(color) == 7:
            conn.execute(
                "UPDATE categories SET color = ? WHERE id = ?",
                ("#FF" + color[1:], row["id"]),
            )
    rows = conn.execute("SELECT id, color FROM investments").fetchall()
    for row in rows:
        color = row["color"]
        if color.startswith("#") and len(color) == 7:
            conn.execute(
                "UPDATE investments SET color = ? WHERE id = ?",
                ("#FF" + color[1:], row["id"]),
            )
