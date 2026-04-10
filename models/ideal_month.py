import sqlite3
from dataclasses import dataclass
from models.database import get_connection


@dataclass
class IdealMonth:
    id: int
    name: str
    description: str
    created_at: str


@dataclass
class IdealMonthItem:
    id: int
    ideal_month_id: int
    category_id: int | None
    amount: float
    type: str  # "income" | "expense"
    created_at: str


def get_all() -> list[IdealMonth]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, description, created_at FROM ideal_months ORDER BY name"
        ).fetchall()
    return [IdealMonth(**dict(r)) for r in rows]


def get_by_id(ideal_month_id: int) -> IdealMonth | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, description, created_at FROM ideal_months WHERE id = ?",
            (ideal_month_id,),
        ).fetchone()
    return IdealMonth(**dict(row)) if row else None


def create(name: str, description: str = "") -> IdealMonth:
    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO ideal_months (name, description) VALUES (?, ?)",
                (name, description),
            )
            return get_by_id(cur.lastrowid)
    except sqlite3.IntegrityError:
        raise ValueError("name_exists")


def update(ideal_month_id: int, name: str, description: str = "") -> IdealMonth:
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE ideal_months SET name = ?, description = ? WHERE id = ?",
                (name, description, ideal_month_id),
            )
        return get_by_id(ideal_month_id)
    except sqlite3.IntegrityError:
        raise ValueError("name_exists")


def delete(ideal_month_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM ideal_months WHERE id = ?", (ideal_month_id,))


def get_items(ideal_month_id: int) -> list[IdealMonthItem]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, ideal_month_id, category_id, amount, type, created_at
            FROM ideal_month_items
            WHERE ideal_month_id = ?
            ORDER BY type DESC, amount DESC
            """,
            (ideal_month_id,),
        ).fetchall()
    return [IdealMonthItem(**dict(r)) for r in rows]


def set_items(ideal_month_id: int, items: list[dict]) -> None:
    """Replace all items for a template atomically."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM ideal_month_items WHERE ideal_month_id = ?",
            (ideal_month_id,),
        )
        conn.executemany(
            "INSERT INTO ideal_month_items (ideal_month_id, category_id, amount, type) VALUES (?, ?, ?, ?)",
            [
                (ideal_month_id, item.get("category_id"), item["amount"], item["type"])
                for item in items
            ],
        )


def get_comparison(ideal_month_id: int, month: str) -> list[dict]:
    """
    Compare ideal month targets against actual transactions for the given month.
    Returns a list of dicts with keys:
        category_id, category_name, category_color, type, target, actual, diff
    Ordered: income first, then expense; each group sorted by target descending.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                imi.id          AS item_id,
                imi.type        AS type,
                imi.amount      AS target,
                c.id            AS category_id,
                c.name          AS category_name,
                c.color         AS category_color,
                COALESCE(
                    (
                        SELECT SUM(t.amount)
                        FROM transactions t
                        WHERE t.category_id = imi.category_id
                          AND t.type = imi.type
                          AND strftime('%Y-%m', t.date) = :month
                    ), 0.0
                ) AS actual
            FROM ideal_month_items imi
            LEFT JOIN categories c ON c.id = imi.category_id
            WHERE imi.ideal_month_id = :ideal_month_id
            ORDER BY
                CASE imi.type WHEN 'income' THEN 0 ELSE 1 END,
                imi.amount DESC
            """,
            {"ideal_month_id": ideal_month_id, "month": month},
        ).fetchall()

    result = []
    for r in rows:
        result.append({
            "category_id": r["category_id"],
            "category_name": r["category_name"],
            "category_color": r["category_color"] or "#607D8B",
            "type": r["type"],
            "target": r["target"],
            "actual": r["actual"],
            "diff": r["actual"] - r["target"],
        })
    return result
