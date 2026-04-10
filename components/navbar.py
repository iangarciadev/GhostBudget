import flet as ft
from i18n import t


class NavBar(ft.NavigationRail):
    ROUTES = ["/", "/transactions", "/categories", "/investments", "/ideal_months", "/settings"]

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
            leading=ft.Container(
                content=ft.Image(src="logo.png", width=48, height=48),
                padding=ft.padding.symmetric(vertical=12),
            ),
            destinations=self._build_destinations(),
        )

    def _build_destinations(self) -> list:
        return [
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label=t("nav.dashboard"),
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                selected_icon=ft.Icons.RECEIPT_LONG,
                label=t("nav.transactions"),
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LABEL_OUTLINED,
                selected_icon=ft.Icons.LABEL,
                label=t("nav.categories"),
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SHOW_CHART_OUTLINED,
                selected_icon=ft.Icons.SHOW_CHART,
                label=t("nav.investments"),
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TUNE_OUTLINED,
                selected_icon=ft.Icons.TUNE,
                label=t("nav.ideal_months"),
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label=t("nav.settings"),
            ),
        ]

    def refresh(self) -> None:
        """Rebuild destination labels with the current language."""
        self.destinations = self._build_destinations()
        self.update()

    def sync_route(self, route: str) -> None:
        self.selected_index = self._route_to_index(route)
        self.update()

    def _route_to_index(self, route: str) -> int:
        try:
            return self.ROUTES.index(route)
        except ValueError:
            return 0
