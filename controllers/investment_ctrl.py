import models.investment as inv_model
from state import AppState


def add_investment(state: AppState, name: str, color: str) -> None:
    inv_model.create(name, color)
    state.reload()


def edit_investment(state: AppState, investment_id: int, name: str, color: str) -> None:
    inv_model.update(investment_id, name, color)
    state.reload()


def remove_investment(state: AppState, investment_id: int) -> None:
    inv_model.delete(investment_id)
    state.reload()


def deposit(state: AppState, investment_id: int, amount: float, date_: str, note: str = "") -> None:
    inv_model.add_operation(investment_id, amount, "deposit", date_, note)
    state.reload()


def withdraw(state: AppState, investment_id: int, amount: float, date_: str, note: str = "") -> None:
    current = next((i for i in state.investments if i.id == investment_id), None)
    if current and amount > current.balance:
        raise ValueError("insufficient_balance")
    inv_model.add_operation(investment_id, amount, "withdrawal", date_, note)
    state.reload()
