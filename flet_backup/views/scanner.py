"""
VeloApp — Opción 1: Escáner de Facturas
Escanea facturas (online/offline), lista de productos y bloc de notas mensual
"""
import flet as ft
import json
import os
import threading
from datetime import datetime
from src.db import database as db
from src.utils import ocr as ocr_module
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, BLACK_STRIP, MONTH_NAMES,
    velo_card, section_title, sub_text, accent_button,
    show_snack, empty_state
)


def build_scanner_view(page: ft.Page) -> ft.Container:

    # ── Estado interno ─────────────────────────────────────
    current_image_path = [None]
    current_items = []          # lista editable de items detectados
    manual_items = []           # items en modo offline

    # ── Controles ──────────────────────────────────────────
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    img_preview = ft.Image(
        src="",
        visible=False, border_radius=12, fit=ft.BoxFit.CONTAIN,
        width=340, height=180,
    )
    scan_status = ft.Text("", size=12, color=TEXT_SEC,
                          text_align=ft.TextAlign.CENTER)

    items_list = ft.ListView(spacing=4, padding=0)
    items_section = ft.Column([
        ft.Row([
            section_title("Productos detectados"),
            ft.Container(expand=True),
        ]),
        items_list,
    ], visible=False, spacing=8)

    # Bloc de notas (facturas guardadas)
    notes_list = ft.ListView(spacing=6, padding=0, expand=True)

    # Campo para nombrar la factura
    titulo_field = ft.TextField(
        label="Nombre de la factura (ej: Mercado del Viernes)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT,
        focused_border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        visible=False,
    )

    save_btn = ft.ElevatedButton(
        "💾 Guardar factura del mes",
        on_click=lambda e: save_factura(),
        bgcolor=GREEN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12),
                             padding=ft.Padding.symmetric(vertical=12)),
        color=TEXT_WHITE,
        visible=False,
    )

    # ── Helper: construir fila de item ─────────────────────
    def build_item_row(item: dict, idx: int, editable: bool = False):
        prod_ctrl = ft.Text(
            item["producto"],
            size=13, color=TEXT_WHITE, expand=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        price_ctrl = ft.Text(
            f"${item['precio']}",
            size=14, color=GREEN, weight=ft.FontWeight.BOLD,
            width=80, text_align=ft.TextAlign.RIGHT,
        )
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{idx+1}.", size=12, color=TEXT_SEC, width=22),
                prod_ctrl,
                price_ctrl,
            ], spacing=6),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor=ft.Colors.with_opacity(0.05 if idx % 2 == 0 else 0.0, ACCENT),
            border_radius=8,
        )

    def render_items():
        items_list.controls.clear()
        if current_items:
            for i, item in enumerate(current_items):
                items_list.controls.append(build_item_row(item, i))
            items_section.visible = True
            titulo_field.visible = True
            save_btn.visible = True
        else:
            items_section.visible = False
            titulo_field.visible = False
            save_btn.visible = False

    # ── Manual: agregar item offline ───────────────────────
    manual_prod = ft.TextField(
        label="Producto",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        expand=True,
    )
    manual_price = ft.TextField(
        label="Precio $",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT,
        bgcolor=NAVY_DARK,
        border_radius=10,
        width=110,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    manual_section = ft.Column([
        ft.Text("📝 Modo offline — ingresa los items manualmente",
                size=12, color=AMBER),
        ft.Row([manual_prod, manual_price], spacing=8),
        ft.ElevatedButton(
            "+ Agregar item",
            on_click=lambda e: add_manual_item(),
            bgcolor=ACCENT,
            color=TEXT_WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        ),
    ], spacing=8, visible=False)

    def add_manual_item():
        prod = manual_prod.value.strip()
        price = manual_price.value.strip()
        if not prod or not price:
            show_snack(page, "Ingresa producto y precio", RED)
            return
        current_items.append({"producto": prod, "precio": price})
        manual_prod.value = ""
        manual_price.value = ""
        render_items()
        page.update()

    # ── Escanear imagen ────────────────────────────────────
    def process_image(image_path: str):
        current_image_path[0] = image_path
        scan_status.value = "⏳ Procesando imagen..."
        img_preview.src = image_path
        img_preview.visible = True
        current_items.clear()
        render_items()
        manual_section.visible = False
        page.update()

        def run_ocr():
            result = ocr_module.scan_invoice(image_path)
            if result["online"] and result["items"]:
                current_items.extend(result["items"])
                scan_status.value = (
                    f"✅ Online — {len(result['items'])} items detectados"
                )
            elif result["online"] and not result["items"]:
                scan_status.value = (
                    "⚠️ Se leyó la factura pero no se detectaron precios. "
                    "Agrega los items manualmente."
                )
                manual_section.visible = True
            else:
                # Offline
                scan_status.value = result.get("error", "Sin internet — modo manual")
                manual_section.visible = True

            render_items()
            page.update()

        thread = threading.Thread(target=run_ocr, daemon=True)
        thread.start()

    def on_file_pick(e):
        if e.files:
            process_image(e.files[0].path)

    file_picker.on_result = on_file_pick

    # ── Guardar factura ────────────────────────────────────
    def save_factura():
        if not current_items:
            show_snack(page, "No hay items para guardar", RED)
            return
        titulo = titulo_field.value.strip() or f"Factura {datetime.now().strftime('%d/%m')}"
        raw    = json.dumps(current_items, ensure_ascii=False)
        db.save_factura(titulo, raw, current_items)
        show_snack(page, f"✅ '{titulo}' guardada en el bloc del mes", GREEN)

        # Reset
        current_items.clear()
        img_preview.visible = False
        scan_status.value = ""
        titulo_field.value = ""
        manual_section.visible = False
        render_items()
        load_notes()
        page.update()

    # ── Notas del mes ──────────────────────────────────────
    def load_notes():
        notes_list.controls.clear()
        facturas = db.get_facturas_mes()
        if not facturas:
            notes_list.controls.append(
                ft.Container(
                    content=empty_state("Sin facturas este mes", ft.Icons.RECEIPT_LONG),
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            total_mes = sum(
                sum(
                    float(it["precio"].replace(",", ".").replace("$", ""))
                    for it in f["items"]
                    if it.get("precio", "").replace(",", "").replace(".", "").isdigit()
                    or any(c.isdigit() for c in it.get("precio", ""))
                )
                for f in facturas
            )
            notes_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("Total del mes:", size=13, color=TEXT_SEC),
                        ft.Text(f"📊 {len(facturas)} facturas", size=12, color=ACCENT),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.only(bottom=8),
                )
            )
            for f in facturas:
                def delete_cb(e, fid=f["id"]):
                    db.delete_factura(fid)
                    load_notes()
                    page.update()

                items_preview = ", ".join(
                    it["producto"] for it in f["items"][:3]
                )
                if len(f["items"]) > 3:
                    items_preview += f" + {len(f['items']) - 3} más"

                notes_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.RECEIPT, size=18, color=ACCENT),
                                ft.Text(f["titulo"] or "Factura", size=13,
                                        color=TEXT_WHITE,
                                        weight=ft.FontWeight.W_600,
                                        expand=True,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f["fecha"], size=10, color=TEXT_SEC),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=RED,
                                    icon_size=18,
                                    on_click=delete_cb,
                                    tooltip="Eliminar",
                                ),
                            ], spacing=6),
                            ft.Text(
                                items_preview or "Sin items detectados",
                                size=11, color=TEXT_SEC,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{len(f['items'])} productos",
                                size=10, color=GREEN,
                            ),
                        ], spacing=4),
                        bgcolor=NAVY_MID,
                        border_radius=12,
                        padding=12,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ACCENT)),
                        margin=ft.Margin.only(bottom=6),
                    )
                )

    # ── Layout ─────────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([
            # Header
            ft.Row([
                ft.Icon(ft.Icons.DOCUMENT_SCANNER, size=22, color=ACCENT),
                section_title("Escáner de Facturas", size=18),
            ], spacing=8),
            sub_text("Fácil, rápido y sin errores"),
            ft.Container(height=10),

            # Botones de cámara / galería
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CAMERA_ALT, size=28, color=TEXT_WHITE),
                        ft.Text("Tomar foto", size=11, color=TEXT_WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    on_click=lambda e: file_picker.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["jpg", "jpeg", "png"],
                        file_type=ft.FilePickerFileType.IMAGE,
                    ),
                    bgcolor=ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14),
                                        padding=ft.Padding.symmetric(horizontal=20, vertical=12)),
                    expand=True,
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PHOTO_LIBRARY, size=28, color=TEXT_WHITE),
                        ft.Text("Galería", size=11, color=TEXT_WHITE),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    on_click=lambda e: file_picker.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["jpg", "jpeg", "png"],
                    ),
                    bgcolor=NAVY_MID,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14),
                                        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                                        side=ft.BorderSide(1, ACCENT)),
                    expand=True,
                ),
            ]),
            ft.Container(height=8),

            # Preview + status
            ft.Container(
                content=ft.Column([
                    img_preview,
                    scan_status,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                alignment=ft.Alignment(0, 0),
            ),

            # Modo manual (offline)
            manual_section,
            ft.Container(height=4),

            # Items detectados
            titulo_field,
            items_section,
            save_btn,

            ft.Divider(color=BLACK_STRIP, thickness=2),

            # Bloc de notas del mes
            ft.Row([
                ft.Icon(ft.Icons.NOTE_ALT, size=18, color=AMBER),
                section_title("Bloc del mes", size=15),
            ], spacing=6),
            sub_text("Todas las facturas guardadas este mes"),
            ft.Container(height=6),
            ft.Container(content=notes_list, expand=True),
        ],
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
        ),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    # Carga inicial
    load_notes()

    def refresh():
        load_notes()
        page.update()

    view.refresh = refresh  # type: ignore
    return view
