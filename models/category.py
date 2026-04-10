from dataclasses import dataclass
from models.database import get_connection


@dataclass
class Category:
    id: int
    name: str
    color: str
    icon: str
    type: str  # "income" | "expense" | "all"
    parent_id: int | None = None


def _row_to_category(row) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        color=row["color"],
        icon=row["icon"],
        type=row["type"],
        parent_id=row["parent_id"] if "parent_id" in row.keys() else None,
    )


def get_all() -> list[Category]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, color, icon, type, parent_id FROM categories ORDER BY name"
        ).fetchall()
    return [_row_to_category(r) for r in rows]


def get_top_level() -> list[Category]:
    """Return only categories with no parent (cannot be used as subcategories)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, color, icon, type, parent_id FROM categories"
            " WHERE parent_id IS NULL ORDER BY name"
        ).fetchall()
    return [_row_to_category(r) for r in rows]


def get_by_id(category_id: int) -> Category | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, color, icon, type, parent_id FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
    return _row_to_category(row) if row else None


def create(name: str, color: str, icon: str, type_: str, parent_id: int | None = None) -> Category:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO categories (name, color, icon, type, parent_id) VALUES (?, ?, ?, ?, ?)",
            (name, color, icon, type_, parent_id),
        )
        return get_by_id(cur.lastrowid)


def update(
    category_id: int,
    name: str,
    color: str,
    icon: str,
    type_: str,
    parent_id: int | None = None,
) -> Category:
    with get_connection() as conn:
        conn.execute(
            "UPDATE categories SET name=?, color=?, icon=?, type=?, parent_id=? WHERE id=?",
            (name, color, icon, type_, parent_id, category_id),
        )
    return get_by_id(category_id)


def delete(category_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
