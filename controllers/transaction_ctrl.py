import models.transaction as tx_model
from state import AppState


def add_transaction(
    state: AppState,
    amount: float,
    type_: str,
    date_: str,
    category_id: int | None = None,
    description: str = "",
) -> None:
    tx_model.create(amount, type_, date_, category_id, description)
    state.reload()


def edit_transaction(
    state: AppState,
    transaction_id: int,
    amount: float,
    type_: str,
    date_: str,
    category_id: int | None = None,
    description: str = "",
) -> None:
    tx_model.update(transaction_id, amount, type_, date_, category_id, description)
    state.reload()


def remove_transaction(state: AppState, transaction_id: int) -> None:
    tx_model.delete(transaction_id)
    state.reload()
