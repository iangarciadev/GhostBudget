import flet as ft
from state import AppState
from controllers.category_ctrl import add_category, edit_category, remove_category
from i18n import t


def _open_dialog(page, dlg):
    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _close_dialog(page, dlg):
    dlg.open = False
    page.update()

MATERIAL_ICONS = [
    "restaurant", "directions_car", "home", "health_and_safety",
    "sports_esports", "school", "more_horiz", "payments", "work",
    "attach_money", "shopping_cart", "local_gas_station", "flight",
    "fitness_center", "pets", "child_care", "coffee",
]

COLORS = [
    ("#FFE53935", "Vermelho"),  ("#FFFB8C00", "Laranja"),
    ("#FFF4511E", "Laranja-esc"), ("#FF8E24AA", "Roxo"),
    ("#FF1E88E5", "Azul"),      ("#FF00897B", "Verde-água"),
    ("#FF43A047", "Verde"),     ("#FF7CB342", "Verde-claro"),
    ("#FF00ACC1", "Ciano"),     ("#FF546E7A", "Cinza-azul"),
    ("#FFF06292", "Rosa"),      ("#FFFFB300", "Amarelo"),
]


def _to_icon(name: str) -> ft.Icons:
    try:
        return getattr(ft.Icons, name.upper())
    except AttributeError:
        return ft.Icons.MORE_HORIZ


def _to_color(hex_color: str) -> str:
    if hex_color.startswith("#") and len(hex_color) == 7:
        return "#FF" + hex_color[1:]
    return hex_color


def _type_options() -> list:
    return [
        ft.dropdown.Option(key="expense", text=t("categories.type.expense")),
        ft.dropdown.Option(key="income",  text=t("categories.type.income")),
        ft.dropdown.Option(key="all",     text=t("categories.type.both")),
    ]


def _section_header(label: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=12, weight=ft.FontWeight.W_600,
                        color=ft.Colors.ON_SURFACE_VARIANT),
        padding=ft.padding.only(left=24, top=16, bottom=4),
    )


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
                        ft.Text(t("categories.title"), size=22, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            t("categories.new"),
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
        groups = [
            ("expense", t("categories.type.expense")),
            ("income",  t("categories.type.income")),
            ("all",     t("categories.type.both")),
        ]
        all_cats = self._state.categories

        subs_by_parent: dict[int, list] = {}
        for c in all_cats:
            if c.parent_id is not None:
                subs_by_parent.setdefault(c.parent_id, []).append(c)

        items = []
        for type_key, section_label in groups:
            cats = [c for c in all_cats if c.type == type_key and c.parent_id is None]
            if not cats:
                continue
            items.append(_section_header(section_label))
            for cat in cats:
                subs = sorted(subs_by_parent.get(cat.id, []), key=lambda c: c.name)
                items.append(self._category_row(cat, sub_count=len(subs)))
                items.append(ft.Divider(height=1))
                for sub in subs:
                    items.append(self._subcategory_row(sub, cat))
                    items.append(ft.Divider(height=1))
        return items

    def _category_row(self, cat, sub_count: int = 0):
        name_parts = [ft.Text(cat.name, weight=ft.FontWeight.W_500, size=14)]
        if sub_count:
            name_parts.append(
                ft.Text(f"{sub_count} sub", size=11, color=ft.Colors.ON_SURFACE_VARIANT)
            )
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=36, height=36,
                        bgcolor=_to_color(cat.color),
                        border_radius=18,
                        content=ft.Icon(_to_icon(cat.icon), color=ft.Colors.WHITE, size=18),
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                    ft.Container(width=12),
                    ft.Row(name_parts, spacing=6, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip=t("categories.add_sub"),
                        data=cat,
                        on_click=self._add_sub,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip=t("categories.edit"),
                        data=cat,
                        on_click=self._edit,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip=t("categories.delete"),
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        data=cat.id,
                        on_click=self._delete,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=8),
        )

    def _subcategory_row(self, sub, parent_cat):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=24),
                    ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT, size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(width=4),
                    ft.Container(
                        width=28, height=28,
                        bgcolor=_to_color(parent_cat.color),
                        border_radius=14,
                        content=ft.Icon(_to_icon(parent_cat.icon), color=ft.Colors.WHITE, size=14),
                        alignment=ft.alignment.Alignment(0, 0),
                    ),
                    ft.Container(width=8),
                    ft.Text(sub.name, weight=ft.FontWeight.W_400, size=13, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip=t("categories.edit"),
                        data=sub,
                        on_click=self._edit,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip=t("categories.delete"),
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        data=sub.id,
                        on_click=self._delete,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=6),
        )

    def _add_sub(self, e):
        _CategoryForm(
            self._page, self._state, self._on_change, parent=e.control.data
        ).open()

    def _edit(self, e):
        _CategoryForm(self._page, self._state, self._on_change, existing=e.control.data).open()

    def _delete(self, e):
        remove_category(self._state, e.control.data)
        self._on_change()

    def refresh(self):
        self._build()
        self.update()


class _CategoryForm:
    """Form for creating/editing categories and subcategories.

    - No existing, no parent  → create top-level category (name + type + color + icon)
    - parent provided         → create subcategory under that parent (name only)
    - existing, no parent_id  → edit top-level category
    - existing with parent_id → edit subcategory (name only)
    """

    def __init__(self, page, state, on_change, existing=None, parent=None):
        self._page = page
        self._state = state
        self._on_change = on_change
        self._existing = existing

        # Resolve the parent category object
        if parent is not None:
            self._parent = parent
        elif existing and existing.parent_id:
            self._parent = next(
                (c for c in state.categories if c.id == existing.parent_id), None
            )
        else:
            self._parent = None

        is_sub = self._parent is not None

        self._name = ft.TextField(
            label=t("categories.form.name"),
            value=existing.name if existing else "",
            expand=True,
        )

        if is_sub:
            # Subcategory form: only name + info about parent
            title = (
                t("categories.dialog.edit_sub")
                if existing
                else t("categories.dialog.new_sub", parent=self._parent.name)
            )
            self._dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Column(
                    [
                        self._name,
                        ft.Row(
                            [
                                ft.Container(
                                    width=20, height=20,
                                    bgcolor=_to_color(self._parent.color),
                                    border_radius=10,
                                    content=ft.Icon(
                                        _to_icon(self._parent.icon),
                                        color=ft.Colors.WHITE,
                                        size=12,
                                    ),
                                    alignment=ft.alignment.Alignment(0, 0),
                                ),
                                ft.Text(
                                    t("categories.form.inherits_style",
                                      parent=self._parent.name),
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    tight=True,
                    spacing=12,
                    width=340,
                ),
                actions=[
                    ft.TextButton(t("categories.cancel"), on_click=lambda e: self._close()),
                    ft.ElevatedButton(t("categories.save"), on_click=self._save),
                ],
            )
        else:
            # Top-level category form: name + type + color + icon
            self._type = ft.Dropdown(
                label=t("categories.form.type"),
                options=_type_options(),
                width=160,
                value=existing.type if existing else "expense",
            )
            self._color = ft.Dropdown(
                label=t("categories.form.color"),
                options=[ft.dropdown.Option(key=c, text=lbl) for c, lbl in COLORS],
                value=existing.color if existing else COLORS[0][0],
                width=160,
            )
            self._icon = ft.Dropdown(
                label=t("categories.form.icon"),
                options=[ft.dropdown.Option(key=i, text=i) for i in MATERIAL_ICONS],
                value=existing.icon if existing else MATERIAL_ICONS[0],
                width=200,
            )
            title = t("categories.dialog.edit") if existing else t("categories.dialog.new")
            self._dlg = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Column(
                    [
                        ft.Row([self._name, self._type]),
                        ft.Row([self._color, self._icon]),
                    ],
                    tight=True,
                    spacing=12,
                    width=460,
                ),
                actions=[
                    ft.TextButton(t("categories.cancel"), on_click=lambda e: self._close()),
                    ft.ElevatedButton(t("categories.save"), on_click=self._save),
                ],
            )

    def open(self):
        _open_dialog(self._page, self._dlg)

    def _close(self):
        _close_dialog(self._page, self._dlg)

    def _save(self, e):
        name = self._name.value.strip()
        if not name:
            self._name.error_text = t("categories.error.name_required")
            self._name.update()
            return

        if self._parent:
            # Subcategory: inherit everything from parent
            color = self._parent.color
            icon = self._parent.icon
            type_ = self._parent.type
            parent_id = self._parent.id
        else:
            color = self._color.value or COLORS[0][0]
            icon = self._icon.value or MATERIAL_ICONS[0]
            type_ = self._type.value or "expense"
            parent_id = None

        if self._existing:
            edit_category(self._state, self._existing.id, name, color, icon, type_, parent_id)
        else:
            add_category(self._state, name, color, icon, type_, parent_id)

        self._close()
        self._on_change()
