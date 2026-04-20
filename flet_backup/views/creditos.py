"""
VeloApp — Opción 4: Créditos
Registro de compras a crédito, cuotas mensuales, recordatorio diario
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, ACCENT_DARK, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, MONTH_NAMES,
    section_title, sub_text, show_snack, empty_state, velo_card
)


def build_creditos_view(page: ft.Page) -> ft.Container:

    creditos_list = ft.ListView(spacing=8, padding=0)
    form_visible = [False]
    now = datetime.now()

    # ── Campos del formulario ──────────────────────────────
    nombre_field = ft.TextField(
        label="¿Qué compraste? (ej: Televisor Samsung)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
    )
    costo_field = ft.TextField(
        label="Costo total $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    cuota_field = ft.TextField(
        label="Cuota mensual $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    form_section = ft.AnimatedSwitcher(
        content=ft.Container(height=0),
        transition=ft.AnimatedSwitcherTransition.FADE, duration=200,
    )

    def toggle_form(e=None):
        form_visible[0] = not form_visible[0]
        if form_visible[0]:
            form_section.content = ft.Container(
                content=ft.Column([
                    ft.Text("Nuevo crédito", size=14,
                            weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    nombre_field,
                    ft.Row([costo_field, cuota_field], spacing=8),
                    ft.ElevatedButton(
                        "💳 Registrar crédito",
                        on_click=save_credito,
                        bgcolor=ACCENT, color=TEXT_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding.symmetric(vertical=12),
                        ),
                        expand=True,
                    ),
                ], spacing=10),
                bgcolor=ft.Colors.with_opacity(0.07, ACCENT),
                border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.20, ACCENT)),
            )
        else:
            form_section.content = ft.Container(height=0)
        page.update()

    def save_credito(e):
        nombre = nombre_field.value.strip()
        costo_str = costo_field.value.strip().replace(",", ".")
        cuota_str = cuota_field.value.strip().replace(",", ".")
        if not nombre or not costo_str or not cuota_str:
            show_snack(page, "Completa todos los campos", RED)
            return
        try:
            costo = float(costo_str)
            cuota = float(cuota_str)
            if costo <= 0 or cuota <= 0:
                raise ValueError
        except ValueError:
            show_snack(page, "Montos inválidos", RED)
            return

        db.create_credito(nombre, costo, cuota)
        nombre_field.value = ""
        costo_field.value = ""
        cuota_field.value = ""
        form_visible[0] = False
        form_section.content = ft.Container(height=0)
        show_snack(page, f"✅ Crédito '{nombre}' registrado", GREEN)
        load_list()
        page.update()

    # ── Pagar cuota ────────────────────────────────────────
    def pagar_cuota(credito: dict):
        cuota_val = ft.TextField(
            label=f"Monto a pagar (cuota: ${credito['cuota_mensual']:,.2f})",
            label_style=ft.TextStyle(color=TEXT_SEC, size=12),
            text_style=ft.TextStyle(color=TEXT_WHITE),
            border_color=ACCENT, focused_border_color=ACCENT,
            bgcolor=NAVY_DARK, border_radius=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(credito["cuota_mensual"]),
        )

        def confirm_pago(e):
            try:
                monto = float(cuota_val.value.replace(",", "."))
                db.pagar_cuota_credito(credito["id"], monto)
                show_snack(page, f"✅ Pago de ${monto:,.2f} registrado", GREEN)
                page.close(dlg)
                load_list()
                page.update()
            except Exception:
                show_snack(page, "Monto inválido", RED)

        def cancel(e):
            page.close(dlg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Registrar pago", color=TEXT_WHITE),
            content=ft.Column([
                ft.Text(f"Crédito: {credito['nombre']}", size=13, color=TEXT_SEC),
                cuota_val,
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel,
                              style=ft.ButtonStyle(color=TEXT_SEC)),
                ft.ElevatedButton("Pagar", on_click=confirm_pago,
                                  bgcolor=GREEN, color=TEXT_WHITE,
                                  style=ft.ButtonStyle(
                                      shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            bgcolor=NAVY_MID, shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.open(dlg)

    # ── Cargar lista ───────────────────────────────────────
    def load_list():
        creditos_list.controls.clear()
        creditos = db.get_creditos()

        activos = [c for c in creditos if not c["completado"]]
        completados = [c for c in creditos if c["completado"]]

        total_deuda = sum(
            c["costo_total"] - c["monto_pagado"] for c in activos
        )

        if not creditos:
            creditos_list.controls.append(ft.Container(
                content=empty_state("Sin créditos registrados", ft.Icons.CREDIT_CARD),
                padding=32, alignment=ft.Alignment(0, 0),
            ))
            return

        # ── Resumen total ──────────────────────────────────
        creditos_list.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("Deuda total", size=11, color=TEXT_SEC),
                        ft.Text(f"${total_deuda:,.2f}", size=20,
                                color=RED, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.VerticalDivider(color=TEXT_SEC),
                    ft.Column([
                        ft.Text("Activos", size=11, color=TEXT_SEC),
                        ft.Text(str(len(activos)), size=20,
                                color=AMBER, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.VerticalDivider(color=TEXT_SEC),
                    ft.Column([
                        ft.Text("Pagados", size=11, color=TEXT_SEC),
                        ft.Text(str(len(completados)), size=20,
                                color=GREEN, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                bgcolor=ft.Colors.with_opacity(0.06, RED),
                border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.15, RED)),
                margin=ft.Margin.only(bottom=8),
            )
        )

        # ── Créditos activos ───────────────────────────────
        if activos:
            creditos_list.controls.append(
                ft.Text("💳 Activos", size=14, weight=ft.FontWeight.BOLD,
                        color=AMBER)
            )
            for c in activos:
                pagado = c["monto_pagado"]
                total = c["costo_total"]
                pct = min(pagado / total, 1.0) if total > 0 else 0
                restante = total - pagado
                meses_rest = (
                    int(restante / c["cuota_mensual"]) + 1
                    if c["cuota_mensual"] > 0 else 0
                )

                def complete_cb(e, cid=c["id"], cname=c["nombre"]):
                    db.completar_credito(cid)
                    show_snack(page, f"🎉 ¡Crédito '{cname}' pagado completamente!", GREEN)
                    load_list()
                    page.update()

                def pagar_cb(e, cred=c):
                    pagar_cuota(cred)

                def del_cb(e, cid=c["id"]):
                    db.delete_credito(cid)
                    load_list()
                    page.update()

                creditos_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CREDIT_CARD, size=18, color=AMBER),
                                ft.Text(c["nombre"], size=14, color=TEXT_WHITE,
                                        weight=ft.FontWeight.W_600, expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE,
                                              icon_color=RED, icon_size=16,
                                              on_click=del_cb),
                            ], spacing=6),
                            ft.ProgressBar(
                                value=pct,
                                bgcolor=ft.Colors.with_opacity(0.15, AMBER),
                                color=GREEN if pct >= 1.0 else AMBER,
                                height=8, border_radius=4,
                            ),
                            ft.Row([
                                ft.Text(f"${pagado:,.2f} / ${total:,.2f}",
                                        size=11, color=TEXT_SEC),
                                ft.Container(expand=True),
                                ft.Text(f"{pct*100:.0f}%", size=11,
                                        color=GREEN if pct >= 0.8 else AMBER,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Cuota mensual", size=10, color=TEXT_SEC),
                                    ft.Text(f"${c['cuota_mensual']:,.2f}", size=13,
                                            color=AMBER, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Column([
                                    ft.Text("Resta aprox.", size=10, color=TEXT_SEC),
                                    ft.Text(f"{meses_rest} mes(es)", size=13,
                                            color=TEXT_SEC),
                                ]),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "Pagar cuota",
                                    on_click=pagar_cb,
                                    bgcolor=ACCENT, color=TEXT_WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding.symmetric(
                                            horizontal=10, vertical=8),
                                    ),
                                ),
                            ], spacing=8),
                            ft.ElevatedButton(
                                "✅ Crédito pagado completamente",
                                on_click=complete_cb,
                                bgcolor=ft.Colors.with_opacity(0.15, GREEN),
                                color=GREEN,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(vertical=10),
                                    side=ft.BorderSide(1, GREEN),
                                ),
                                expand=True,
                            ),
                        ], spacing=8),
                        bgcolor=NAVY_MID, border_radius=14, padding=14,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.20, AMBER)),
                        margin=ft.Margin.only(bottom=8),
                    )
                )

        # ── Créditos completados ───────────────────────────
        if completados:
            creditos_list.controls.append(
                ft.Text("✅ Completados", size=14,
                        weight=ft.FontWeight.BOLD, color=GREEN)
            )
            for c in completados:
                def del_cb(e, cid=c["id"]):
                    db.delete_credito(cid)
                    load_list()
                    page.update()

                creditos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=GREEN),
                            ft.Text(c["nombre"], size=13, color=TEXT_SEC,
                                    expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(f"${c['costo_total']:,.2f}", size=13,
                                    color=GREEN, weight=ft.FontWeight.BOLD),
                            ft.IconButton(icon=ft.Icons.CLOSE, icon_color=RED,
                                          icon_size=16, on_click=del_cb),
                        ], spacing=8),
                        bgcolor=ft.Colors.with_opacity(0.05, GREEN),
                        border_radius=10, padding=10,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.15, GREEN)),
                        margin=ft.Margin.only(bottom=4),
                    )
                )

    # ── Layout ─────────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CREDIT_CARD, size=22, color=AMBER),
                section_title("Mis Créditos", size=18),
                ft.Container(expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD, bgcolor=AMBER, foreground_color=TEXT_WHITE,
                    on_click=toggle_form, mini=True,
                    tooltip="Nuevo crédito",
                ),
            ], spacing=8),
            sub_text("Controla lo que debes, cuánto pagas al mes"),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=14, color=AMBER),
                    ft.Text(
                        f"Recordatorio activo: cada vez que abras la app",
                        size=11, color=TEXT_SEC,
                    ),
                ], spacing=6),
                bgcolor=ft.Colors.with_opacity(0.08, AMBER),
                border_radius=8, padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            ),
            ft.Container(height=6),
            form_section,
            ft.Container(height=4),
            ft.Container(content=creditos_list, expand=True),
        ],
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    load_list()

    def refresh():
        load_list()
        page.update()

    view.refresh = refresh  # type: ignore
    return view
