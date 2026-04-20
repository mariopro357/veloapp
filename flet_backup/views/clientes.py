"""
VeloApp — Opción 3: Cartelera de Clientes
Carpetas de clientes con historial de trabajos y estado de pago
"""
import flet as ft
from datetime import datetime
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, BLACK_STRIP, MONTH_NAMES,
    section_title, sub_text, show_snack, empty_state,
    estado_badge
)


def build_clientes_view(page: ft.Page) -> ft.Container:

    # ── Estado de navegación ───────────────────────────────
    active_cliente = [None]   # None = lista de clientes | dict = carpeta de cliente

    # ── Contenedor principal (se intercambia) ──────────────
    main_area = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=6, expand=True)

    # ══════════════════════════════════════════════════════
    # VISTA: Lista de Clientes
    # ══════════════════════════════════════════════════════

    # Campos para nuevo cliente
    nuevo_nombre = ft.TextField(
        label="Nombre del cliente",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10, expand=True,
    )
    nuevo_tel = ft.TextField(
        label="Teléfono (opcional)",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10, width=140,
        keyboard_type=ft.KeyboardType.PHONE,
    )

    add_form_visible = [False]
    add_form = ft.AnimatedSwitcher(
        content=ft.Container(height=0),
        transition=ft.AnimatedSwitcherTransition.FADE, duration=200,
    )

    def toggle_add_form(e=None):
        add_form_visible[0] = not add_form_visible[0]
        if add_form_visible[0]:
            add_form.content = ft.Container(
                content=ft.Column([
                    ft.Text("Nuevo cliente", size=14,
                            weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    ft.Row([nuevo_nombre, nuevo_tel], spacing=8),
                    ft.ElevatedButton(
                        "Guardar cliente",
                        on_click=save_new_client,
                        bgcolor=GREEN, color=TEXT_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10)),
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.with_opacity(0.07, GREEN),
                border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.20, GREEN)),
            )
        else:
            add_form.content = ft.Container(height=0)
        page.update()

    def save_new_client(e):
        nombre = nuevo_nombre.value.strip()
        if not nombre:
            show_snack(page, "Escribe el nombre del cliente", RED)
            return
        db.create_cliente(nombre, nuevo_tel.value.strip())
        nuevo_nombre.value = ""
        nuevo_tel.value = ""
        add_form_visible[0] = False
        add_form.content = ft.Container(height=0)
        show_snack(page, f"✅ Cliente '{nombre}' creado", GREEN)
        show_clients_list()

    def show_clients_list():
        active_cliente[0] = None
        main_area.controls.clear()
        clientes = db.get_clientes()

        header = ft.Row([
            ft.Icon(ft.Icons.PEOPLE, size=22, color=ACCENT),
            section_title("Mis Clientes", size=18),
            ft.Container(expand=True),
            ft.FloatingActionButton(
                icon=ft.Icons.PERSON_ADD,
                bgcolor=ACCENT, foreground_color=TEXT_WHITE,
                on_click=toggle_add_form, mini=True,
                tooltip="Agregar cliente",
            ),
        ], spacing=8)

        main_area.controls.append(header)
        main_area.controls.append(sub_text(f"{len(clientes)} cliente(s) registrados"))
        main_area.controls.append(ft.Container(height=6))
        main_area.controls.append(add_form)
        main_area.controls.append(ft.Container(height=4))

        if not clientes:
            main_area.controls.append(ft.Container(
                content=empty_state("Sin clientes aún.\nToca ＋ para agregar tu primero",
                                   ft.Icons.PERSON_ADD_ALT),
                padding=32, alignment=ft.Alignment(0, 0),
            ))
        else:
            for c in clientes:
                pendiente = db.get_total_pendiente_cliente(c["id"])
                trabajos = db.get_trabajos_cliente(c["id"])

                def open_client(e, cl=c):
                    show_client_detail(cl)

                def del_client(e, cid=c["id"], cname=c["nombre"]):
                    def confirm(ev):
                        db.delete_cliente(cid)
                        show_snack(page, f"Cliente '{cname}' eliminado", RED)
                        show_clients_list()
                        page.close(dlg)

                    def cancel(ev):
                        page.close(dlg)

                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("¿Eliminar cliente?", color=TEXT_WHITE),
                        content=ft.Text(f"Se borrará '{cname}' y todos sus trabajos.",
                                        color=TEXT_SEC),
                        actions=[
                            ft.TextButton("Cancelar", on_click=cancel,
                                          style=ft.ButtonStyle(color=TEXT_SEC)),
                            ft.TextButton("Eliminar", on_click=confirm,
                                          style=ft.ButtonStyle(color=RED)),
                        ],
                        bgcolor=NAVY_MID, shape=ft.RoundedRectangleBorder(radius=16),
                    )
                    page.open(dlg)

                main_area.controls.append(
                    ft.GestureDetector(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Text(
                                        c["nombre"][0].upper(), size=18,
                                        color=TEXT_WHITE, weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=ACCENT, border_radius=25,
                                    width=46, height=46,
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column([
                                    ft.Text(c["nombre"], size=14, color=TEXT_WHITE,
                                            weight=ft.FontWeight.W_600,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(
                                        f"{len(trabajos)} trabajos · "
                                        f"Pendiente: ${pendiente:,.2f}",
                                        size=11, color=AMBER if pendiente > 0 else TEXT_SEC,
                                    ),
                                ], spacing=3, expand=True),
                                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_SEC, size=20),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE, icon_color=RED,
                                    icon_size=18, on_click=del_client,
                                ),
                            ], spacing=10),
                            bgcolor=NAVY_MID, border_radius=14, padding=12,
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ACCENT)),
                            margin=ft.Margin.only(bottom=6),
                        ),
                        on_tap=open_client,
                    )
                )
        page.update()

    # ══════════════════════════════════════════════════════
    # VISTA: Detalle de Cliente (carpeta)
    # ══════════════════════════════════════════════════════

    def show_client_detail(cliente: dict):
        active_cliente[0] = cliente
        main_area.controls.clear()

        trabajo_desc = ft.TextField(
            label="Descripción del trabajo",
            label_style=ft.TextStyle(color=TEXT_SEC, size=12),
            text_style=ft.TextStyle(color=TEXT_WHITE),
            border_color=ACCENT, focused_border_color=ACCENT,
            bgcolor=NAVY_DARK, border_radius=10, expand=True,
            multiline=True, max_lines=3,
        )
        trabajo_monto = ft.TextField(
            label="Cobré $",
            label_style=ft.TextStyle(color=TEXT_SEC, size=12),
            text_style=ft.TextStyle(color=TEXT_WHITE),
            border_color=ACCENT, focused_border_color=ACCENT,
            bgcolor=NAVY_DARK, border_radius=10, width=130,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        trabajo_form_visible = [False]
        trabajo_form = ft.AnimatedSwitcher(
            content=ft.Container(height=0),
            transition=ft.AnimatedSwitcherTransition.FADE, duration=200,
        )

        def toggle_trabajo_form(e=None):
            trabajo_form_visible[0] = not trabajo_form_visible[0]
            if trabajo_form_visible[0]:
                trabajo_form.content = ft.Container(
                    content=ft.Column([
                        ft.Text("Nuevo trabajo", size=13,
                                weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                        trabajo_desc,
                        ft.Row([trabajo_monto, ft.Container(expand=True),
                                ft.ElevatedButton(
                                    "Guardar",
                                    on_click=lambda e: save_nuevo_trabajo(),
                                    bgcolor=ACCENT, color=TEXT_WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=10)),
                                )], spacing=8),
                    ], spacing=8),
                    bgcolor=ft.Colors.with_opacity(0.07, ACCENT),
                    border_radius=14, padding=14,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ACCENT)),
                )
            else:
                trabajo_form.content = ft.Container(height=0)
            page.update()

        def save_nuevo_trabajo():
            desc = trabajo_desc.value.strip()
            monto_str = trabajo_monto.value.strip().replace(",", ".")
            if not desc or not monto_str:
                show_snack(page, "Completa todos los campos", RED)
                return
            try:
                monto = float(monto_str)
            except ValueError:
                show_snack(page, "Monto inválido", RED)
                return
            db.create_trabajo(cliente["id"], desc, monto)
            trabajo_desc.value = ""
            trabajo_monto.value = ""
            trabajo_form_visible[0] = False
            trabajo_form.content = ft.Container(height=0)
            show_snack(page, "✅ Trabajo guardado", GREEN)
            show_client_detail(cliente)

        trabajos_list = ft.ListView(spacing=6, padding=0)

        def load_trabajos():
            trabajos_list.controls.clear()
            trabajos = db.get_trabajos_cliente(cliente["id"])
            total_pendiente = sum(
                t["monto"] for t in trabajos if t["estado"] == "en_espera"
            )
            total_cobrado = sum(
                t["monto"] for t in trabajos if t["estado"] == "pagado"
            )

            if not trabajos:
                trabajos_list.controls.append(ft.Container(
                    content=empty_state("Sin trabajos aún", ft.Icons.WORK_OUTLINE),
                    padding=24, alignment=ft.Alignment(0, 0),
                ))
            else:
                # Resumen financiero
                trabajos_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text("Cobrado", size=11, color=TEXT_SEC),
                                ft.Text(f"${total_cobrado:,.2f}", size=16,
                                        color=GREEN, weight=ft.FontWeight.BOLD),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.VerticalDivider(color=TEXT_SEC, width=1),
                            ft.Column([
                                ft.Text("Pendiente", size=11, color=TEXT_SEC),
                                ft.Text(f"${total_pendiente:,.2f}", size=16,
                                        color=AMBER, weight=ft.FontWeight.BOLD),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.VerticalDivider(color=TEXT_SEC, width=1),
                            ft.Column([
                                ft.Text("Trabajos", size=11, color=TEXT_SEC),
                                ft.Text(str(len(trabajos)), size=16,
                                        color=ACCENT, weight=ft.FontWeight.BOLD),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                        bgcolor=NAVY_MID, border_radius=12, padding=12,
                        margin=ft.Margin.only(bottom=8),
                    )
                )

                for t in trabajos:
                    def toggle_estado(e, tid=t["id"], test=t["estado"]):
                        nuevo = "pagado" if test == "en_espera" else "en_espera"
                        db.update_trabajo_estado(tid, nuevo)
                        show_client_detail(cliente)

                    def del_trabajo(e, tid=t["id"]):
                        db.delete_trabajo(tid)
                        show_client_detail(cliente)

                    trabajos_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(t["fecha"], size=10, color=TEXT_SEC),
                                    ft.Container(expand=True),
                                    estado_badge(t["estado"]),
                                ]),
                                ft.Text(t["descripcion"], size=13, color=TEXT_WHITE),
                                ft.Row([
                                    ft.Text(f"${t['monto']:,.2f}", size=15,
                                            color=GREEN if t["estado"] == "pagado" else AMBER,
                                            weight=ft.FontWeight.BOLD),
                                    ft.Container(expand=True),
                                    ft.TextButton(
                                        "✓ Pagado" if t["estado"] == "en_espera"
                                        else "↩ Pendiente",
                                        on_click=toggle_estado,
                                        style=ft.ButtonStyle(
                                            color=GREEN if t["estado"] == "en_espera" else AMBER,
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, icon_color=RED,
                                        icon_size=16, on_click=del_trabajo,
                                    ),
                                ], spacing=0),
                            ], spacing=6),
                            bgcolor=NAVY_MID, border_radius=12, padding=12,
                            border=ft.Border.all(
                                1,
                                ft.Colors.with_opacity(0.20, GREEN if t["estado"] == "pagado"
                                                       else AMBER),
                            ),
                            margin=ft.Margin.only(bottom=6),
                        )
                    )

        load_trabajos()

        # Header carpeta
        main_area.controls.extend([
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS, icon_color=TEXT_WHITE,
                    on_click=lambda e: show_clients_list(),
                    icon_size=20,
                ),
                ft.Container(
                    content=ft.Text(cliente["nombre"][0].upper(), size=16,
                                    color=TEXT_WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=ACCENT, border_radius=20, width=38, height=38,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(cliente["nombre"], size=16,
                            weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    ft.Text(cliente.get("telefono", "") or "Sin teléfono",
                            size=11, color=TEXT_SEC),
                ], spacing=2, expand=True),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD, bgcolor=ACCENT, foreground_color=TEXT_WHITE,
                    on_click=toggle_trabajo_form, mini=True,
                    tooltip="Agregar trabajo",
                ),
            ], spacing=10),
            ft.Container(height=6),
            trabajo_form,
            ft.Container(height=4),
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color=AMBER),
                ft.Text("Historial de trabajos", size=13,
                        weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
            ], spacing=6),
            ft.Container(height=4),
            trabajos_list,
        ])
        page.update()

    # ── Layout base ────────────────────────────────────────
    view = ft.Container(
        content=ft.Column([main_area], expand=True, scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    # Carga inicial
    show_clients_list()

    def refresh():
        if active_cliente[0]:
            show_client_detail(active_cliente[0])
        else:
            show_clients_list()

    view.refresh = refresh  # type: ignore
    return view
