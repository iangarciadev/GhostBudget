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
    """Retorna despesas do mês agrupadas hierarquicamente.

    Cada item de nível superior tem:
        {category_id, name, color, total, subcategories}
    onde total = gastos diretos na categoria-mãe + soma das subcategorias,
    e subcategories é lista de {category_id, name, total}.
    Subcategorias sem gasto no mês não aparecem na lista interna.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id        AS category_id,
                c.name      AS name,
                c.color     AS color,
                c.parent_id AS parent_id,
                COALESCE(SUM(t.amount), 0) AS direct_total
            FROM categories c
            LEFT JOIN transactions t
                ON t.category_id = c.id
                AND t.type = 'expense'
                AND strftime('%Y-%m', t.date) = ?
            WHERE c.type IN ('expense', 'all')
            GROUP BY c.id
            """,
            (month,),
        ).fetchall()

    all_cats = [dict(r) for r in rows]

    # Index by id for fast lookup
    by_id = {r["category_id"]: r for r in all_cats}

    # Separate top-level from subcategories
    top_level = [r for r in all_cats if r["parent_id"] is None]
    subs_by_parent: dict[int, list[dict]] = {}
    for r in all_cats:
        if r["parent_id"] is not None:
            subs_by_parent.setdefault(r["parent_id"], []).append(r)

    result = []
    for parent in top_level:
        subs = subs_by_parent.get(parent["category_id"], [])
        active_subs = sorted(
            [s for s in subs if s["direct_total"] > 0],
            key=lambda x: x["direct_total"],
            reverse=True,
        )
        parent_total = parent["direct_total"] + sum(s["direct_total"] for s in subs)
        if parent_total <= 0:
            continue
        result.append(
            {
                "category_id": parent["category_id"],
                "name": parent["name"],
                "color": parent["color"],
                "total": parent_total,
                "subcategories": [
                    {"category_id": s["category_id"], "name": s["name"], "total": s["direct_total"]}
                    for s in active_subs
                ],
            }
        )

    result.sort(key=lambda x: x["total"], reverse=True)
    return result


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
