"""
VeloApp — Constantes de diseño y componentes compartidos
Paleta: Azul marino oscuro + franjas negras
"""
import flet as ft

# =========================================================
# PALETA DE COLORES
# =========================================================
NAV_BG       = "#07101F"   # Fondo navbar (más oscuro)
NAVY_DARK    = "#0A1628"   # Fondo principal
NAVY_MID     = "#0F2040"   # Fondo de tarjetas
NAVY_LIGHT   = "#1A3A6E"   # Elemento con contraste
ACCENT       = "#2E7CF6"   # Azul eléctrico (activo)
ACCENT_DARK  = "#1A5BC4"   # Azul más oscuro
BLACK        = "#000000"
BLACK_STRIP  = "#050A12"   # Franja negra (separador)
TEXT_WHITE   = "#FFFFFF"
TEXT_SEC     = "#8BA4C0"   # Gris azulado
GREEN        = "#00D4AA"
AMBER        = "#FFB347"
RED          = "#FF5C5C"
PURPLE       = "#7C3AED"

# =========================================================
# LISTAS DE DATOS
# =========================================================
MONTH_NAMES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

WORK_TYPES = [
    "Refrigeración / Aire Acondicionado",
    "Electricidad",
    "Plomería",
    "Construcción",
    "Mecánica / Automotriz",
    "Carpintería",
    "Pintura",
    "Jardinería / Paisajismo",
    "Tecnología / Computación",
    "Otro",
]

EXPENSE_CATEGORIES = [
    "🛒 Mercado / Comida",
    "⛽ Combustible / Transporte",
    "💊 Salud / Medicinas",
    "👗 Ropa / Calzado",
    "🏠 Casa / Alquiler",
    "📱 Teléfono / Internet",
    "🔧 Repuestos / Herramientas",
    "🎉 Entretenimiento",
    "📚 Educación",
    "💡 Electricidad / Servicios",
    "🍽️ Comida en la calle",
    "📦 Otros",
]

DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# =========================================================
# COMPONENTES REUTILIZABLES
# =========================================================

def velo_card(content, padding: int = 16, radius: int = 16,
              bgcolor: str = NAVY_MID, border_color: str = None) -> ft.Container:
    """Tarjeta estilo VeloApp con borde sutil."""
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border_radius=radius,
        padding=padding,
        border=ft.Border.all(1, border_color or ft.Colors.with_opacity(0.18, ACCENT)),
        margin=ft.Margin.only(bottom=8),
    )


def section_title(text: str, size: int = 16) -> ft.Text:
    return ft.Text(
        text, size=size,
        weight=ft.FontWeight.BOLD,
        color=TEXT_WHITE,
    )


def sub_text(text: str, size: int = 12) -> ft.Text:
    return ft.Text(text, size=size, color=TEXT_SEC)


def accent_button(text: str, on_click, icon=None, bgcolor: str = ACCENT,
                  expand: bool = False) -> ft.ElevatedButton:
    row_content = []
    if icon:
        row_content.append(ft.Icon(icon, size=18, color=TEXT_WHITE))
    row_content.append(ft.Text(text, color=TEXT_WHITE, size=14,
                                weight=ft.FontWeight.W_600))
    return ft.ElevatedButton(
        content=ft.Row(row_content, tight=True, spacing=6,
                       alignment=ft.MainAxisAlignment.CENTER),
        on_click=on_click,
        bgcolor=bgcolor,
        expand=expand,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            overlay_color=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
        ),
    )


def danger_btn(text: str, on_click) -> ft.TextButton:
    return ft.TextButton(
        text=text,
        on_click=on_click,
        style=ft.ButtonStyle(color=RED),
    )


def divider() -> ft.Container:
    """Franja negra divisoria."""
    return ft.Container(height=2, bgcolor=BLACK_STRIP)


def amount_text(value: float, color: str = GREEN, size: int = 28) -> ft.Text:
    return ft.Text(
        f"${value:,.2f}",
        size=size,
        weight=ft.FontWeight.BOLD,
        color=color,
    )


def badge(text: str, color: str = ACCENT) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=10, color=TEXT_WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=color,
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
    )


def show_snack(page: ft.Page, text: str, color: str = None):
    page.open(ft.SnackBar(
        content=ft.Text(text, color=TEXT_WHITE),
        bgcolor=color or NAVY_LIGHT,
        duration=2500,
    ))


def estado_badge(estado: str) -> ft.Container:
    if estado == "pagado":
        return badge("✓ Pagado", GREEN)
    return badge("⏳ En espera", AMBER)


def empty_state(message: str, icon=None) -> ft.Column:
    return ft.Column([
        ft.Icon(icon or ft.Icons.INBOX, size=64,
                color=ft.Colors.with_opacity(0.25, TEXT_SEC)),
        ft.Text(message, size=14, color=TEXT_SEC,
                text_align=ft.TextAlign.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
       spacing=12)
