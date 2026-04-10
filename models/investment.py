from dataclasses import dataclass
from datetime import datetime
from models.database import get_connection


@dataclass
class Investment:
    id: int
    name: str
    color: str
    balance: float
    created_at: str


@dataclass
class InvestmentTransaction:
    id: int
    investment_id: int
    amount: float
    operation: str
    note: str
    date: str
    created_at: str


def _row_to_investment(row) -> Investment:
    return Investment(
        id=row["id"],
        name=row["name"],
        color=row["color"],
        balance=row["balance"] or 0.0,
        created_at=row["created_at"],
    )


_BALANCE_QUERY = """
    SELECT i.id, i.name, i.color, i.created_at,
        COALESCE(SUM(
            CASE it.operation
                WHEN 'deposit'    THEN  it.amount
                WHEN 'withdrawal' THEN -it.amount
                ELSE 0
            END
        ), 0) AS balance
    FROM investments i
    LEFT JOIN investment_transactions it ON it.investment_id = i.id
"""


def get_all() -> list:
    with get_connection() as conn:
        rows = conn.execute(_BALANCE_QUERY + " GROUP BY i.id ORDER BY i.name").fetchall()
    return [_row_to_investment(r) for r in rows]


def get_by_id(investment_id: int):
    with get_connection() as conn:
        row = conn.execute(
            _BALANCE_QUERY + " WHERE i.id = ? GROUP BY i.id", (investment_id,)
        ).fetchone()
    return _row_to_investment(row) if row else None


def create(name: str, color: str) -> Investment:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO investments (name, color) VALUES (?, ?)", (name, color))
        new_id = cur.lastrowid
    return get_by_id(new_id)


def update(investment_id: int, name: str, color: str) -> Investment:
    with get_connection() as conn:
        conn.execute(
            "UPDATE investments SET name=?, color=? WHERE id=?",
            (name, color, investment_id),
        )
    return get_by_id(investment_id)


def delete(investment_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM investments WHERE id = ?", (investment_id,))


def add_operation(investment_id: int, amount: float, operation: str, date_: str, note: str = "") -> None:
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO investment_transactions "
            "(investment_id, amount, operation, note, date, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (investment_id, amount, operation, note, date_, now),
        )
