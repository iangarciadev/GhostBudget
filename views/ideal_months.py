from datetime import date
import flet as ft
from state import AppState
import models.ideal_month as im_model
from controllers.ideal_month_ctrl import (
    add_ideal_month,
    edit_ideal_month,
    remove_ideal_month,
    save_items,
)
from i18n import t


def _fmt(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _open_dialog(page, dlg):
    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _close_dialog(page, dlg):
    dlg.open = False
    page.update()


def _last_months(n: int = 13) -> list[str]:
    today = date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return months


class IdealMonthsView(ft.Column):
    def __init__(self, page: ft.Page, state: AppState, on_change):
        super().__init__(expand=True, spacing=0)
        self._page = page
        self._state = state
        self._on_change = on_change
        self._selected_id: int | None = None
        self._comparison_month: str = state.current_month
        self._build()

    # ── internal refresh (keeps selection) ───────────────────────────────────
    def _refresh(self):
        self._state.reload()
        self._build()
        self.update()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # keep selection valid after reload
        ids = {m.id for m in self._state.ideal_months}
        if self._selected_id not in ids:
            self._selected_id = None

        self.controls = [
            # header
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            t("ideal_month.title"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.ElevatedButton(
                            t("ideal_month.new"),
                            icon=ft.Icons.ADD,
                            on_click=lambda e: _TemplateForm(
                                self._page, self._state, self._refresh
                            ).open(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
            ),
            ft.Divider(height=1),
            # body: left list + right panel
            ft.Row(
                [
                    self._build_left_panel(),
                    ft.VerticalDivider(width=1),
                    self._build_right_panel(),
                ],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ]

    # ── left panel ────────────────────────────────────────────────────────────
    def _build_left_panel(self) -> ft.Container:
        items = []

        if not self._state.ideal_months:
            items.append(
                ft.Container(
                    content=ft.Text(
                        t("ideal_month.empty_list"),
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        size=13,
                    ),
                    padding=ft.padding.all(16),
                )
            )
        else:
            for m in self._state.ideal_months:
                is_selected = m.id == self._selected_id
                items.append(self._build_template_row(m, is_selected))
                items.append(ft.Divider(height=1))

        return ft.Container(
            width=270,
            content=ft.Column(
                items,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

    def _build_template_row(self, m, is_selected: bool) -> ft.Container:
        def on_select(e, mid=m.id):
            self._selected_id = mid
            self._build()
            self.update()

        return ft.Container(
            bgcolor=(
                ft.Colors.SURFACE_CONTAINER if is_selected else ft.Colors.TRANSPARENT
            ),
            content=ft.Row(
                [
                    ft.GestureDetector(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        m.name,
                                        weight=ft.FontWeight.W_500,
                                        size=14,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        m.description or "",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                spacing=2,
                                tight=True,
                            ),
                            expand=True,
                        ),
                        on_tap=on_select,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip=t("ideal_month.edit"),
                        icon_size=18,
                        data=m,
                        on_click=self._open_edit,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LIST_OUTLINED,
                        tooltip=t("ideal_month.edit_items"),
                        icon_size=18,
                        data=m,
                        on_click=self._open_items,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip=t("ideal_month.delete"),
                        icon_color=ft.Colors.ON_SURFACE_VARIANT,
                        icon_size=18,
                        data=m.id,
                        on_click=self._delete,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.only(left=16, top=8, bottom=8, right=4),
        )

    # ── right panel ───────────────────────────────────────────────────────────
    def _build_right_panel(self) -> ft.Container:
        if self._selected_id is None:
            return ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.TUNE,
                            size=48,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            t("ideal_month.select_prompt"),
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    spacing=12,
                ),
                alignment=ft.alignment.Alignment(0, 0),
            )

        template = next(
            (m for m in self._state.ideal_months if m.id == self._selected_id), None
        )
        if template is None:
            return ft.Container(expand=True)

        rows = im_model.get_comparison(self._selected_id, self._comparison_month)

        month_options = [
            ft.dropdown.Option(key=mo, text=mo) for mo in _last_months(13)
        ]
        if self._comparison_month not in [o.key for o in month_options]:
            self._comparison_month = _last_months(1)[0]

        def on_month_change(e):
            self._comparison_month = e.control.value
            self._build()
            self.update()

        month_dd = ft.Dropdown(
            value=self._comparison_month,
            options=month_options,
            width=140,
            dense=True,
        )
        month_dd.on_change = on_month_change

        income_rows = [r for r in rows if r["type"] == "income"]
        expense_rows = [r for r in rows if r["type"] == "expense"]

        body_controls = []

        if income_rows:
            body_controls.append(
                _section_header(t("ideal_month.section_income"), ft.Colors.GREEN_400)
            )
            for r in income_rows:
                body_controls.append(_comparison_row(r))

        if expense_rows:
            body_controls.append(
                _section_header(t("ideal_month.section_expense"), ft.Colors.RED_400)
            )
            for r in expense_rows:
                body_controls.append(_comparison_row(r))

        if not rows:
            body_controls.append(
                ft.Container(
                    content=ft.Text(
                        t("ideal_month.no_items"),
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    padding=ft.padding.all(24),
                )
            )

        return ft.Container(
            expand=True,
            content=ft.Column(
                [
                    # comparison header
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    template.name,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                                ft.Text(
                                    t("ideal_month.compare_with"),
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    size=13,
                                ),
                                month_dd,
                                ft.IconButton(
                                    icon=ft.Icons.LIST_OUTLINED,
                                    tooltip=t("ideal_month.edit_items"),
                                    data=template,
                                    on_click=self._open_items,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    ),
                    ft.Divider(height=1),
                    ft.Column(
                        body_controls,
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        )

    # ── event handlers ────────────────────────────────────────────────────────
    def _open_edit(self, e):
        _TemplateForm(
            self._page, self._state, self._refresh, existing=e.control.data
        ).open()

    def _open_items(self, e):
        template = e.control.data
        _ItemsForm(self._page, self._state, self._refresh, template).open()

    def _delete(self, e):
        remove_ideal_month(self._state, e.control.data)
        self._refresh()


# ── helper widgets ────────────────────────────────────────────────────────────

def _section_header(label: str, color) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            label.upper(),
            size=11,
            weight=ft.FontWeight.BOLD,
            color=color,
        ),
        padding=ft.padding.only(left=20, top=16, bottom=6),
    )


def _comparison_row(r: dict) -> ft.Container:
    cat_name = r["category_name"] or t("ideal_month.deleted_category")
    color = r["category_color"]
    target = r["target"]
    actual = r["actual"]
    diff = r["diff"]
    is_expense = r["type"] == "expense"

    # progress bar fill ratio clamped [0, 1]
    ratio = min(actual / target, 1.0) if target > 0 else (1.0 if actual > 0 else 0.0)
    over_budget = (is_expense and diff > 0) or (not is_expense and diff < 0)
    bar_color = ft.Colors.RED_400 if over_budget else color

    # diff badge
    if abs(diff) < 0.005:
        badge = None
    elif (is_expense and diff > 0) or (not is_expense and diff < 0):
        badge = ft.Container(
            content=ft.Text(
                f"▲ {_fmt(abs(diff))}",
                size=11,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=ft.Colors.RED_700,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )
    else:
        badge = ft.Container(
            content=ft.Text(
                f"▼ {_fmt(abs(diff))}",
                size=11,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=ft.Colors.GREEN_700,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )

    progress_bar = ft.Container(
        content=ft.Stack(
            [
                # background
                ft.Container(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=3,
                    height=6,
                    expand=True,
                ),
                # fill
                ft.Container(
                    bgcolor=bar_color,
                    border_radius=3,
                    height=6,
                    width=None,
                    expand=ratio,
                ),
            ],
            expand=True,
        ),
        height=6,
        expand=True,
        padding=ft.padding.symmetric(vertical=0),
    )

    amounts_row = ft.Row(
        [
            ft.Text(
                t("ideal_month.target") + ": " + _fmt(target),
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT,
                expand=True,
            ),
            ft.Text(
                t("ideal_month.actual") + ": " + _fmt(actual),
                size=12,
                weight=ft.FontWeight.W_500,
            ),
        ],
        spacing=8,
    )

    row_content = ft.Row(
        [
            # color dot
            ft.Container(
                width=10,
                height=10,
                bgcolor=color,
                border_radius=5,
            ),
            ft.Container(width=8),
            # main content
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                cat_name,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                expand=True,
                            ),
                            *([] if badge is None else [badge]),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    amounts_row,
                    progress_bar,
                ],
                spacing=4,
                expand=True,
                tight=True,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=row_content,
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
    )


# ── dialogs ───────────────────────────────────────────────────────────────────

class _TemplateForm:
    def __init__(self, page, state, refresh, existing=None):
        self._page = page
        self._state = state
        self._refresh = refresh
        self._existing = existing

        self._name = ft.TextField(
            label=t("ideal_month.form.name"),
            value=existing.name if existing else "",
            expand=True,
            autofocus=True,
        )
        self._desc = ft.TextField(
            label=t("ideal_month.form.description"),
            value=existing.description if existing else "",
            expand=True,
        )

        title = (
            t("ideal_month.dialog.edit") if existing else t("ideal_month.dialog.new")
        )
        self._dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(
                [self._name, self._desc],
                tight=True,
                spacing=12,
                width=400,
            ),
            actions=[
                ft.TextButton(t("ideal_month.cancel"), on_click=lambda e: self._close()),
                ft.ElevatedButton(t("ideal_month.save"), on_click=self._save),
            ],
        )

    def open(self):
        _open_dialog(self._page, self._dlg)

    def _close(self):
        _close_dialog(self._page, self._dlg)

    def _save(self, e):
        name = self._name.value.strip()
        if not name:
            self._name.error_text = t("ideal_month.error.name_required")
            self._name.update()
            return

        try:
            if self._existing:
                edit_ideal_month(self._state, self._existing.id, name, self._desc.value.strip())
            else:
                add_ideal_month(self._state, name, self._desc.value.strip())
        except ValueError:
            self._name.error_text = t("ideal_month.error.name_exists")
            self._name.update()
            return

        self._close()
        self._refresh()


class _ItemsForm:
    def __init__(self, page, state, refresh, template):
        self._page = page
        self._state = state
        self._refresh = refresh
        self._template = template

        existing = im_model.get_items(template.id)
        self._items: list[dict] = [
            {
                "category_id": it.category_id,
                "amount": it.amount,
                "type": it.type,
            }
            for it in existing
        ]

        self._dlg = ft.AlertDialog(
            title=ft.Text(t("ideal_month.dialog.items", name=template.name)),
            content=self._build_content(),
            actions=[
                ft.TextButton(t("ideal_month.cancel"), on_click=lambda e: self._close()),
                ft.ElevatedButton(t("ideal_month.save"), on_click=self._save),
            ],
            scrollable=True,
        )

    def open(self):
        _open_dialog(self._page, self._dlg)

    def _close(self):
        _close_dialog(self._page, self._dlg)

    def _build_content(self) -> ft.Column:
        income_rows = [i for i in self._items if i["type"] == "income"]
        expense_rows = [i for i in self._items if i["type"] == "expense"]

        income_cats = [
            ft.dropdown.Option(key=str(c.id), text=c.name)
            for c in self._state.categories
            if c.type in ("income", "all")
        ]
        expense_cats = [
            ft.dropdown.Option(key=str(c.id), text=c.name)
            for c in self._state.categories
            if c.type in ("expense", "all")
        ]

        controls = []

        # Income section
        controls.append(
            ft.Container(
                content=ft.Text(
                    t("ideal_month.section_income").upper(),
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREEN_400,
                ),
                padding=ft.padding.only(bottom=6, top=4),
            )
        )
        for idx, item in enumerate(income_rows):
            controls.append(
                self._build_item_row(item, idx, income_cats, "income")
            )
        controls.append(self._build_add_row(income_cats, "income"))

        controls.append(ft.Divider(height=16))

        # Expense section
        controls.append(
            ft.Container(
                content=ft.Text(
                    t("ideal_month.section_expense").upper(),
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_400,
                ),
                padding=ft.padding.only(bottom=6, top=4),
            )
        )
        for idx, item in enumerate(expense_rows):
            controls.append(
                self._build_item_row(item, idx, expense_cats, "expense")
            )
        controls.append(self._build_add_row(expense_cats, "expense"))

        return ft.Column(controls, spacing=6, tight=True, width=480)

    def _build_item_row(self, item: dict, idx: int, cat_options, type_: str) -> ft.Row:
        all_items_of_type = [i for i in self._items if i["type"] == type_]
        real_idx = self._items.index(item)

        cat_dd = ft.Dropdown(
            options=cat_options,
            value=str(item["category_id"]) if item["category_id"] is not None else None,
            label=t("ideal_month.items.category"),
            width=200,
            dense=True,
        )
        cat_dd.on_change = lambda e, ri=real_idx: self._update_category(ri, e.control.value)
        amt_field = ft.TextField(
            value=f"{item['amount']:.2f}",
            label=t("ideal_month.items.amount"),
            width=130,
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        amt_field.on_change = lambda e, ri=real_idx: self._update_amount(ri, e.control.value)
        del_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            icon_size=18,
            data=real_idx,
            on_click=self._delete_item,
        )
        return ft.Row([cat_dd, amt_field, del_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _build_add_row(self, cat_options, type_: str) -> ft.Row:
        cat_dd = ft.Ref[ft.Dropdown]()
        amt_field = ft.Ref[ft.TextField]()

        def on_add(e):
            cat_val = cat_dd.current.value
            amt_val = amt_field.current.value.strip()
            try:
                amount = float(amt_val.replace(",", "."))
                if amount <= 0:
                    raise ValueError
            except (ValueError, AttributeError):
                amt_field.current.error_text = t("ideal_month.error.invalid_amount")
                amt_field.current.update()
                return
            self._items.append({
                "category_id": int(cat_val) if cat_val else None,
                "amount": amount,
                "type": type_,
            })
            self._rerender()

        return ft.Row(
            [
                ft.Dropdown(
                    ref=cat_dd,
                    options=cat_options,
                    label=t("ideal_month.items.category"),
                    width=200,
                    dense=True,
                ),
                ft.TextField(
                    ref=amt_field,
                    label=t("ideal_month.items.amount"),
                    width=130,
                    dense=True,
                    keyboard_type=ft.KeyboardType.NUMBER,
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=ft.Colors.TEAL_400,
                    icon_size=20,
                    tooltip=(
                        t("ideal_month.items.add_income")
                        if type_ == "income"
                        else t("ideal_month.items.add_expense")
                    ),
                    on_click=on_add,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _update_category(self, real_idx: int, value: str | None):
        self._items[real_idx]["category_id"] = int(value) if value else None

    def _update_amount(self, real_idx: int, value: str):
        try:
            self._items[real_idx]["amount"] = float(value.replace(",", "."))
        except (ValueError, AttributeError):
            pass

    def _delete_item(self, e):
        idx = e.control.data
        if 0 <= idx < len(self._items):
            self._items.pop(idx)
        self._rerender()

    def _rerender(self):
        self._dlg.content = self._build_content()
        self._dlg.update()

    def _save(self, e):
        valid_items = [
            i for i in self._items if i.get("amount", 0) > 0
        ]
        save_items(self._state, self._template.id, valid_items)
        self._close()
        self._refresh()
