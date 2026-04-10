import models.ideal_month as im_model
from models.ideal_month import IdealMonth
from state import AppState


def add_ideal_month(state: AppState, name: str, description: str = "") -> IdealMonth:
    result = im_model.create(name, description)
    state.reload()
    return result


def edit_ideal_month(
    state: AppState, ideal_month_id: int, name: str, description: str = ""
) -> IdealMonth:
    result = im_model.update(ideal_month_id, name, description)
    state.reload()
    return result


def remove_ideal_month(state: AppState, ideal_month_id: int) -> None:
    im_model.delete(ideal_month_id)
    state.reload()


def save_items(state: AppState, ideal_month_id: int, items: list[dict]) -> None:
    im_model.set_items(ideal_month_id, items)
    state.reload()
