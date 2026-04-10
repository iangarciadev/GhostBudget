import flet as ft
from datetime import date
from state import AppState
from controllers.transaction_ctrl import add_transaction, remove_transaction
from i18n import t


def _fmt_amount(amount: float, type_: str) -> str:
    signal = "+" if type_ == "income" else "-"
    return f"{signal} R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _category_name(state: AppState, category_id: int | None) -> str:
    if category_id is None:
        return t("transactions.no_category")
    for c in state.categories:
        if c.id == category_id:
            return c.name
    return t("transactions.no_category")


def _category_color(state: AppState, category_id: int | None) -> str:
    if category_id is None:
        return "#607D8B"
    for c in state.categories:
        if c.id == category_id:
            return c.color
    return "#607D8B"


class TransactionsView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._build()

    def _build(self):
        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(t("transactions.title"), size=22, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            t("transactions.new"),
                            icon=ft.Icons.ADD,
                            on_click=self._open_form,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
            ),
            ft.Divider(height=1),
            *self._build_list(),
        ]

    def _build_list(self):
        if not self._state.transactions:
            return [
                ft.Container(
                    content=ft.Text(
                        t("transactions.empty"),
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.Alignment(0, 0),
                    padding=40,
                )
            ]

        items = []
        for tx in self._state.transactions:
            color = ft.Colors.GREEN_600 if tx.type == "income" else ft.Colors.RED_600
            cat_color = _category_color(self._state, tx.category_id)
            items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=4, height=48, bgcolor=cat_color, border_radius=2),
                            ft.Container(width=8),
                            ft.Column(
                                [
                                    ft.Text(
                                        tx.description or _category_name(self._state, tx.category_id),
                                        weight=ft.FontWeight.W_500,
                                        size=14,
                                    ),
                                    ft.Text(
                                        f"{tx.date}  ·  {_category_name(self._state, tx.category_id)}",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(
                                _fmt_amount(tx.amount, tx.type),
                                color=color,
                                weight=ft.FontWeight.BOLD,
                                size=15,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                tooltip=t("transactions.delete"),
                                data=tx.id,
                                on_click=self._delete,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=24, vertical=8),
                )
            )
            items.append(ft.Divider(height=1))
        return items

    def _delete(self, e):
        remove_transaction(self._state, e.control.data)
        self._on_change()

    def _open_form(self, e):
        _TransactionForm(self._page, self._state, self._on_change).open()

    def refresh(self):
        self._build()
        self.update()


class _TransactionForm:
    def __init__(self, page: ft.Page, state: AppState, on_change):
        self._page = page
        self._state = state
        self._on_change = on_change

        self._amount = ft.TextField(label=t("transactions.form.amount"), keyboard_type=ft.KeyboardType.NUMBER, width=200)
        self._desc = ft.TextField(label=t("transactions.form.desc"), expand=True)
        self._date_field = ft.TextField(
            label=t("transactions.form.date"), value=date.today().isoformat(), width=160,
            hint_text=t("transactions.form.date_hint"),
        )
        self._type_toggle = ft.SegmentedButton(
            selected={"expense"},
            segments=[
                ft.Segment(value="expense", label=ft.Text(t("transactions.form.type_expense"))),
                ft.Segment(value="income", label=ft.Text(t("transactions.form.type_income"))),
            ],
        )
        expense_cats = [c for c in state.categories if c.type in ("expense", "all")]
        income_cats  = [c for c in state.categories if c.type in ("income", "all")]

        self._category = ft.Dropdown(
            label=t("transactions.form.category"),
            options=[ft.dropdown.Option(key=str(c.id), text=c.name) for c in expense_cats],
            width=220,
        )

        def on_type_change(e):
            selected = list(self._type_toggle.selected)[0]
            if selected == "expense":
                cats = expense_cats
            else:
                cats = income_cats
            self._category.options = [ft.dropdown.Option(key=str(c.id), text=c.name) for c in cats]
            self._category.value = None
            self._category.update()

        self._type_toggle.on_change = on_type_change

        self._dlg = ft.AlertDialog(
            title=ft.Text(t("transactions.dialog.title")),
            content=ft.Column(
                [
                    self._type_toggle,
                    ft.Row([self._amount, self._date_field]),
                    ft.Row([self._category, self._desc]),
                ],
                tight=True,
                spacing=12,
                width=500,
            ),
            actions=[
                ft.TextButton(t("transactions.cancel"), on_click=lambda e: self._close()),
                ft.ElevatedButton(t("transactions.save"), on_click=self._save),
            ],
        )

    def open(self):
        self._page.open(self._dlg)

    def _close(self):
        self._page.close(self._dlg)

    def _save(self, e):
        try:
            amount = float(self._amount.value.replace(",", "."))
        except (ValueError, AttributeError):
            self._amount.error_text = t("transactions.invalid_amount")
            self._amount.update()
            return

        type_ = list(self._type_toggle.selected)[0]
        cat_id = int(self._category.value) if self._category.value else None
        desc = self._desc.value or ""
        date_ = self._date_field.value or date.today().isoformat()

        add_transaction(self._state, amount, type_, date_, cat_id, desc)
        self._close()
        self._on_change()
