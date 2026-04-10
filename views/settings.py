import flet as ft
from state import AppState
import controllers.sync_ctrl as sync_ctrl
import i18n


class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change, on_lang_change):
        super().__init__(expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._on_lang_change = on_lang_change
        self._status_text = ft.Text("", color=ft.Colors.GREEN_600)
        self._lang_dropdown = ft.Dropdown(
            label=i18n.t("settings.language.label"),
            width=220,
            value=i18n.get_current_language(),
            options=[
                ft.dropdown.Option("en", i18n.t("lang.en")),
                ft.dropdown.Option("pt", i18n.t("lang.pt")),
            ],
        )
        self._lang_dropdown.on_change = self._change_language
        self._build()

    def _build(self):
        self._lang_dropdown.label = i18n.t("settings.language.label")
        self._lang_dropdown.value = i18n.get_current_language()
        self._lang_dropdown.options = [
            ft.dropdown.Option("en", i18n.t("lang.en")),
            ft.dropdown.Option("pt", i18n.t("lang.pt")),
        ]
        linked = sync_ctrl.is_linked()

        self.controls = [
            ft.Container(
                content=ft.Text(i18n.t("settings.title"), size=22, weight=ft.FontWeight.BOLD),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(i18n.t("settings.gdrive.section"), size=16, weight=ft.FontWeight.W_600),
                        ft.Text(
                            i18n.t("settings.gdrive.description"),
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
                                    i18n.t("settings.gdrive.linked") if linked else i18n.t("settings.gdrive.not_linked"),
                                    size=13,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                ft.OutlinedButton(
                                    i18n.t("settings.gdrive.link_btn"),
                                    icon=ft.Icons.LINK,
                                    on_click=self._link,
                                ),
                                ft.ElevatedButton(
                                    i18n.t("settings.gdrive.upload_btn"),
                                    icon=ft.Icons.CLOUD_UPLOAD_OUTLINED,
                                    on_click=self._upload,
                                    disabled=not linked,
                                ),
                                ft.ElevatedButton(
                                    i18n.t("settings.gdrive.restore_btn"),
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
                            i18n.t("settings.gdrive.hint"),
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            italic=True,
                        ),
                    ],
                    spacing=6,
                ),
                padding=24,
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(i18n.t("settings.language.section"), size=16, weight=ft.FontWeight.W_600),
                        ft.Container(height=4),
                        self._lang_dropdown,
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

    def _change_language(self, e):
        i18n.load_language(e.control.value)
        self._on_lang_change()
        self.refresh()

    def refresh(self):
        self._build()
        self.update()
