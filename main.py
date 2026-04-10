import flet as ft
from models.database import init_db
from state import AppState
from components.navbar import NavBar
from views.dashboard import DashboardView
from views.transactions import TransactionsView
from views.categories import CategoriesView
from views.settings import SettingsView


def main(page: ft.Page):
    page.title = "GhostBudget"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.window.width = 1000
    page.window.height = 660
    page.window.min_width = 700
    page.window.min_height = 500
    page.padding = 0

    init_db()
    state = AppState()
    state.reload()

    navbar = NavBar(page)
    content_area = ft.Column(expand=True)

    def on_data_change():
        """Chamado por qualquer view que altere dados — re-renderiza a view atual."""
        state.reload()
        render(page.route)

    def render(route: str):
        navbar.sync_route(route)
        content_area.controls.clear()

        match route:
            case "/":
                content_area.controls.append(
                    DashboardView(page, state, on_data_change)
                )
            case "/transactions":
                content_area.controls.append(
                    TransactionsView(page, state, on_data_change)
                )
            case "/categories":
                content_area.controls.append(
                    CategoriesView(page, state, on_data_change)
                )
            case "/settings":
                content_area.controls.append(
                    SettingsView(page, state, on_data_change)
                )
            case _:
                content_area.controls.append(
                    DashboardView(page, state, on_data_change)
                )

        content_area.update()

    def route_change(e: ft.RouteChangeEvent):
        render(e.route)

    page.on_route_change = route_change

    page.add(
        ft.Row(
            [
                navbar,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )

    page.go("/")


if __name__ == "__main__":
    ft.app(target=main)
