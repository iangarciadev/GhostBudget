import flet as ft
from datetime import date
from state import AppState
from controllers.investment_ctrl import (
    add_investment, edit_investment, remove_investment, deposit, withdraw
)
from i18n import t

INVEST_COLORS = [
    ("#FF009688", "Teal"),
    ("#FF2196F3", "Azul"),
    ("#FF4CAF50", "Verde"),
    ("#FFFFC107", "Amarelo"),
    ("#FFFF9800", "Laranja"),
    ("#FFF44336", "Vermelho"),
    ("#FFE91E63", "Rosa"),
    ("#FF9C27B0", "Roxo"),
    ("#FF3F51B5", "Índigo"),
    ("#FF00BCD4", "Ciano"),
    ("#FF8BC34A", "Verde-claro"),
    ("#FF795548", "Marrom"),
]


def _to_color(hex_color: str) -> str:
    """Ensure color has 8-digit ARGB hex format required by Flet 0.84."""
    if hex_color.startswith("#") and len(hex_color) == 7:
        return "#FF" + hex_color[1:]
    return hex_color


def _fmt(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class InvestmentsView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._build()

    def _build(self):
        self.controls = [
            self._build_header(),
            ft.Divider(height=1),
            self._build_summary(),
            ft.Divider(height=1),
            *self._build_list(),
        ]

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(t("investments.title"), size=22, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        t("investments.new"),
                        icon=ft.Icons.ADD,
                        on_click=lambda e: _InvestmentForm(
                            self._page, self._state, self._on_change
                        ).open(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
        )

    def _build_summary(self):
        total = self._state.investments_total
        count = len(self._state.investments)

        total_col = ft.Column(
            [
                ft.Text(
                    t("investments.total_invested"),
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text(
                    _fmt(total),
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.TEAL_400,
                ),
                ft.Text(
                    t("investments.count", count=count),
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
            spacing=4,
            expand=True,
        )

        chart = self._build_chart()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [total_col],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    chart,
                ],
                spacing=16,
            ),
            padding=24,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            margin=ft.margin.symmetric(horizontal=24, vertical=12),
            border_radius=12,
        )

    def _build_chart(self) -> ft.Control:
        total = self._state.investments_total
        investments = self._state.investments

        if not total or not investments:
            return ft.Container(
                content=ft.Text(
                    t("investments.empty"),
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                padding=ft.padding.only(top=4),
            )

        bar = ft.Row(
            [
                ft.Container(
                    bgcolor=_to_color(inv.color),
                    border_radius=4,
                    expand=max(1, round((inv.balance / total) * 1000)),
                    height=22,
                    tooltip=f"{inv.name}: {inv.balance / total * 100:.1f}%",
                )
                for inv in investments
            ],
            spacing=3,
        )

        legend = ft.Row(
            [
                ft.Row(
                    [
                        ft.Container(
                            width=10, height=10,
                            bgcolor=_to_color(inv.color),
                            border_radius=2,
                        ),
                        ft.Text(
                            f"{inv.name}  {inv.balance / total * 100:.1f}%",
                            size=12,
                        ),
                    ],
                    spacing=6,
                )
                for inv in investments
            ],
            wrap=True,
            spacing=12,
            run_spacing=6,
        )

        return ft.Column([bar, legend], spacing=10)

    def _build_list(self):
        if not self._state.investments:
            return [
                ft.Container(
                    content=ft.Text(
                        t("investments.empty"),
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.Alignment(0, 0),
                    padding=40,
                )
            ]

        items = []
        for inv in self._state.investments:
            items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=36, height=36,
                                bgcolor=_to_color(inv.color),
                                border_radius=18,
                                content=ft.Icon(
                                    ft.Icons.TRENDING_UP,
                                    color=ft.Colors.WHITE,
                                    size=18,
                                ),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            ft.Container(width=12),
                            ft.Column(
                                [
                                    ft.Text(inv.name, weight=ft.FontWeight.W_500, size=14),
                                    ft.Text(
                                        _fmt(inv.balance),
                                        size=13,
                                        color=ft.Colors.TEAL_300,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                tooltip=t("investments.deposit"),
                                data=inv,
                                on_click=self._open_deposit,
                                icon_color=ft.Colors.GREEN_400,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                tooltip=t("investments.withdraw"),
                                data=inv,
                                on_click=self._open_withdraw,
                                icon_color=ft.Colors.ORANGE_400,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip=t("investments.edit"),
                                data=inv,
                                on_click=self._edit,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip=t("investments.delete"),
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                data=inv.id,
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

    def _open_deposit(self, e):
        _OperationForm(
            self._page, self._state, self._on_change, e.control.data, "deposit"
        ).open()

    def _open_withdraw(self, e):
        _OperationForm(
            self._page, self._state, self._on_change, e.control.data, "withdrawal"
        ).open()

    def _edit(self, e):
        _InvestmentForm(
            self._page, self._state, self._on_change, existing=e.control.data
        ).open()

    def _delete(self, e):
        remove_investment(self._state, e.control.data)
        self._on_change()

    def refresh(self):
        self._build()
        self.update()


def _open_dialog(page, dlg):
    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _close_dialog(page, dlg):
    dlg.open = False
    page.update()


class _InvestmentForm:
    def __init__(self, page, state, on_change, existing=None):
        self._page = page
        self._state = state
        self._on_change = on_change
        self._existing = existing

        self._name = ft.TextField(
            label=t("investments.form.name"),
            value=existing.name if existing else "",
            expand=True,
        )
        self._color = ft.Dropdown(
            label=t("investments.form.color"),
            options=[ft.dropdown.Option(key=c, text=lbl) for c, lbl in INVEST_COLORS],
            value=existing.color if existing else INVEST_COLORS[0][0],
            width=160,
        )

        title = t("investments.dialog.edit") if existing else t("investments.dialog.new")
        self._dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(
                [ft.Row([self._name, self._color])],
                tight=True,
                spacing=12,
                width=440,
            ),
            actions=[
                ft.TextButton(t("investments.cancel"), on_click=lambda e: self._close()),
                ft.ElevatedButton(t("investments.save"), on_click=self._save),
            ],
        )

    def open(self):
        _open_dialog(self._page, self._dlg)

    def _close(self):
        _close_dialog(self._page, self._dlg)

    def _save(self, e):
        name = self._name.value.strip()
        if not name:
            self._name.error_text = t("investments.error.name_required")
            self._name.update()
            return

        color = self._color.value or INVEST_COLORS[0][0]

        if self._existing:
            edit_investment(self._state, self._existing.id, name, color)
        else:
            add_investment(self._state, name, color)

        self._close()
        self._on_change()


class _OperationForm:
    def __init__(self, page, state, on_change, investment, operation="deposit"):
        self._page = page
        self._state = state
        self._on_change = on_change
        self._investment = investment
        self._operation = operation

        self._amount = ft.TextField(
            label=t("investments.form.amount"),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=180,
        )
        self._date_field = ft.TextField(
            label=t("investments.form.date"),
            value=date.today().isoformat(),
            width=160,
            hint_text="YYYY-MM-DD",
        )
        self._note = ft.TextField(
            label=t("investments.form.note"),
            expand=True,
        )
        self._error = ft.Text("", color=ft.Colors.RED_600, size=12)

        op_label = (
            t("investments.deposit")
            if operation == "deposit"
            else t("investments.withdraw")
        )
        self._dlg = ft.AlertDialog(
            title=ft.Text(f"{op_label} — {investment.name}"),
            content=ft.Column(
                [
                    ft.Row([self._amount, self._date_field]),
                    self._note,
                    self._error,
                ],
                tight=True,
                spacing=12,
                width=440,
            ),
            actions=[
                ft.TextButton(t("investments.cancel"), on_click=lambda e: self._close()),
                ft.ElevatedButton(op_label, on_click=self._save),
            ],
        )

    def open(self):
        _open_dialog(self._page, self._dlg)

    def _close(self):
        _close_dialog(self._page, self._dlg)

    def _save(self, e):
        try:
            amount = float(self._amount.value.replace(",", "."))
            if amount <= 0:
                raise ValueError
        except (ValueError, AttributeError, TypeError):
            self._amount.error_text = t("investments.error.invalid_amount")
            self._amount.update()
            return

        date_ = self._date_field.value or date.today().isoformat()
        note = self._note.value or ""

        try:
            if self._operation == "deposit":
                deposit(self._state, self._investment.id, amount, date_, note)
            else:
                withdraw(self._state, self._investment.id, amount, date_, note)
        except ValueError:
            self._error.value = t("investments.error.insufficient_balance")
            self._error.update()
            return

        self._close()
        self._on_change()
