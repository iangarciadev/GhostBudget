from models.database import get_connection


def get_monthly_summary(month: str) -> dict:
    """Retorna total de receitas, despesas e saldo do mês."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS total_expense
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?
            """,
            (month,),
        ).fetchone()
    income = row["total_income"]
    expense = row["total_expense"]
    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
    }


def get_expense_by_category(month: str) -> list[dict]:
    """Retorna lista {category_id, name, color, total} das despesas do mês por categoria."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id   AS category_id,
                c.name AS name,
                c.color AS color,
                COALESCE(SUM(t.amount), 0) AS total
            FROM categories c
            LEFT JOIN transactions t
                ON t.category_id = c.id
                AND t.type = 'expense'
                AND strftime('%Y-%m', t.date) = ?
            WHERE c.type IN ('expense', 'all')
            GROUP BY c.id
            HAVING total > 0
            ORDER BY total DESC
            """,
            (month,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_monthly_trend(months: int = 6) -> list[dict]:
    """Retorna lista {month, income, expense} dos últimos N meses."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                strftime('%Y-%m', date) AS month,
                COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS expense
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT ?
            """,
            (months,),
        ).fetchall()
    return list(reversed([dict(r) for r in rows]))
