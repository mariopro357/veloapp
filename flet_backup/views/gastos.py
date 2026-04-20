"""
VeloApp — Opción 2: Gastos Mensuales
Registro de gastos por categoría, total del mes, auto-reset mensual
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, BLACK_STRIP, MONTH_NAMES, DAYS_ES,
    EXPENSE_CATEGORIES, section_title, sub_text,
    show_snack, empty_state, velo_card
)


def build_gastos_view(page: ft.Page) -> ft.Container:

    now = datetime.now()
    month_name = MONTH_NAMES[now.month]

    # ── Controles ──────────────────────────────────────────
    total_text = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=RED)
    total_label = ft.Text(f"Gastos de {month_name}", size=13, color=TEXT_SEC)
    gastos_list = ft.ListView(spacing=4, padding=0)
    selected_cat = [EXPENSE_CATEGORIES[0]]

    cat_dropdown = ft.Dropdown(
        label="Categoría",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT,
        focused_border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        options=[ft.dropdown.Option(c) for c in EXPENSE_CATEGORIES],
        value=EXPENSE_CATEGORIES[0],
        expand=True,
    )

    desc_field = ft.TextField(
        label="Descripción (opcional)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT,
        focused_border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        expand=True,
    )

    monto_field = ft.TextField(
        label="Monto $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT,
        focused_border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=130,
    )

    # ── Cargar lista ───────────────────────────────────────
    def load_list():
        gastos_list.controls.clear()
        gastos = db.get_gastos_mes()
        total = db.get_total_gastos_mes()
        total_text.value = f"${total:,.2f}"
        total_label.value = f"Gastos de {month_name}"

        if not gastos:
            gastos_list.controls.append(
                ft.Container(
                    content=empty_state("Sin gastos este mes 🎉", ft.Icons.SAVINGS),
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for g in gastos:
                def del_cb(e, gid=g["id"]):
                    db.delete_gasto(gid)
                    load_list()
                    page.update()

                gastos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(g["categoria"][:20], size=12,
                                    color=TEXT_SEC, expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Column([
                                ft.Text(g.get("descripcion", "") or "",
                                        size=11, color=TEXT_SEC,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(g["fecha"], size=10, color=TEXT_SEC),
                            ], spacing=2, expand=True),
                            ft.Text(f"${g['monto']:,.2f}", size=14,
                                    color=RED, weight=ft.FontWeight.BOLD,
                                    width=80, text_align=ft.TextAlign.RIGHT),
                            ft.IconButton(icon=ft.Icons.CLOSE, icon_color=RED,
                                          icon_size=16, on_click=del_cb),
                        ], spacing=6, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=NAVY_MID,
                        border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                        margin=ft.Margin.only(bottom=4),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.10, RED)),
                    )
                )

    # ── Agregar gasto ──────────────────────────────────────
    def add_gasto(e):
        cat = cat_dropdown.value
        desc = desc_field.value.strip()
        monto_str = monto_field.value.strip().replace(",", ".")
        if not monto_str:
            show_snack(page, "Ingresa el monto del gasto", RED)
            return
        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            show_snack(page, "Monto inválido", RED)
            return

        db.save_gasto(cat, desc, monto)
        desc_field.value = ""
        monto_field.value = ""
        show_snack(page, f"✅ Gasto de ${monto:,.2f} registrado", GREEN)
        load_list()
        page.update()

    # ── FAB ────────────────────────────────────────────────
    form_visible = [False]
    form_section = ft.AnimatedSwitcher(
        content=ft.Container(height=0),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
    )

    def toggle_form(e=None):
        form_visible[0] = not form_visible[0]
        if form_visible[0]:
            form_section.content = ft.Container(
                content=ft.Column([
                    ft.Text("Nuevo gasto", size=14,
                            weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    cat_dropdown,
                    desc_field,
                    ft.Row([
                        monto_field,
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Agregar",
                            on_click=add_gasto,
                            bgcolor=ACCENT,
                            color=TEXT_WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                    ], spacing=8),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.07, ACCENT),
                border_radius=14,
                padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ACCENT)),
            )
        else:
            form_section.content = ft.Container(height=0)
        page.update()

    add_btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ACCENT,
        foreground_color=TEXT_WHITE,
        on_click=toggle_form,
        mini=True,
    )

    # ── Totales por categoría ──────────────────────────────
    def build_summary():
        gastos = db.get_gastos_mes()
        cat_totals = {}
        for g in gastos:
            cat = g["categoria"]
            cat_totals[cat] = cat_totals.get(cat, 0) + g["monto"]

        if not cat_totals:
            return ft.Container(height=0)

        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        max_val = sorted_cats[0][1] if sorted_cats else 1

        rows = []
        for cat, total in sorted_cats[:5]:
            pct = total / max_val
            rows.append(
                ft.Column([
                    ft.Row([
                        ft.Text(cat[:22], size=11, color=TEXT_SEC, expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"${total:,.2f}", size=11, color=RED,
                                weight=ft.FontWeight.BOLD),
                    ]),
                    ft.ProgressBar(value=pct, bgcolor=ft.Colors.with_opacity(0.15, RED),
                                   color=RED, height=5, border_radius=4),
                ], spacing=3)
            )

        return ft.Container(
            content=ft.Column([
                ft.Text("Top categorías", size=13,
                        weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                *rows,
            ], spacing=8),
            bgcolor=NAVY_MID,
            border_radius=14,
            padding=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, RED)),
        )

    summary_area = ft.Column([])

    def refresh():
        load_list()
        summary_area.controls.clear()
        summary_area.controls.append(build_summary())
        page.update()

    # ── Layout ─────────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([
            # Header total
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.RECEIPT_LONG, size=22, color=RED),
                        section_title("Gastos Mensuales", size=18),
                        ft.Container(expand=True),
                        add_btn,
                    ], spacing=8),
                    total_label,
                    total_text,
                ], spacing=4),
                bgcolor=ft.Colors.with_opacity(0.06, RED),
                border_radius=16,
                padding=16,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, RED)),
            ),
            ft.Container(height=6),
            form_section,
            ft.Container(height=4),
            summary_area,
            ft.Container(height=6),
            ft.Row([
                ft.Icon(ft.Icons.LIST_ALT, size=16, color=TEXT_SEC),
                sub_text("Movimientos del mes"),
            ], spacing=6),
            ft.Container(content=gastos_list, expand=True),
        ],
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    refresh()
    view.refresh = refresh  # type: ignore
    return view
