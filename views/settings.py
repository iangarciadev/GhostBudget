import flet as ft
from state import AppState
import controllers.sync_ctrl as sync_ctrl


class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._status_text = ft.Text("", color=ft.Colors.GREEN_600)
        self._build()

    def _build(self):
        linked = sync_ctrl.is_linked()

        self.controls = [
            ft.Container(
                content=ft.Text("Configurações", size=22, weight=ft.FontWeight.BOLD),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Google Drive", size=16, weight=ft.FontWeight.W_600),
                        ft.Text(
                            "Sincronize seu banco de dados entre dispositivos usando o Google Drive.",
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            size=13,
                        ),
                        ft.Container(height=8),
                        ft.Row(
                            [
                                ft.Container(
                                    width=10, height=10,
                                    bgcolor=ft.Colors.GREEN_600 if linked else ft.Colors.GREY_400,
                                    border_radius=5,
                                ),
                                ft.Text(
                                    "Conta vinculada" if linked else "Nenhuma conta vinculada",
                                    size=13,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    "Vincular conta Google",
                                    icon=ft.Icons.LINK,
                                    on_click=self._link,
                                ),
                                ft.ElevatedButton(
                                    "Enviar backup",
                                    icon=ft.Icons.CLOUD_UPLOAD_OUTLINED,
                                    on_click=self._upload,
                                    disabled=not linked,
                                ),
                                ft.ElevatedButton(
                                    "Restaurar backup",
                                    icon=ft.Icons.CLOUD_DOWNLOAD_OUTLINED,
                                    on_click=self._download,
                                    disabled=not linked,
                                ),
                            ],
                            spacing=12,
                            wrap=True,
                        ),
                        ft.Container(height=8),
                        self._status_text,
                        ft.Container(height=4),
                        ft.Text(
                            "Para usar o Google Drive, coloque o arquivo credentials.json "
                            "(baixado do Google Cloud Console) na pasta raiz do GhostBudget.",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            italic=True,
                        ),
                    ],
                    spacing=6,
                ),
                padding=24,
            ),
        ]

    def _set_status(self, msg: str, error: bool = False):
        self._status_text.value = msg
        self._status_text.color = ft.Colors.RED_600 if error else ft.Colors.GREEN_600
        self._status_text.update()

    def _link(self, e):
        try:
            msg = sync_ctrl.link_account()
            self._set_status(msg)
            self._state.gdrive_linked = True
            self.refresh()
        except Exception as ex:
            self._set_status(str(ex), error=True)

    def _upload(self, e):
        try:
            msg = sync_ctrl.upload(self._state)
            self._set_status(msg)
        except Exception as ex:
            self._set_status(str(ex), error=True)

    def _download(self, e):
        try:
            msg = sync_ctrl.download(self._state)
            self._set_status(msg)
            self._on_change()
        except Exception as ex:
            self._set_status(str(ex), error=True)

    def refresh(self):
        self._build()
        self.update()
