import flet as ft


class NavBar(ft.NavigationRail):
    ROUTES = ["/", "/transactions", "/categories", "/settings"]

    def __init__(self, page: ft.Page):
        self._page = page

        def on_change(e):
            page.go(self.ROUTES[e.control.selected_index])

        super().__init__(
            selected_index=self._route_to_index(page.route),
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            on_change=on_change,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                    selected_icon=ft.Icons.RECEIPT_LONG,
                    label="Lançamentos",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LABEL_OUTLINED,
                    selected_icon=ft.Icons.LABEL,
                    label="Categorias",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Config",
                ),
            ],
        )

    def sync_route(self, route: str) -> None:
        self.selected_index = self._route_to_index(route)
        self.update()

    def _route_to_index(self, route: str) -> int:
        try:
            return self.ROUTES.index(route)
        except ValueError:
            return 0
