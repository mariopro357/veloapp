"""
VeloApp — Opción 6: Horarios de Trabajo
Genera un horario personalizado evitando comer en la calle y promoviendo descanso
"""
import flet as ft
from src.db import database as db
from src.utils.theme import (
    NAVY_DARK, NAVY_MID, ACCENT, TEXT_WHITE, TEXT_SEC,
    GREEN, AMBER, RED, WORK_TYPES,
    section_title, sub_text, show_snack
)

# Colores de bloques del horario
BLOCK_COLORS = {
    "work":     ("#1E4D8C", "🔧"),
    "meal":     ("#1A6B4A", "🍳"),
    "personal": ("#4A2D6B", "🚿"),
    "rest":     ("#5D4A1A", "😴"),
    "sleep":    ("#0D1F3C", "💤"),
    "wake":     ("#3D2B00", "🌅"),
}

DAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _generate_schedule(work_type: str, start_h: int, end_h: int) -> list[dict]:
    """Genera bloques de horario optimizados."""
    blocks = []

    # Despertar 1h antes del trabajo (mínimo 5am)
    wake_h = max(start_h - 1, 5)

    if wake_h < start_h:
        blocks.append({
            "time": f"{wake_h:02d}:00",
            "label": "Despertar — Preparar desayuno en casa",
            "duration": "45 min",
            "type": "wake",
        })
        blocks.append({
            "time": f"{wake_h:02d}:45",
            "label": "Aseo personal y alistarse",
            "duration": "15 min",
            "type": "personal",
        })

    # Primera parte del trabajo
    mid_h = (start_h + end_h) // 2
    blocks.append({
        "time": f"{start_h:02d}:00",
        "label": f"Trabajo — {work_type}",
        "duration": f"{mid_h - start_h}h",
        "type": "work",
    })

    # Pausa de almuerzo (en casa)
    blocks.append({
        "time": f"{mid_h:02d}:00",
        "label": "Pausa almuerzo — Cocina en casa (ahorra dinero 💰)",
        "duration": "1h 30min",
        "type": "meal",
    })

    # Segunda parte del trabajo
    resume_h = mid_h + 1
    resume_m = 30
    blocks.append({
        "time": f"{resume_h:02d}:{resume_m:02d}",
        "label": f"Trabajo — {work_type}",
        "duration": f"{end_h - resume_h}h {60 - resume_m}min",
        "type": "work",
    })

    # Regreso a casa
    blocks.append({
        "time": f"{end_h:02d}:00",
        "label": "Llegada a casa — Preparar cena",
        "duration": "45 min",
        "type": "meal",
    })

    # Tiempo libre / familia
    rest_h = end_h
    # Hora de dormir: 8pm si llegó antes de las 6pm, sino 10pm
    sleep_h = 20 if end_h <= 18 else 22

    if rest_h + 1 < sleep_h:
        blocks.append({
            "time": f"{rest_h:02d}:45",
            "label": "Descanso — Familia, ocio y preparación del mañana",
            "duration": f"{sleep_h - rest_h - 1}h 15min",
            "type": "rest",
        })

    blocks.append({
        "time": f"{sleep_h:02d}:00",
        "label": "🌙 Dormir — Recuperación para mañana",
        "duration": "8h",
        "type": "sleep",
    })

    return blocks


def build_horarios_view(page: ft.Page) -> ft.Container:

    schedule_area = ft.Column(spacing=6)
    config_area = ft.Column(spacing=8)
    view_mode = [None]   # None = config | "schedule" = horario generado

    # ── Onboarding / Config ────────────────────────────────
    work_type_dd = ft.Dropdown(
        label="¿En qué trabajas?",
        label_style=ft.TextStyle(color=TEXT_SEC, size=12),
        text_style=ft.TextStyle(color=TEXT_WHITE, size=13),
        border_color=ACCENT, focused_border_color=ACCENT,
        bgcolor=NAVY_DARK, border_radius=10,
        options=[ft.dropdown.Option(w) for w in WORK_TYPES],
        value=WORK_TYPES[0],
    )

    # Hora inicio/fin con sliders
    start_h_val = [7]
    end_h_val = [17]

    start_label = ft.Text(f"Inicio laboral: 07:00 AM", size=13,
                          color=TEXT_WHITE, weight=ft.FontWeight.W_500)
    end_label = ft.Text(f"Fin laboral: 05:00 PM", size=13,
                        color=TEXT_WHITE, weight=ft.FontWeight.W_500)

    def fmt_hour(h: int) -> str:
        suffix = "AM" if h < 12 else "PM"
        hh = h if h <= 12 else h - 12
        hh = 12 if hh == 0 else hh
        return f"{hh:02d}:00 {suffix}"

    def on_start_change(e):
        v = int(e.control.value)
        start_h_val[0] = v
        start_label.value = f"Inicio laboral: {fmt_hour(v)}"
        start_label.update()

    def on_end_change(e):
        v = int(e.control.value)
        end_h_val[0] = v
        end_label.value = f"Fin laboral: {fmt_hour(v)}"
        end_label.update()

    start_slider = ft.Slider(
        min=4, max=12, divisions=8,
        value=7, active_color=ACCENT,
        inactive_color=ft.Colors.with_opacity(0.2, ACCENT),
        label="{value}h",
        on_change=on_start_change,
    )
    end_slider = ft.Slider(
        min=13, max=22, divisions=9,
        value=17, active_color=GREEN,
        inactive_color=ft.Colors.with_opacity(0.2, GREEN),
        label="{value}h",
        on_change=on_end_change,
    )

    def build_config_form():
        config_area.controls.clear()
        saved_type   = db.get_config("horario_work_type", "")
        saved_start  = db.get_config("horario_start",     "7")
        saved_end    = db.get_config("horario_end",       "17")

        if saved_type:
            work_type_dd.value = saved_type
        if saved_start:
            start_slider.value = int(saved_start)
            start_h_val[0] = int(saved_start)
            start_label.value = f"Inicio laboral: {fmt_hour(int(saved_start))}"
        if saved_end:
            end_slider.value = int(saved_end)
            end_h_val[0] = int(saved_end)
            end_label.value = f"Fin laboral: {fmt_hour(int(saved_end))}"

        config_area.controls.extend([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, size=18, color=ACCENT),
                        ft.Text("Configura tu horario", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                    ], spacing=8),
                    sub_text(
                        "El app organizará tu día para que comas en casa "
                        "y descanses bien 💪"
                    ),
                ], spacing=6),
                bgcolor=ft.Colors.with_opacity(0.07, ACCENT),
                border_radius=14, padding=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ACCENT)),
            ),
            work_type_dd,
            ft.Container(
                content=ft.Column([
                    start_label,
                    start_slider,
                    ft.Text("Desliza para ajustar hora de entrada",
                            size=10, color=TEXT_SEC),
                ], spacing=4),
                bgcolor=NAVY_MID, border_radius=12, padding=12,
            ),
            ft.Container(
                content=ft.Column([
                    end_label,
                    end_slider,
                    ft.Text("Desliza para ajustar hora de salida",
                            size=10, color=TEXT_SEC),
                ], spacing=4),
                bgcolor=NAVY_MID, border_radius=12, padding=12,
            ),
            ft.ElevatedButton(
                "🗓️ Generar mi horario",
                on_click=generate_schedule,
                bgcolor=ACCENT, color=TEXT_WHITE,
                expand=True,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding.symmetric(vertical=14),
                ),
            ),
        ])

    def generate_schedule(e=None):
        start = start_h_val[0]
        end   = end_h_val[0]
        wtype = work_type_dd.value or WORK_TYPES[0]

        if end <= start:
            show_snack(page, "La hora de salida debe ser después de la entrada", RED)
            return

        # Guardar config
        db.set_config("horario_work_type", wtype)
        db.set_config("horario_start",     str(start))
        db.set_config("horario_end",       str(end))

        blocks = _generate_schedule(wtype, start, end)
        view_mode[0] = "schedule"
        show_schedule(blocks, wtype, start, end)

    def show_schedule(blocks: list, wtype: str, start: int, end: int):
        schedule_area.controls.clear()
        schedule_area.controls.append(
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.EDIT, icon_color=TEXT_SEC, icon_size=18,
                    on_click=lambda e: show_config_mode(),
                    tooltip="Editar horario",
                ),
                section_title(f"Horario — {wtype.split('/')[0].strip()}", size=15),
            ], spacing=6)
        )
        schedule_area.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=AMBER),
                    ft.Text(
                        f"Entrada: {fmt_hour(start)} — Salida: {fmt_hour(end)} "
                        f"· Venezuela (UTC-4)",
                        size=11, color=TEXT_SEC,
                    ),
                ], spacing=6),
            )
        )
        schedule_area.controls.append(ft.Container(height=6))

        for bloc in blocks:
            bg, emoji = BLOCK_COLORS.get(bloc["type"], (NAVY_MID, "⏰"))
            schedule_area.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(bloc["time"], size=13,
                                        color=TEXT_WHITE, weight=ft.FontWeight.BOLD),
                                ft.Text(emoji, size=20),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                               spacing=2),
                            width=70,
                        ),
                        ft.Container(width=1, bgcolor=ft.Colors.with_opacity(0.3, TEXT_SEC),
                                     height=50),
                        ft.Column([
                            ft.Text(bloc["label"], size=13, color=TEXT_WHITE,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(bloc["duration"], size=11, color=TEXT_SEC),
                        ], spacing=3, expand=True),
                    ], spacing=10),
                    bgcolor=bg,
                    border_radius=12, padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    margin=ft.Margin.only(bottom=4),
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.12, TEXT_WHITE)),
                )
            )

        # Tip al final
        schedule_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.LIGHTBULB, size=16, color=AMBER),
                            ft.Text("Consejo del app", size=13,
                                    color=AMBER, weight=ft.FontWeight.BOLD)], spacing=6),
                    ft.Text(
                        "Cocinar en casa diariamente puede ahorrarte más de "
                        "$150/mes versus comer en la calle. ¡Tu billetera te lo agradece! 🍽️",
                        size=12, color=TEXT_SEC,
                    ),
                ], spacing=6),
                bgcolor=ft.Colors.with_opacity(0.07, AMBER),
                border_radius=12, padding=12,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.18, AMBER)),
                margin=ft.Margin.only(top=6),
            )
        )
        page.update()

    def show_config_mode():
        view_mode[0] = None
        schedule_area.controls.clear()
        build_config_form()
        page.update()

    # ── Layout ─────────────────────────────────────────────
    main_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=6, expand=True)
    main_col.controls.extend([
        ft.Row([
            ft.Icon(ft.Icons.SCHEDULE, size=22, color=ACCENT),
            section_title("Mi Horario de Trabajo", size=18),
        ], spacing=8),
        sub_text("Diseñado para tu rutina y tu bolsillo"),
        ft.Container(height=8),
        config_area,
        schedule_area,
    ])

    view = ft.Container(
        content=main_col,
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    # Verificar si ya hay horario guardado
    saved = db.get_config("horario_work_type", "")
    if saved:
        st = int(db.get_config("horario_start", "7"))
        en = int(db.get_config("horario_end", "17"))
        work_type_dd.value = saved
        start_h_val[0] = st
        end_h_val[0] = en
        blocks = _generate_schedule(saved, st, en)
        view_mode[0] = "schedule"
        show_schedule(blocks, saved, st, en)
    else:
        build_config_form()

    def refresh():
        if view_mode[0] == "schedule":
            wt = db.get_config("horario_work_type", WORK_TYPES[0])
            st = int(db.get_config("horario_start", "7"))
            en = int(db.get_config("horario_end", "17"))
            blocks = _generate_schedule(wt, st, en)
            show_schedule(blocks, wt, st, en)
        else:
            show_config_mode()

    view.refresh = refresh  # type: ignore
    return view
