"""
VeloApp — Opción 7: Ingresos Diarios
Registra lo que cobraste hoy según tu trabajo, ve totales diarios y mensuales
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, MONTH_NAMES, WORK_TYPES,
    section_title, sub_text, show_snack, empty_state
)


def build_ingresos_view(page: ft.Page) -> ft.Container:

    now = datetime.now()
    month_name = MONTH_NAMES[now.month]

    # ── Resumen ────────────────────────────────────────────
    hoy_text = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=GREEN)
    mes_text  = ft.Text("$0.00", size=20, weight=ft.FontWeight.BOLD, color=ACCENT)
    ingresos_list = ft.ListView(spacing=4, padding=0)

    # ── Tarifa por servicio (configuración) ────────────────
    setup_visible = [False]
    tarifa_field = ft.TextField(
        label="Mi tarifa por servicio/trabajo $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        value=db.get_config("tarifa_base", ""),
    )

    def save_tarifa(e):
        t = tarifa_field.value.strip().replace(",", ".")
        if t:
            try:
                float(t)
                db.set_config("tarifa_base", t)
                show_snack(page, "✅ Tarifa guardada", GREEN)
                tarifa_text.value = f"Tarifa base: ${float(t):,.2f}"
                page.update()
            except ValueError:
                show_snack(page, "Valor inválido", RED)

    tarifa_saved = db.get_config("tarifa_base", "0")
    tarifa_text = ft.Text(
        f"Tarifa base: ${float(tarifa_saved):,.2f}" if tarifa_saved else
        "Sin tarifa configurada",
        size=12, color=TEXT_SEC,
    )

    setup_area = ft.AnimatedSwitcher(
        content=ft.Container(height=0),
        transition=ft.AnimatedSwitcherTransition.FADE, duration=200,
    )

    def toggle_setup(e=None):
        setup_visible[0] = not setup_visible[0]
        if setup_visible[0]:
            setup_area.content = ft.Container(
                content=ft.Column([
                    ft.Text("Configura tu tarifa base", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    sub_text("Esto es cuánto cobras normalmente por servicio"),
                    tarifa_field,
                    ft.ElevatedButton(
                        "Guardar tarifa",
                        on_click=save_tarifa,
                        bgcolor=ACCENT, color=TEXT_WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.with_opacity(0.07, ACCENT),
                border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ACCENT)),
            )
        else:
            setup_area.content = ft.Container(height=0)
        page.update()

    # ── Formulario de ingreso ──────────────────────────────
    tipo_dd = ft.Dropdown(
        label="Tipo de trabajo",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        options=[ft.dropdown.Option(w) for w in WORK_TYPES],
        value=db.get_config("horario_work_type", WORK_TYPES[0]),
    )

    desc_field = ft.TextField(
        label="¿Qué hiciste? (ej: Instalé un split 12000 BTU)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        multiline=True, max_lines=2, expand=True,
    )

    monto_field = ft.TextField(
        label="¿Cuánto cobraste? $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=18),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        expand=True,
    )

    # Botón auto-fill con tarifa base
    def autofill_tarifa(e):
        tarifa = db.get_config("tarifa_base", "")
        if tarifa:
            monto_field.value = tarifa
            monto_field.update()
        else:
            show_snack(page, "Primero configura tu tarifa base ⚙️", AMBER)

    # ── Guardar ingreso ────────────────────────────────────
    def save_ingreso(e):
        tipo = tipo_dd.value or WORK_TYPES[0]
        desc = desc_field.value.strip()
        monto_str = monto_field.value.strip().replace(",", ".")
        if not monto_str:
            show_snack(page, "Ingresa el monto cobrado", RED)
            return
        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            show_snack(page, "Monto inválido", RED)
            return

        db.registrar_ingreso(tipo, desc, monto)
        monto_field.value = ""
        desc_field.value = ""
        show_snack(page, f"✅ ¡Excelente! Ganaste ${monto:,.2f} hoy 💪", GREEN)
        refresh()

    # ── Cargar lista ───────────────────────────────────────
    def load_list():
        ingresos_list.controls.clear()
        ingresos = db.get_ingresos_mes()
        hoy_total = db.get_total_ingresos_hoy()
        mes_total = db.get_total_ingresos_mes()
        hoy_text.value = f"${hoy_total:,.2f}"
        mes_text.value  = f"${mes_total:,.2f}"

        if not ingresos:
            ingresos_list.controls.append(ft.Container(
                content=empty_state(
                    "Sin ingresos este mes.\n¡Anota lo que cobras hoy!",
                    ft.Icons.ATTACH_MONEY,
                ),
                padding=24, alignment=ft.Alignment(0, 0),
            ))
        else:
            # Agrupar por día
            dia_actual = ""
            dia_total = 0.0
            for ing in ingresos:
                if ing["fecha"] != dia_actual:
                    if dia_actual:
                        # Mostrar subtotal del día anterior
                        ingresos_list.controls.insert(
                            -len([x for x in ingresos_list.controls
                                  if hasattr(x, "_dia") and x._dia == dia_actual]),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(dia_actual, size=11,
                                            color=TEXT_SEC, weight=ft.FontWeight.BOLD),
                                    ft.Container(expand=True),
                                    ft.Text(f"Total: ${dia_total:,.2f}", size=11,
                                            color=GREEN, weight=ft.FontWeight.BOLD),
                                ]),
                                padding=ft.Padding.symmetric(vertical=4),
                            )
                        )
                    dia_actual = ing["fecha"]
                    dia_total = 0.0
                    ingresos_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(ing["fecha"], size=11,
                                        color=TEXT_SEC, weight=ft.FontWeight.BOLD),
                            ]),
                            padding=ft.Padding.only(top=8, bottom=4),
                        )
                    )

                dia_total += ing["monto"]

                def del_cb(e, iid=ing["id"]):
                    db.delete_ingreso(iid)
                    refresh()

                ingresos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.ATTACH_MONEY, size=16,
                                                color=GREEN),
                                bgcolor=ft.Colors.with_opacity(0.15, GREEN),
                                border_radius=8, padding=6,
                            ),
                            ft.Column([
                                ft.Text(ing["tipo_trabajo"].split("/")[0].strip(),
                                        size=12, color=ACCENT,
                                        weight=ft.FontWeight.W_500),
                                ft.Text(ing.get("descripcion", "") or " ",
                                        size=11, color=TEXT_SEC,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                            ], spacing=2, expand=True),
                            ft.Text(f"${ing['monto']:,.2f}", size=15,
                                    color=GREEN, weight=ft.FontWeight.BOLD),
                            ft.IconButton(icon=ft.Icons.CLOSE, icon_color=RED,
                                          icon_size=16, on_click=del_cb),
                        ], spacing=8),
                        bgcolor=NAVY_MID, border_radius=10, padding=10,
                        margin=ft.Margin.only(bottom=4),
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.12, GREEN)),
                    )
                )

    # ── Layout ─────────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.ATTACH_MONEY, size=22, color=GREEN),
                section_title("Mis Ingresos", size=18),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS, icon_color=TEXT_SEC, icon_size=20,
                    on_click=toggle_setup, tooltip="Configurar tarifa",
                ),
            ], spacing=8),
            sub_text("Anota lo que ganaste al terminar tu trabajo"),
            tarifa_text,
            ft.Container(height=6),
            setup_area,

            # Resumen hoy / mes
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Hoy ganaste", size=11, color=TEXT_SEC),
                        hoy_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.VerticalDivider(color=TEXT_SEC),
                    ft.Column([
                        ft.Text(f"{month_name}", size=11, color=TEXT_SEC),
                        mes_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                bgcolor=ft.Colors.with_opacity(0.06, GREEN),
                border_radius=16, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.20, GREEN)),
            ),
            ft.Container(height=10),

            # Formulario
            ft.Text("¿Qué cobraste hoy?", size=14,
                    weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            tipo_dd,
            desc_field,
            ft.Row([
                monto_field,
                ft.IconButton(
                    icon=ft.Icons.AUTO_AWESOME, icon_color=AMBER,
                    on_click=autofill_tarifa,
                    tooltip="Usar tarifa base",
                ),
            ], spacing=6),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=20, color=TEXT_WHITE),
                    ft.Text("Registrar cobro de hoy", color=TEXT_WHITE,
                            size=14, weight=ft.FontWeight.W_600),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                on_click=save_ingreso,
                bgcolor=GREEN, expand=True,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding.symmetric(vertical=14),
                ),
            ),
            ft.Container(height=10),

            # Historial
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=16, color=TEXT_SEC),
                ft.Text("Historial del mes", size=13,
                        weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            ], spacing=6),
            ft.Container(content=ingresos_list, expand=True),
        ],
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    def refresh():
        load_list()
        page.update()

    load_list()
    view.refresh = refresh  # type: ignore
    return view
