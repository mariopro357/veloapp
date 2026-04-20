"""
VeloApp — Opción 5: Ahorros
Ahorra para metas, registra depósitos y retiros, muestra total acumulado
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, PURPLE,
    section_title, sub_text, show_snack, empty_state
)


def build_ahorros_view(page: ft.Page) -> ft.Container:

    total_text = ft.Text("$0.00", size=42, weight=ft.FontWeight.BOLD, color=GREEN)
    total_sub = ft.Text("Total ahorrado", size=13, color=TEXT_SEC)
    movimientos_list = ft.ListView(spacing=4, padding=0)

    # ── Campos ────────────────────────────────────────────
    monto_field = ft.TextField(
        label="Monto $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=18),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        expand=True,
    )
    desc_field = ft.TextField(
        label="Nota (opcional, ej: Ahorré del trabajo hoy)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        expand=True,
    )

    # ── Registrar movimiento ───────────────────────────────
    def registrar(tipo: str):
        monto_str = monto_field.value.strip().replace(",", ".")
        if not monto_str:
            show_snack(page, "Ingresa un monto", RED)
            return
        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            show_snack(page, "Monto inválido", RED)
            return

        if tipo == "gasto":
            total_actual = db.get_total_ahorros()
            if monto > total_actual:
                show_snack(page, f"No tienes suficientes ahorros (${total_actual:,.2f})", RED)
                return

        desc = desc_field.value.strip()
        db.registrar_ahorro(tipo, monto, desc)

        if tipo == "ahorro":
            show_snack(page, f"🐷 ¡Ahorrado ${monto:,.2f}! Sige así 💪", GREEN)
        else:
            show_snack(page, f"💸 Gasto de ${monto:,.2f} descontado de ahorros", AMBER)

        monto_field.value = ""
        desc_field.value = ""
        refresh()

    # ── Meta de ahorro ─────────────────────────────────────
    meta_field = ft.TextField(
        label="Mi meta de ahorro $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=160,
        value=db.get_config("meta_ahorro", ""),
    )
    meta_progress = ft.ProgressBar(value=0, bgcolor=ft.Colors.with_opacity(0.15, GREEN),
                                   color=GREEN, height=10, border_radius=6)
    meta_pct_text = ft.Text("0%", size=12, color=GREEN, weight=ft.FontWeight.BOLD)
    meta_desc_text = ft.Text("", size=11, color=TEXT_SEC)

    def save_meta(e):
        m = meta_field.value.strip().replace(",", ".")
        if m:
            try:
                float(m)
                db.set_config("meta_ahorro", m)
                show_snack(page, "✅ Meta guardada", GREEN)
                refresh()
            except ValueError:
                show_snack(page, "Meta inválida", RED)

    # ── Cargar datos ───────────────────────────────────────
    def load_movimientos():
        movimientos_list.controls.clear()
        movs = db.get_movimientos_ahorros()
        if not movs:
            movimientos_list.controls.append(ft.Container(
                content=empty_state("Sin movimientos aún", ft.Icons.SAVINGS),
                padding=24, alignment=ft.Alignment(0, 0),
            ))
        else:
            for m in movs:
                es_ahorro = m["tipo"] == "ahorro"
                movimientos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.ADD if es_ahorro else ft.Icons.REMOVE,
                                    size=16, color=GREEN if es_ahorro else RED,
                                ),
                                bgcolor=ft.Colors.with_opacity(
                                    0.15, GREEN if es_ahorro else RED),
                                border_radius=8, padding=6,
                            ),
                            ft.Column([
                                ft.Text(m.get("descripcion", "") or
                                        ("Ahorro" if es_ahorro else "Gasto de ahorros"),
                                        size=12, color=TEXT_WHITE,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(m["fecha"], size=10, color=TEXT_SEC),
                            ], spacing=2, expand=True),
                            ft.Text(
                                f"{'+'if es_ahorro else '-'}${m['monto']:,.2f}",
                                size=14, color=GREEN if es_ahorro else RED,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ], spacing=10),
                        bgcolor=NAVY_MID, border_radius=10, padding=10,
                        margin=ft.Margin.only(bottom=4),
                        border=ft.Border.all(
                            1, ft.Colors.with_opacity(
                                0.12, GREEN if es_ahorro else RED)),
                    )
                )

    def refresh():
        total = db.get_total_ahorros()
        total_text.value = f"${total:,.2f}"
        total_text.color = GREEN if total >= 0 else RED

        # Meta progress
        meta_str = db.get_config("meta_ahorro", "0")
        try:
            meta = float(meta_str)
        except (ValueError, TypeError):
            meta = 0

        if meta > 0:
            pct = min(total / meta, 1.0)
            meta_progress.value = pct
            meta_pct_text.value = f"{pct*100:.1f}%"
            meta_desc_text.value = (
                f"${total:,.2f} de ${meta:,.2f} — "
                f"faltan ${max(meta - total, 0):,.2f}"
            )
        else:
            meta_progress.value = 0
            meta_pct_text.value = ""
            meta_desc_text.value = "Define una meta para ver tu progreso"

        load_movimientos()
        page.update()

    # ── Layout ─────────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.SAVINGS, size=22, color=GREEN),
                section_title("Mis Ahorros", size=18),
            ], spacing=8),
            sub_text("Cada peso cuenta. ¡Tú puedes!"),
            ft.Container(height=8),

            # Total display
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=36, color=GREEN),
                    total_text,
                    total_sub,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                bgcolor=ft.Colors.with_opacity(0.06, GREEN),
                border_radius=20, padding=20,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.20, GREEN)),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=10),

            # Meta progress
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🎯 Mi meta de ahorro", size=13,
                                weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                        ft.Container(expand=True),
                        meta_pct_text,
                    ]),
                    meta_progress,
                    meta_desc_text,
                    ft.Row([
                        meta_field,
                        ft.ElevatedButton(
                            "Guardar meta",
                            on_click=save_meta,
                            bgcolor=ACCENT, color=TEXT_WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                            ),
                        ),
                    ], spacing=8),
                ], spacing=8),
                bgcolor=NAVY_MID, border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ACCENT)),
            ),
            ft.Container(height=10),

            # Acciones
            ft.Text("¿Qué vas a hacer hoy?", size=14,
                    weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            monto_field,
            desc_field,
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=18, color=TEXT_WHITE),
                        ft.Text("🐷 Ahorré hoy", color=TEXT_WHITE,
                                weight=ft.FontWeight.W_600),
                    ], spacing=6, tight=True),
                    on_click=lambda e: registrar("ahorro"),
                    bgcolor=GREEN,
                    expand=True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(vertical=14),
                    ),
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REMOVE, size=18, color=TEXT_WHITE),
                        ft.Text("💸 Gasté", color=TEXT_WHITE,
                                weight=ft.FontWeight.W_600),
                    ], spacing=6, tight=True),
                    on_click=lambda e: registrar("gasto"),
                    bgcolor=RED,
                    expand=True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding.symmetric(vertical=14),
                    ),
                ),
            ]),
            ft.Container(height=10),

            # Historial
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=16, color=TEXT_SEC),
                ft.Text("Historial de movimientos", size=13,
                        weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            ], spacing=6),
            ft.Container(content=movimientos_list, expand=True),
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
