import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Any

# Añadir el raíz actual al sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Importar funciones de base de datos
from src.db.database import (
    init_db,
    # Clientes
    create_cliente, get_clientes, delete_cliente,
    create_trabajo, get_trabajos_cliente, update_trabajo_estado, delete_trabajo, get_total_pendiente_cliente,
    # Gastos
    save_gasto, get_gastos_mes, get_total_gastos_mes, delete_gasto,
    # Créditos
    create_credito, get_creditos, pagar_cuota_credito, completar_credito, delete_credito,
    # Ahorros
    registrar_ahorro, get_total_ahorros, get_movimientos_ahorros,
    # Ingresos
    registrar_ingreso, get_ingresos_mes, get_total_ingresos_mes, get_total_ingresos_hoy, delete_ingreso
)

app = FastAPI(title="VeloApp API")

# Inicializa DB al arrancar
@app.on_event("startup")
def startup_event():
    init_db()

# ================================
# MODELOS PYDANTIC
# ================================
class ClienteIn(BaseModel):
    nombre: str
    telefono: str = ""
    notas: str = ""

class TrabajoIn(BaseModel):
    cliente_id: int
    descripcion: str
    monto: float

class TrabajoEstadoIn(BaseModel):
    estado: str

class GastoIn(BaseModel):
    categoria: str
    descripcion: str
    monto: float

class CreditoIn(BaseModel):
    nombre: str
    costo_total: float
    cuota_mensual: float

class PagoCreditoIn(BaseModel):
    monto: float

class AhorroIn(BaseModel):
    tipo: str # "ahorro" o "gasto"
    monto: float
    descripcion: str = ""

class IngresoIn(BaseModel):
    tipo_trabajo: str
    descripcion: str = ""
    monto: float

# ================================
# RUTAS API
# ================================

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

# --- CLIENTES ---
@app.get("/api/clientes")
def api_get_clientes():
    return {"data": get_clientes()}

@app.post("/api/clientes")
def api_create_cliente(c: ClienteIn):
    cid = create_cliente(c.nombre, c.telefono, c.notas)
    return {"status": "success", "id": cid}

@app.delete("/api/clientes/{cliente_id}")
def api_delete_cliente(cliente_id: int):
    delete_cliente(cliente_id)
    return {"status": "success"}

# --- TRABAJOS DE CLIENTES ---
@app.get("/api/clientes/{cliente_id}/trabajos")
def api_get_trabajos(cliente_id: int):
    return {"data": get_trabajos_cliente(cliente_id)}

@app.post("/api/trabajos")
def api_create_trabajo(t: TrabajoIn):
    tid = create_trabajo(t.cliente_id, t.descripcion, t.monto)
    return {"status": "success", "id": tid}

@app.put("/api/trabajos/{trabajo_id}/estado")
def api_update_estado(trabajo_id: int, te: TrabajoEstadoIn):
    update_trabajo_estado(trabajo_id, te.estado)
    return {"status": "success"}

@app.get("/api/clientes/{cliente_id}/total_pendiente")
def api_get_pendiente(cliente_id: int):
    return {"total": get_total_pendiente_cliente(cliente_id)}

# --- GASTOS ---
@app.get("/api/gastos")
def api_get_gastos():
    return {"data": get_gastos_mes()}

@app.get("/api/gastos/total")
def api_get_total_gastos():
    return {"total": get_total_gastos_mes()}

@app.post("/api/gastos")
def api_create_gasto(g: GastoIn):
    save_gasto(g.categoria, g.descripcion, g.monto)
    return {"status": "success"}

@app.delete("/api/gastos/{gasto_id}")
def api_delete_gasto(gasto_id: int):
    delete_gasto(gasto_id)
    return {"status": "success"}

# --- CRÉDITOS ---
@app.get("/api/creditos")
def api_get_creditos_all():
    return {"data": get_creditos(solo_activos=False)}

@app.post("/api/creditos")
def api_create_credito(c: CreditoIn):
    cid = create_credito(c.nombre, c.costo_total, c.cuota_mensual)
    return {"status": "success", "id": cid}

@app.post("/api/creditos/{credito_id}/pagar")
def api_pagar_credito(credito_id: int, p: PagoCreditoIn):
    pagar_cuota_credito(credito_id, p.monto)
    return {"status": "success"}

@app.post("/api/creditos/{credito_id}/completar")
def api_completar_cred(credito_id: int):
    completar_credito(credito_id)
    return {"status": "success"}

@app.delete("/api/creditos/{credito_id}")
def api_del_credito(credito_id: int):
    delete_credito(credito_id)
    return {"status": "success"}

# --- AHORROS ---
@app.get("/api/ahorros/total")
def api_get_tot_ahorros():
    return {"total": get_total_ahorros()}

@app.get("/api/ahorros/movimientos")
def api_get_movs():
    return {"data": get_movimientos_ahorros()}

@app.post("/api/ahorros")
def api_reg_ahorro(a: AhorroIn):
    registrar_ahorro(a.tipo, a.monto, a.descripcion)
    return {"status": "success"}

# --- INGRESOS ---
@app.get("/api/ingresos")
def api_get_ingresos():
    return {"data": get_ingresos_mes()}

@app.get("/api/ingresos/total")
def api_get_tot_ingresos():
    return {"total": get_total_ingresos_mes()}

@app.post("/api/ingresos")
def api_reg_ingreso(i: IngresoIn):
    registrar_ingreso(i.tipo_trabajo, i.descripcion, i.monto)
    return {"status": "success"}

@app.delete("/api/ingresos/{ingreso_id}")
def api_del_ingreso(ingreso_id: int):
    delete_ingreso(ingreso_id)
    return {"status": "success"}

# ================================
# FRONTEND STATIC FILES
# ================================
# Monta la carpeta frontend en la raíz para servir el HTML/JS/CSS
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Inicia el sevidor automáticamente al ejecutar `python server.py`
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
