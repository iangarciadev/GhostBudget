import flet as ft
from state import AppState
import models.stats as stats_model
from i18n import t


def _fmt(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _summary_card(label: str, value: float, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(_fmt(value), size=22, weight=ft.FontWeight.BOLD, color=color),
            ],
            spacing=4,
        ),
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        expand=True,
    )


class DashboardView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=16)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._build()

    def _build(self):
        s = self._state.summary
        by_cat = stats_model.get_expense_by_category(self._state.current_month)
        trend = stats_model.get_monthly_trend(6)

        balance_color = ft.Colors.GREEN_600 if s["balance"] >= 0 else ft.Colors.RED_600

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            t("dashboard.title", month=self._state.current_month),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Row(
                            [
                                _summary_card(t("dashboard.income"), s["income"], ft.Colors.GREEN_600),
                                _summary_card(t("dashboard.expense"), s["expense"], ft.Colors.RED_600),
                                _summary_card(t("dashboard.balance"), s["balance"], balance_color),
                            ],
                            spacing=16,
                        ),
                    ],
                    spacing=16,
                ),
                padding=24,
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(t("dashboard.by_category"), size=16, weight=ft.FontWeight.W_600),
                        *self._build_category_bars(by_cat, s["expense"]),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(t("dashboard.trend"), size=16, weight=ft.FontWeight.W_600),
                        *self._build_trend(trend),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        ]

    def _build_category_bars(self, by_cat: list[dict], total_expense: float) -> list:
        if not by_cat:
            return [ft.Text(t("dashboard.no_expenses"), color=ft.Colors.ON_SURFACE_VARIANT)]
        max_val = max(c["total"] for c in by_cat)
        bars = []
        for cat in by_cat:
            pct = cat["total"] / max_val if max_val else 0
            bars.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(width=12, height=12, bgcolor=cat["color"], border_radius=2),
                                ft.Text(cat["name"], size=13, expand=True),
                                ft.Text(_fmt(cat["total"]), size=13, weight=ft.FontWeight.W_500),
                            ],
                            spacing=8,
                        ),
                        ft.Container(
                            content=ft.Container(
                                width=None,
                                bgcolor=cat["color"],
                                border_radius=4,
                            ),
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            border_radius=4,
                            height=10,
                            alignment=ft.alignment.Alignment(-1, 0),
                            expand=True,
                        ),
                    ],
                    spacing=4,
                )
            )
        return bars

    def _build_trend(self, trend: list[dict]) -> list:
        if not trend:
            return [ft.Text(t("dashboard.no_data"), color=ft.Colors.ON_SURFACE_VARIANT)]

        max_val = max(max(m["income"], m["expense"]) for m in trend) or 1
        bar_height = 100

        columns = []
        for m in trend:
            inc_h = int(m["income"] / max_val * bar_height)
            exp_h = int(m["expense"] / max_val * bar_height)
            columns.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    height=inc_h or 2, width=14,
                                    bgcolor=ft.Colors.GREEN_400, border_radius=ft.border_radius.vertical(top=3),
                                ),
                                ft.Container(
                                    height=exp_h or 2, width=14,
                                    bgcolor=ft.Colors.RED_400, border_radius=ft.border_radius.vertical(top=3),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            spacing=2,
                            height=bar_height,
                        ),
                        ft.Text(m["month"][5:], size=11, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            )

        legend = ft.Row(
            [
                ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN_400, border_radius=2),
                ft.Text(t("dashboard.type_income"), size=12),
                ft.Container(width=12, height=12, bgcolor=ft.Colors.RED_400, border_radius=2),
                ft.Text(t("dashboard.type_expense"), size=12),
            ],
            spacing=6,
        )

        return [
            ft.Row(columns, spacing=12, vertical_alignment=ft.CrossAxisAlignment.END),
            legend,
        ]

    def refresh(self):
        self._build()
        self.update()
