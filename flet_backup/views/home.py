"""
VeloApp — Vista Principal (Dashboard)
Resumen de todos los módulos del mes actual
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, NAV_BG, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, BLACK_STRIP, MONTH_NAMES, DAYS_ES,
    velo_card, section_title, amount_text, sub_text
)


def build_home_view(page: ft.Page) -> ft.Container:
    """Dashboard principal: resumen del mes."""

    now = datetime.now()
    day_name = DAYS_ES[now.weekday()]
    month_name = MONTH_NAMES[now.month]

    # ── controles principales ──────────────────────────────

    gastos_val  = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color=RED)
    ingresos_val = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color=GREEN)
    balance_val  = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color=AMBER)
    ahorros_val  = ft.Text("$0.00", size=26, weight=ft.FontWeight.BOLD, color=ACCENT)
    creditos_val = ft.Text("0", size=26, weight=ft.FontWeight.BOLD, color=AMBER)

    def refresh():
        gastos   = db.get_total_gastos_mes()
        ingresos = db.get_total_ingresos_mes()
        balance  = ingresos - gastos
        ahorros  = db.get_total_ahorros()
        creds    = db.get_creditos(solo_activos=True)

        gastos_val.value   = f"${gastos:,.2f}"
        ingresos_val.value = f"${ingresos:,.2f}"
        balance_val.value  = f"${balance:,.2f}"
        balance_val.color  = GREEN if balance >= 0 else RED
        ahorros_val.value  = f"${ahorros:,.2f}"
        creditos_val.value = str(len(creds))
        page.update()

    # ── Tarjeta de resumen ─────────────────────────────────
    def stat_card(icon, label, value_ctrl, bg_color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=TEXT_WHITE),
                        bgcolor=bg_color,
                        border_radius=10,
                        padding=8,
                    ),
                    ft.Text(label, size=11, color=TEXT_SEC,
                            weight=ft.FontWeight.W_500),
                ], spacing=8, alignment=ft.MainAxisAlignment.START),
                ft.Container(height=6),
                value_ctrl,
                ft.Text(f"{month_name} {now.year}", size=10, color=TEXT_SEC),
            ], spacing=0),
            bgcolor=NAVY_MID,
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ACCENT)),
            expand=True,
        )

    stat_grid = ft.Column([
        ft.Row([
            stat_card(ft.Icons.ARROW_UPWARD, "Ingresos", ingresos_val, GREEN),
            ft.Container(width=8),
            stat_card(ft.Icons.ARROW_DOWNWARD, "Gastos", gastos_val, RED),
        ]),
        ft.Container(height=8),
        ft.Row([
            stat_card(ft.Icons.ACCOUNT_BALANCE_WALLET, "Balance", balance_val, ACCENT),
            ft.Container(width=8),
            stat_card(ft.Icons.SAVINGS, "Ahorros", ahorros_val, ft.Colors.PURPLE_400),
        ]),
        ft.Container(height=8),
        ft.Row([
            stat_card(ft.Icons.CREDIT_CARD, "Créditos activos", creditos_val, AMBER),
            ft.Container(width=8),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=28,
                            color=ft.Colors.with_opacity(0.4, ACCENT)),
                    ft.Text("Toca un\nbotón arriba\no abajo para\nnavegar",
                            size=10, color=TEXT_SEC,
                            text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                bgcolor=ft.Colors.with_opacity(0.08, ACCENT),
                border_radius=16,
                padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.10, ACCENT)),
                expand=True,
            ),
        ]),
    ])

    # ── Quick Tips ─────────────────────────────────────────
    tips = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.STAR, size=16, color=AMBER),
                ft.Text("Consejos rápidos", size=13,
                        weight=ft.FontWeight.BOLD, color=AMBER),
            ], spacing=6),
            ft.Text(
                "📷 Escanea facturas para guardar tus compras\n"
                "💸 Anota cada gasto diario\n"
                "🐷 Ahorra un poco cada día\n"
                "⏰ Tu recordatorio de créditos se activa al abrir la app",
                size=12, color=TEXT_SEC,
            ),
        ], spacing=8),
        bgcolor=ft.Colors.with_opacity(0.07, AMBER),
        border_radius=14,
        padding=14,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.20, AMBER)),
    )

    # ── Layout final ───────────────────────────────────────
    header = ft.Container(
        content=ft.Column([
            ft.Text(
                f"Bienvenido 👋",
                size=22, weight=ft.FontWeight.BOLD, color=TEXT_WHITE,
            ),
            ft.Text(
                f"{day_name} {now.day} de {month_name}",
                size=13, color=TEXT_SEC,
            ),
        ], spacing=2),
        padding=ft.Padding.only(bottom=16),
    )

    view = ft.Container(
        content=ft.Column(
            [header, stat_grid, ft.Container(height=12), tips],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    # Carga inicial + exponer refresh
    refresh()
    view.refresh = refresh  # type: ignore
    return view
