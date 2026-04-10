from dataclasses import dataclass
from datetime import date, datetime
from models.database import get_connection


@dataclass
class Transaction:
    id: int
    amount: float
    type: str       # "income" | "expense"
    category_id: int | None
    description: str
    date: str       # ISO 8601: YYYY-MM-DD
    created_at: str


def _row_to_transaction(row) -> Transaction:
    return Transaction(
        id=row["id"],
        amount=row["amount"],
        type=row["type"],
        category_id=row["category_id"],
        description=row["description"] or "",
        date=row["date"],
        created_at=row["created_at"],
    )


def get_all(month: str | None = None) -> list[Transaction]:
    """Retorna transações. Se month='YYYY-MM', filtra pelo mês."""
    with get_connection() as conn:
        if month:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC",
                (month,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM transactions ORDER BY date DESC"
            ).fetchall()
    return [_row_to_transaction(r) for r in rows]


def get_by_id(transaction_id: int) -> Transaction | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
    return _row_to_transaction(row) if row else None


def create(
    amount: float,
    type_: str,
    date_: str,
    category_id: int | None = None,
    description: str = "",
) -> Transaction:
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO transactions (amount, type, category_id, description, date, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (amount, type_, category_id, description, date_, now),
        )
        return get_by_id(cur.lastrowid)


def update(
    transaction_id: int,
    amount: float,
    type_: str,
    date_: str,
    category_id: int | None = None,
    description: str = "",
) -> Transaction:
    with get_connection() as conn:
        conn.execute(
            """UPDATE transactions
               SET amount=?, type=?, category_id=?, description=?, date=?
               WHERE id=?""",
            (amount, type_, category_id, description, date_, transaction_id),
        )
    return get_by_id(transaction_id)


def delete(transaction_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
