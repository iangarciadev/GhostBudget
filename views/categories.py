import flet as ft
from state import AppState
from controllers.category_ctrl import add_category, edit_category, remove_category

MATERIAL_ICONS = [
    "restaurant", "directions_car", "home", "health_and_safety",
    "sports_esports", "school", "more_horiz", "payments", "work",
    "attach_money", "shopping_cart", "local_gas_station", "flight",
    "fitness_center", "pets", "child_care", "coffee",
]

COLORS = [
    ("#E53935", "Vermelho"),  ("#FB8C00", "Laranja"),
    ("#F4511E", "Laranja-esc"), ("#8E24AA", "Roxo"),
    ("#1E88E5", "Azul"),      ("#00897B", "Verde-água"),
    ("#43A047", "Verde"),     ("#7CB342", "Verde-claro"),
    ("#00ACC1", "Ciano"),     ("#546E7A", "Cinza-azul"),
    ("#F06292", "Rosa"),      ("#FFB300", "Amarelo"),
]

TYPE_OPTIONS = [
    ft.dropdown.Option(key="expense", text="Despesa"),
    ft.dropdown.Option(key="income",  text="Receita"),
    ft.dropdown.Option(key="all",     text="Ambos"),
]

TYPE_LABEL = {"expense": "Despesa", "income": "Receita", "all": "Ambos"}


class CategoriesView(ft.Column):
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
                        ft.Text("Categorias", size=22, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Nova categoria",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: _CategoryForm(
                                self._page, self._state, self._on_change
                            ).open(),
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
        items = []
        for cat in self._state.categories:
            items.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=36, height=36,
                                bgcolor=cat.color,
                                border_radius=18,
                                content=ft.Icon(cat.icon, color=ft.Colors.WHITE, size=18),
                                alignment=ft.alignment.Alignment(0, 0),
                            ),
                            ft.Container(width=12),
                            ft.Column(
                                [
                                    ft.Text(cat.name, weight=ft.FontWeight.W_500, size=14),
                                    ft.Text(
                                        TYPE_LABEL.get(cat.type, cat.type),
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                data=cat,
                                on_click=self._edit,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Excluir",
                                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                                data=cat.id,
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

    def _edit(self, e):
        _CategoryForm(self._page, self._state, self._on_change, existing=e.control.data).open()

    def _delete(self, e):
        remove_category(self._state, e.control.data)
        self._on_change()

    def refresh(self):
        self._build()
        self.update()


class _CategoryForm:
    def __init__(self, page, state, on_change, existing=None):
        self._page = page
        self._state = state
        self._on_change = on_change
        self._existing = existing

        self._name = ft.TextField(
            label="Nome", value=existing.name if existing else "", expand=True
        )
        self._type = ft.Dropdown(
            label="Tipo", options=TYPE_OPTIONS, width=160,
            value=existing.type if existing else "expense",
        )
        self._color = ft.Dropdown(
            label="Cor",
            options=[ft.dropdown.Option(key=c, text=lbl) for c, lbl in COLORS],
            value=existing.color if existing else COLORS[0][0],
            width=160,
        )
        self._icon = ft.Dropdown(
            label="Ícone",
            options=[ft.dropdown.Option(key=i, text=i) for i in MATERIAL_ICONS],
            value=existing.icon if existing else MATERIAL_ICONS[0],
            width=200,
        )

        title = "Editar categoria" if existing else "Nova categoria"
        self._dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(
                [
                    ft.Row([self._name, self._type]),
                    ft.Row([self._color, self._icon]),
                ],
                tight=True, spacing=12, width=460,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._close()),
                ft.ElevatedButton("Salvar", on_click=self._save),
            ],
        )

    def open(self):
        self._page.open(self._dlg)

    def _close(self):
        self._page.close(self._dlg)

    def _save(self, e):
        name = self._name.value.strip()
        if not name:
            self._name.error_text = "Informe um nome"
            self._name.update()
            return

        color = self._color.value or COLORS[0][0]
        icon = self._icon.value or MATERIAL_ICONS[0]
        type_ = self._type.value or "expense"

        if self._existing:
            edit_category(self._state, self._existing.id, name, color, icon, type_)
        else:
            add_category(self._state, name, color, icon, type_)

        self._close()
        self._on_change()
