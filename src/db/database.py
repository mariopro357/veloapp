"""
VeloApp — Módulo de Base de Datos SQLite
Toda la persistencia de datos de la app
"""
import sqlite3
import os
import json
from datetime import datetime


# =========================================================
# CONEXIÓN Y RUTA
# =========================================================

def get_db_path() -> str:
    """Ruta del archivo DB — funciona en escritorio y Android."""
    db_dir = os.environ.get(
        "FLET_APP_STORAGE_DATA",
        os.path.join(os.path.expanduser("~"), ".veloapp")
    )
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "veloapp.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =========================================================
# INICIALIZAR TABLAS
# =========================================================

def init_db():
    """Crea todas las tablas si no existen."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS facturas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                mes         INTEGER NOT NULL,
                anio        INTEGER NOT NULL,
                fecha       TEXT    NOT NULL,
                titulo      TEXT,
                raw_text    TEXT,
                items_json  TEXT,
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS gastos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                mes         INTEGER NOT NULL,
                anio        INTEGER NOT NULL,
                categoria   TEXT    NOT NULL,
                descripcion TEXT,
                monto       REAL    NOT NULL,
                fecha       TEXT    NOT NULL,
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre         TEXT    NOT NULL,
                telefono       TEXT    DEFAULT '',
                notas          TEXT    DEFAULT '',
                fecha_creacion TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS trabajos_cliente (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id  INTEGER NOT NULL,
                fecha       TEXT    NOT NULL,
                descripcion TEXT    NOT NULL,
                monto       REAL    NOT NULL,
                estado      TEXT    DEFAULT 'pendiente',
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS creditos (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre         TEXT    NOT NULL,
                costo_total    REAL    NOT NULL,
                cuota_mensual  REAL    NOT NULL,
                monto_pagado   REAL    DEFAULT 0,
                completado     INTEGER DEFAULT 0,
                fecha_inicio   TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ahorros (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo        TEXT    NOT NULL,
                monto       REAL    NOT NULL,
                descripcion TEXT    DEFAULT '',
                fecha       TEXT    NOT NULL,
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ingresos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha        TEXT    NOT NULL,
                tipo_trabajo TEXT    NOT NULL,
                descripcion  TEXT    DEFAULT '',
                monto        REAL    NOT NULL,
                created_at   TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS user_config (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        # Migraciones / actualizaciones de esquemas existentes
        # Asegurar columnas nuevas en trabajos_cliente
        try:
            conn.execute("ALTER TABLE trabajos_cliente ADD COLUMN monto_pagado REAL DEFAULT 0")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE trabajos_cliente ADD COLUMN fecha_pago TEXT")
        except Exception:
            pass
        # Crear tabla de pagos por trabajo (para registrar abonos parciales)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pagos_trabajo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trabajo_id INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    fecha TEXT NOT NULL,
                    FOREIGN KEY (trabajo_id) REFERENCES trabajos_cliente(id) ON DELETE CASCADE
                );
                """
            )
        except Exception:
            pass


# =========================================================
# CONFIGS DE USUARIO
# =========================================================

def set_config(key: str, value: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_config (key, value) VALUES (?, ?)",
            (key, str(value))
        )


def get_config(key: str, default=None):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM user_config WHERE key=?", (key,)
        ).fetchone()
    return row["value"] if row else default


# =========================================================
# ABONOS A TRABAJOS
# =========================================================

def pagar_trabajo(trabajo_id: int, monto: float):
    with get_connection() as conn:
        # Registrar abono
        now = __import__('datetime').datetime.now().strftime("%Y-%m-%d")
        conn.execute(
            "UPDATE trabajos_cliente SET monto_pagado = COALESCE(monto_pagado, 0) + ?, fecha_pago = ? WHERE id=?",
            (monto, now, trabajo_id)
        )
        # Añadir registro de pago en historia
        conn.execute(
            "INSERT INTO pagos_trabajo (trabajo_id, monto, fecha) VALUES (?,?,?)",
            (trabajo_id, monto, now)
        )
        # Actualizar estado si ya se pagó por completo
        row = conn.execute("SELECT monto, monto_pagado FROM trabajos_cliente WHERE id=?", (trabajo_id,)).fetchone()
        if row and row["monto_pagado"] >= row["monto"]:
            conn.execute("UPDATE trabajos_cliente SET estado='pagado' WHERE id=?", (trabajo_id,))


def get_gastos_semana():
    now = __import__('datetime').datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM gastos WHERE strftime('%W', fecha) = strftime('%W', ?) AND strftime('%Y', fecha) = strftime('%Y', ?)",
            (date_str, date_str)
        ).fetchone()
    return float(row["total"])


def get_gastos_semana_all():
    return get_gastos_semana()


def get_ingresos_semana():
    now = __import__('datetime').datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(p.monto), 0) AS total FROM pagos_trabajo p WHERE strftime('%W', p.fecha) = strftime('%W', ?) AND strftime('%Y', p.fecha) = strftime('%Y', ?)",
            (date_str, date_str)
        ).fetchone()
    return float(row["total"])


def get_ingresos_mes():
    now = __import__('datetime').datetime.now()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(p.monto), 0) AS total FROM pagos_trabajo p WHERE strftime('%Y-%m', p.fecha) = strftime('%Y-%m', ?)",
            (now.strftime("%Y-%m-%d"),)
        ).fetchone()
    return float(row["total"])


def get_total_ingresos_alltime():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto_pagado), 0) AS total FROM trabajos_cliente"
        ).fetchone()
    return float(row["total"])


def get_disponible():
    with get_connection() as conn:
        total_pagado_row = conn.execute("SELECT COALESCE(SUM(monto_pagado), 0) AS total FROM trabajos_cliente").fetchone()
        total_gastos_row = conn.execute("SELECT COALESCE(SUM(monto), 0) AS total FROM gastos").fetchone()
    total_pagado = float(total_pagado_row["total"]) if total_pagado_row else 0.0
    total_gastos = float(total_gastos_row["total"]) if total_gastos_row else 0.0
    return float(total_pagado - total_gastos)


def get_total_pendiente_cliente(cliente_id: int) -> float:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto - IFNULL(monto_pagado, 0)), 0) AS total FROM trabajos_cliente WHERE cliente_id=?",
            (cliente_id,)
        ).fetchone()
    return float(row["total"])


# =========================================================
# FACTURAS
# =========================================================

def save_factura(titulo: str, raw_text: str, items: list):
    now = datetime.now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO facturas (mes, anio, fecha, titulo, raw_text, items_json) VALUES (?,?,?,?,?,?)",
            (now.month, now.year, now.strftime("%Y-%m-%d"),
             titulo, raw_text, json.dumps(items, ensure_ascii=False))
        )


def get_facturas_mes(mes: int = None, anio: int = None) -> list:
    now = datetime.now()
    mes = mes or now.month
    anio = anio or now.year
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM facturas WHERE mes=? AND anio=? ORDER BY created_at DESC",
            (mes, anio)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["items"] = json.loads(d.get("items_json") or "[]")
        result.append(d)
    return result


def delete_factura(factura_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM facturas WHERE id=?", (factura_id,))


# =========================================================
# GASTOS
# =========================================================

def save_gasto(categoria: str, descripcion: str, monto: float):
    now = datetime.now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO gastos (mes, anio, categoria, descripcion, monto, fecha) VALUES (?,?,?,?,?,?)",
            (now.month, now.year, categoria, descripcion, monto, now.strftime("%Y-%m-%d"))
        )


def get_gastos_mes(mes: int = None, anio: int = None) -> list:
    now = datetime.now()
    mes = mes or now.month
    anio = anio or now.year
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM gastos WHERE mes=? AND anio=? ORDER BY created_at DESC",
            (mes, anio)
        ).fetchall()
    return [dict(r) for r in rows]


def get_total_gastos_mes(mes: int = None, anio: int = None) -> float:
    now = datetime.now()
    mes = mes or now.month
    anio = anio or now.year
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM gastos WHERE mes=? AND anio=?",
            (mes, anio)
        ).fetchone()
    return float(row["total"])


def delete_gasto(gasto_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM gastos WHERE id=?", (gasto_id,))


# =========================================================
# CLIENTES
# =========================================================

def create_cliente(nombre: str, telefono: str = "", notas: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO clientes (nombre, telefono, notas) VALUES (?,?,?)",
            (nombre, telefono, notas)
        )
        return cursor.lastrowid


def get_clientes() -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM clientes ORDER BY nombre COLLATE NOCASE"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_cliente(cliente_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM trabajos_cliente WHERE cliente_id=?", (cliente_id,))
        conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))


def create_trabajo(cliente_id: int, descripcion: str, monto: float) -> int:
    now = datetime.now()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO trabajos_cliente (cliente_id, fecha, descripcion, monto, monto_pagado, estado) VALUES (?,?,?,?,?,?)",
            (cliente_id, now.strftime("%Y-%m-%d"), descripcion, monto, 0, "pendiente")
        )
        return cursor.lastrowid


def get_trabajos_cliente(cliente_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM trabajos_cliente WHERE cliente_id=? ORDER BY created_at DESC",
            (cliente_id,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        mp = d.get("monto_pagado") or 0
        d["monto_pagado"] = float(mp)
        restante = d.get("monto") - d["monto_pagado"]
        d["restante"] = float(restante if restante >= 0 else 0)
        result.append(d)
    return result


def update_trabajo_estado(trabajo_id: int, estado: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE trabajos_cliente SET estado=? WHERE id=?", (estado, trabajo_id)
        )


def delete_trabajo(trabajo_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM trabajos_cliente WHERE id=?", (trabajo_id,))


def get_total_pendiente_cliente(cliente_id: int) -> float:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto - COALESCE(monto_pagado, 0)), 0) AS total FROM trabajos_cliente "
            "WHERE cliente_id=? AND estado='pendiente'",
            (cliente_id,)
        ).fetchone()
    return float(row["total"])


# =========================================================
# CRÉDITOS
# =========================================================

def create_credito(nombre: str, costo_total: float, cuota_mensual: float) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO creditos (nombre, costo_total, cuota_mensual) VALUES (?,?,?)",
            (nombre, costo_total, cuota_mensual)
        )
        return cursor.lastrowid


def get_creditos(solo_activos: bool = False) -> list:
    with get_connection() as conn:
        if solo_activos:
            rows = conn.execute(
                "SELECT * FROM creditos WHERE completado=0 ORDER BY fecha_inicio DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM creditos ORDER BY completado ASC, fecha_inicio DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def pagar_cuota_credito(credito_id: int, monto: float):
    with get_connection() as conn:
        conn.execute(
            "UPDATE creditos SET monto_pagado = MIN(monto_pagado + ?, costo_total) WHERE id=?",
            (monto, credito_id)
        )
        row = conn.execute(
            "SELECT monto_pagado, costo_total FROM creditos WHERE id=?", (credito_id,)
        ).fetchone()
        if row and row["monto_pagado"] >= row["costo_total"]:
            conn.execute("UPDATE creditos SET completado=1 WHERE id=?", (credito_id,))


def completar_credito(credito_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE creditos SET completado=1, monto_pagado=costo_total WHERE id=?",
            (credito_id,)
        )


def delete_credito(credito_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM creditos WHERE id=?", (credito_id,))


# =========================================================
# AHORROS
# =========================================================

def registrar_ahorro(tipo: str, monto: float, descripcion: str = ""):
    """tipo = 'ahorro' | 'gasto'"""
    now = datetime.now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO ahorros (tipo, monto, descripcion, fecha) VALUES (?,?,?,?)",
            (tipo, abs(monto), descripcion, now.strftime("%Y-%m-%d"))
        )


def get_total_ahorros() -> float:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='ahorro' THEN monto ELSE -monto END), 0) AS total "
            "FROM ahorros"
        ).fetchone()
    return float(row["total"])


def get_movimientos_ahorros(limit: int = 50) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM ahorros ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# =========================================================
# INGRESOS
# =========================================================

def registrar_ingreso(tipo_trabajo: str, descripcion: str, monto: float):
    now = datetime.now()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO ingresos (fecha, tipo_trabajo, descripcion, monto) VALUES (?,?,?,?)",
            (now.strftime("%Y-%m-%d"), tipo_trabajo, descripcion, monto)
        )


def get_ingresos_mes(mes: int = None, anio: int = None) -> list:
    now = datetime.now()
    mes = mes or now.month
    anio = anio or now.year
    prefix = f"{anio}-{mes:02d}"
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM ingresos WHERE fecha LIKE ? ORDER BY fecha DESC, created_at DESC",
            (f"{prefix}%",)
        ).fetchall()
    return [dict(r) for r in rows]


def get_total_ingresos_mes(mes: int = None, anio: int = None) -> float:
    now = datetime.now()
    mes = mes or now.month
    anio = anio or now.year
    prefix = f"{anio}-{mes:02d}"
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM ingresos WHERE fecha LIKE ?",
            (f"{prefix}%",)
        ).fetchone()
    return float(row["total"])


def get_total_ingresos_hoy() -> float:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM ingresos WHERE fecha=?",
            (today,)
        ).fetchone()
    return float(row["total"])


def delete_ingreso(ingreso_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM ingresos WHERE id=?", (ingreso_id,))
