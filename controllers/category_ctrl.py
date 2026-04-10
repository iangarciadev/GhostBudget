import models.category as cat_model
from state import AppState


def add_category(state: AppState, name: str, color: str, icon: str, type_: str) -> None:
    cat_model.create(name, color, icon, type_)
    state.reload()


def edit_category(
    state: AppState, category_id: int, name: str, color: str, icon: str, type_: str
) -> None:
    cat_model.update(category_id, name, color, icon, type_)
    state.reload()


def remove_category(state: AppState, category_id: int) -> None:
    cat_model.delete(category_id)
    state.reload()
