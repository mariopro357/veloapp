"""
VeloApp — Punto de entrada principal
Gestor de Finanzas Personal | Flet 2026 | Android
Diseño: Azul marino oscuro + franjas negras | 7 módulos
"""
import flet as ft
import sys
import os
from datetime import datetime

# Asegurar que src/ sea importable
sys.path.insert(0, os.path.dirname(__file__))

from src.db.database import init_db, get_creditos, get_config, set_config
from src.views.home     import build_home_view
from src.views.scanner  import build_scanner_view
from src.views.gastos   import build_gastos_view
from src.views.clientes import build_clientes_view
from src.views.creditos import build_creditos_view
from src.views.ahorros  import build_ahorros_view
from src.views.horarios import build_horarios_view
from src.views.ingresos import build_ingresos_view

# ============================================================
# CONSTANTES DE DISEÑO
# ============================================================
NAV_BG      = "#07101F"
NAVY_DARK   = "#0A1628"
NAVY_MID    = "#0F2040"
ACCENT      = "#2E7CF6"
BLACK_STRIP = "#000000"
TEXT_WHITE  = "#FFFFFF"
TEXT_SEC    = "#8BA4C0"
GREEN       = "#00D4AA"
AMBER       = "#FFB347"
RED         = "#FF5C5C"

MONTH_NAMES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Navegación: (icono, etiqueta, índice, color_acento)
TOP_NAV = [
    (ft.Icons.DOCUMENT_SCANNER, "Facturas",  0, ACCENT),
    (ft.Icons.RECEIPT_LONG,     "Gastos",    1, RED),
    (ft.Icons.PEOPLE,           "Clientes",  2, GREEN),
]
BOT_NAV = [
    (ft.Icons.CREDIT_CARD,    "Créditos",  3, AMBER),
    (ft.Icons.SAVINGS,        "Ahorros",   4, GREEN),
    (ft.Icons.SCHEDULE,       "Horarios",  5, ACCENT),
    (ft.Icons.ATTACH_MONEY,   "Ingresos",  6, GREEN),
]


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main(page: ft.Page):

    # ── Configuración de la página ─────────────────────────
    page.title       = "VeloApp"
    page.theme_mode  = ft.ThemeMode.DARK
    page.bgcolor     = NAVY_DARK
    page.padding     = 0
    page.spacing     = 0

    # Ocultar barra de título en Android (pantalla completa)
    try:
        page.window.title_bar_hidden = True
    except Exception:
        pass

    # ── Inicilaizar base de datos ──────────────────────────
    init_db()

    # ── Vistas (lazily cargadas) ───────────────────────────
    _views = [None] * 7  # índices 0-6

    def get_view(index: int):
        if _views[index] is None:
            builders = [
                build_scanner_view,
                build_gastos_view,
                build_clientes_view,
                build_creditos_view,
                build_ahorros_view,
                build_horarios_view,
                build_ingresos_view,
            ]
            _views[index] = builders[index](page)
        return _views[index]

    # Vista Home (dashboard central, siempre cargado)
    home_view = build_home_view(page)

    # ── Área de contenido central ──────────────────────────
    content_area = ft.Container(
        content=home_view,
        expand=True,
        bgcolor=NAVY_DARK,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    # ── Estado activo ──────────────────────────────────────
    current_idx = [None]   # None = home
    all_btn_refs = []       # list of (index, container, icon_ctrl, label_ctrl, accent)

    # ── Crear botón de navegación ──────────────────────────
    def make_nav_btn(icon, label, index, accent_color):
        icon_ctrl  = ft.Icon(icon, size=22, color=TEXT_SEC)
        label_ctrl = ft.Text(
            label, size=9, color=TEXT_SEC,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            no_wrap=True,
        )
        btn = ft.Container(
            content=ft.Column(
                [icon_ctrl, label_ctrl],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=ft.Padding.symmetric(horizontal=4, vertical=7),
            border_radius=12,
            bgcolor="transparent",
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
            expand=True,
            on_click=lambda e, i=index: switch_view(i),
            ink=True,
        )
        all_btn_refs.append((index, btn, icon_ctrl, label_ctrl, accent_color))
        return btn

    # ── Cambiar vista ─────────────────────────────────────
    def switch_view(index):
        # Actualizar apariencia de botones
        for i, btn, ic, lbl, acc in all_btn_refs:
            if i == index:
                btn.bgcolor = ft.Colors.with_opacity(0.18, acc)
                ic.color    = acc
                lbl.color   = acc
            else:
                btn.bgcolor = "transparent"
                ic.color    = TEXT_SEC
                lbl.color   = TEXT_SEC
            btn.update()

        current_idx[0] = index

        if index is None:
            # Home
            content_area.content = home_view
            if hasattr(home_view, "refresh"):
                home_view.refresh()
        else:
            v = get_view(index)
            content_area.content = v
            if hasattr(v, "refresh"):
                v.refresh()

        content_area.update()

    # ── Icono home ─────────────────────────────────────────
    def go_home(e):
        # Des-activar todos los botones
        for i, btn, ic, lbl, acc in all_btn_refs:
            btn.bgcolor = "transparent"
            ic.color    = TEXT_SEC
            lbl.color   = TEXT_SEC
            btn.update()
        current_idx[0] = None
        content_area.content = home_view
        if hasattr(home_view, "refresh"):
            home_view.refresh()
        content_area.update()

    # ── Header ────────────────────────────────────────────
    now      = datetime.now()
    day_name = DAYS_ES[now.weekday()]
    date_str = f"{day_name} {now.day} {MONTH_NAMES[now.month]}"

    header = ft.Container(
        content=ft.Row([
            ft.GestureDetector(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("V", size=16, color=TEXT_WHITE,
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=ACCENT,
                        border_radius=10, width=32, height=32,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text("VeloApp", size=17, weight=ft.FontWeight.BOLD,
                                color=TEXT_WHITE),
                        ft.Text(date_str, size=10, color=TEXT_SEC),
                    ], spacing=1),
                ], spacing=8),
                on_tap=go_home,
                mouse_cursor=ft.MouseCursor.CLICK,
            ),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.HOME_OUTLINED,
                icon_color=TEXT_SEC,
                icon_size=22,
                tooltip="Inicio",
                on_click=go_home,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=NAV_BG,
        padding=ft.Padding.only(left=14, right=6, top=10, bottom=8),
        border=ft.Border.only(bottom=ft.BorderSide(2, BLACK_STRIP)),
    )

    # ── Barra de navegación superior (3 botones) ──────────
    top_nav = ft.Container(
        content=ft.Row(
            [make_nav_btn(ic, lb, ix, ac) for ic, lb, ix, ac in TOP_NAV],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ),
        bgcolor=NAV_BG,
        padding=ft.Padding.symmetric(vertical=2, horizontal=6),
        border=ft.Border.only(bottom=ft.BorderSide(3, BLACK_STRIP)),
        height=64,
    )

    # Franja negra decorativa superior
    stripe_top = ft.Container(height=3, bgcolor=BLACK_STRIP)

    # ── Barra de navegación inferior (4 botones) ──────────
    stripe_bot = ft.Container(height=3, bgcolor=BLACK_STRIP)

    bot_nav = ft.Container(
        content=ft.Row(
            [make_nav_btn(ic, lb, ix, ac) for ic, lb, ix, ac in BOT_NAV],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ),
        bgcolor=NAV_BG,
        padding=ft.Padding.symmetric(vertical=2, horizontal=2),
        border=ft.Border.only(top=ft.BorderSide(3, BLACK_STRIP)),
        height=64,
    )

    # ── Layout principal ───────────────────────────────────
    page.add(
        ft.Column([
            header,
            top_nav,
            stripe_top,
            content_area,
            stripe_bot,
            bot_nav,
        ],
            spacing=0,
            expand=True,
        )
    )

    # ── Recordatorio de créditos (in-app, diario) ──────────
    def check_credit_reminder():
        from datetime import date
        today_str = date.today().isoformat()
        last_rem  = get_config("last_credit_reminder", "")
        creds     = get_creditos(solo_activos=True)

        if creds and last_rem != today_str:
            set_config("last_credit_reminder", today_str)
            now2 = datetime.now()

            def close_dlg(e):
                page.close(dlg)

            dlg = ft.AlertDialog(
                modal=True,
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=52, color=AMBER),
                        ft.Text(
                            "💰 Recordatorio de Créditos",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=TEXT_WHITE, text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            f"¡Recuerde pagar su crédito el {now2.day} de "
                            f"{MONTH_NAMES[now2.month]}!\nQue tenga un lindo día 😊",
                            size=14, color=TEXT_SEC,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"Tienes {len(creds)} crédito(s) activo(s)",
                                size=12, color=AMBER,
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.12, AMBER),
                            border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                        ),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=20,
                    width=300,
                ),
                actions=[
                    ft.ElevatedButton(
                        "Entendido ✓",
                        on_click=close_dlg,
                        bgcolor=ACCENT, color=TEXT_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        expand=True,
                    ),
                ],
                bgcolor=NAVY_MID,
                shape=ft.RoundedRectangleBorder(radius=20),
            )
            page.open(dlg)

    # Ejecutar el recordatorio al abrir la app
    page.update()
    check_credit_reminder()


# ============================================================
# ARRANCAR APP
# ============================================================
if __name__ == "__main__":
    ft.run(main)
