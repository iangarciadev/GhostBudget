from dataclasses import dataclass, field
from datetime import date
from models.transaction import Transaction
from models.category import Category
from models.ideal_month import IdealMonth
import models.transaction as tx_model
import models.category as cat_model
import models.stats as stats_model
import models.investment as inv_model
import models.ideal_month as im_model


@dataclass
class AppState:
    current_month: str = field(default_factory=lambda: date.today().strftime("%Y-%m"))
    transactions: list[Transaction] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    summary: dict = field(default_factory=lambda: {"income": 0.0, "expense": 0.0, "balance": 0.0})
    gdrive_linked: bool = False
    language: str = "en"
    investments: list = field(default_factory=list)
    investments_total: float = 0.0
    ideal_months: list[IdealMonth] = field(default_factory=list)

    def reload(self) -> None:
        self.transactions = tx_model.get_all(self.current_month)
        self.categories = cat_model.get_all()
        self.summary = stats_model.get_monthly_summary(self.current_month)
        self.investments = inv_model.get_all()
        self.investments_total = sum(inv.balance for inv in self.investments)
        self.ideal_months = im_model.get_all()

    def set_month(self, month: str) -> None:
        self.current_month = month
        self.reload()
