"""
_db.py — Capa de datos SQLite para SalazAnalytics
Multi-empresa: cada registro está asociado a un nit_empresa.
Base de datos: /data/salazanalytics.db (persistente en el VPS)
Fallback: /tmp/salazanalytics.db (si /data no existe)
"""
import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime, date

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

def _db_path() -> str:
    data_dir = Path("/data")
    if data_dir.exists() and os.access(data_dir, os.W_OK):
        return str(data_dir / "salazanalytics.db")
    return "/tmp/salazanalytics.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

# ─────────────────────────────────────────────
# INICIALIZACIÓN — crea tablas si no existen
# ─────────────────────────────────────────────

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        -- Empresas (tenants)
        CREATE TABLE IF NOT EXISTS empresas (
            nit          TEXT PRIMARY KEY,
            nombre       TEXT NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan         TEXT DEFAULT 'basico',
            activo       INTEGER DEFAULT 1,
            ciudad       TEXT DEFAULT 'Pereira',
            direccion    TEXT DEFAULT '',
            telefono     TEXT DEFAULT '',
            regimen      TEXT DEFAULT 'SIMPLE',
            actividad    TEXT DEFAULT 'Servicios profesionales y consultoría',
            fecha_registro TEXT DEFAULT (date('now')),
            ultimo_acceso  TEXT DEFAULT (date('now'))
        );

        -- Movimientos contables
        CREATE TABLE IF NOT EXISTS movimientos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nit_empresa  TEXT NOT NULL REFERENCES empresas(nit),
            fecha        TEXT NOT NULL,
            tipo         TEXT NOT NULL CHECK(tipo IN ('Ingreso','Gasto')),
            categoria    TEXT NOT NULL,
            descripcion  TEXT NOT NULL,
            valor        REAL NOT NULL,
            iva          REAL NOT NULL DEFAULT 0,
            valor_iva    REAL NOT NULL DEFAULT 0,
            total        REAL NOT NULL,
            creado_en    TEXT DEFAULT (datetime('now'))
        );

        -- Facturas emitidas
        CREATE TABLE IF NOT EXISTS facturas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nit_empresa     TEXT NOT NULL REFERENCES empresas(nit),
            numero          TEXT NOT NULL,
            fecha           TEXT NOT NULL,
            fecha_vence     TEXT NOT NULL,
            cliente_nombre  TEXT NOT NULL,
            cliente_nit     TEXT DEFAULT '',
            cliente_email   TEXT DEFAULT '',
            cliente_dir     TEXT DEFAULT '',
            items_json      TEXT NOT NULL,
            notas           TEXT DEFAULT '',
            subtotal        REAL NOT NULL DEFAULT 0,
            total_iva       REAL NOT NULL DEFAULT 0,
            total           REAL NOT NULL DEFAULT 0,
            creado_en       TEXT DEFAULT (datetime('now'))
        );

        -- Empleados
        CREATE TABLE IF NOT EXISTS empleados (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nit_empresa     TEXT NOT NULL REFERENCES empresas(nit),
            nombre          TEXT NOT NULL,
            cargo           TEXT DEFAULT '',
            salario         REAL NOT NULL,
            fecha_ingreso   TEXT NOT NULL,
            activo          INTEGER DEFAULT 1,
            aux_transporte  INTEGER DEFAULT 1,
            creado_en       TEXT DEFAULT (datetime('now'))
        );

        -- Índices para rendimiento
        CREATE INDEX IF NOT EXISTS idx_mov_empresa ON movimientos(nit_empresa);
        CREATE INDEX IF NOT EXISTS idx_mov_fecha   ON movimientos(fecha);
        CREATE INDEX IF NOT EXISTS idx_fac_empresa ON facturas(nit_empresa);
        CREATE INDEX IF NOT EXISTS idx_emp_empresa ON empleados(nit_empresa);
        """)

# ─────────────────────────────────────────────
# EMPRESAS
# ─────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def empresa_crear(nit: str, nombre: str, email: str, password: str, **kwargs) -> bool:
    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO empresas (nit, nombre, email, password_hash, ciudad,
                   direccion, telefono, regimen, actividad)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nit.strip(), nombre.strip(), email.strip().lower(), _hash(password),
                 kwargs.get("ciudad", "Pereira"),
                 kwargs.get("direccion", ""),
                 kwargs.get("telefono", ""),
                 kwargs.get("regimen", "SIMPLE"),
                 kwargs.get("actividad", "Servicios profesionales y consultoría"))
            )
        return True
    except sqlite3.IntegrityError:
        return False

def empresa_login(email: str, password: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM empresas WHERE email=? AND password_hash=? AND activo=1",
            (email.strip().lower(), _hash(password))
        ).fetchone()
        if row:
            conn.execute("UPDATE empresas SET ultimo_acceso=date('now') WHERE nit=?", (row["nit"],))
            return dict(row)
        return None

def empresa_get(nit: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM empresas WHERE nit=?", (nit,)).fetchone()
        return dict(row) if row else None

def empresa_actualizar(nit: str, **kwargs):
    campos = {k: v for k, v in kwargs.items()
              if k in ["nombre","email","ciudad","direccion","telefono","regimen","actividad"]}
    if not campos:
        return
    sets = ", ".join(f"{k}=?" for k in campos)
    with get_conn() as conn:
        conn.execute(f"UPDATE empresas SET {sets} WHERE nit=?",
                     list(campos.values()) + [nit])

def empresa_cambiar_password(nit: str, nueva: str):
    with get_conn() as conn:
        conn.execute("UPDATE empresas SET password_hash=? WHERE nit=?", (_hash(nueva), nit))

# ─────────────────────────────────────────────
# MOVIMIENTOS CONTABLES
# ─────────────────────────────────────────────

def movimiento_crear(nit_empresa: str, fecha: str, tipo: str, categoria: str,
                     descripcion: str, valor: float, iva: float,
                     valor_iva: float, total: float) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO movimientos
               (nit_empresa, fecha, tipo, categoria, descripcion, valor, iva, valor_iva, total)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nit_empresa, str(fecha), tipo, categoria, descripcion,
             valor, iva, valor_iva, total)
        )
        return cur.lastrowid

def movimientos_listar(nit_empresa: str, año: int = None,
                        mes: int = None, tipo: str = None) -> list[dict]:
    query = "SELECT * FROM movimientos WHERE nit_empresa=?"
    params = [nit_empresa]
    if año:
        query += " AND strftime('%Y', fecha)=?"
        params.append(str(año))
    if mes:
        query += " AND strftime('%m', fecha)=?"
        params.append(f"{mes:02d}")
    if tipo:
        query += " AND tipo=?"
        params.append(tipo)
    query += " ORDER BY fecha DESC, id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]

def movimiento_eliminar(id: int, nit_empresa: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM movimientos WHERE id=? AND nit_empresa=?",
                     (id, nit_empresa))

# ─────────────────────────────────────────────
# FACTURAS
# ─────────────────────────────────────────────

import json as _json

def factura_crear(nit_empresa: str, factura: dict) -> int:
    items = factura.get("items", [])
    subtotal  = sum(i["cantidad"] * i["valor_unitario"] for i in items)
    total_iva = sum(i["cantidad"] * i["valor_unitario"] * i["iva"] / 100 for i in items)
    total     = subtotal + total_iva
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO facturas
               (nit_empresa, numero, fecha, fecha_vence, cliente_nombre, cliente_nit,
                cliente_email, cliente_dir, items_json, notas, subtotal, total_iva, total)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nit_empresa, factura["numero"], str(factura["fecha"]),
             str(factura["fecha_vence"]), factura["cliente_nombre"],
             factura.get("cliente_nit",""), factura.get("cliente_email",""),
             factura.get("cliente_direccion",""), _json.dumps(items, ensure_ascii=False),
             factura.get("notas",""), subtotal, total_iva, total)
        )
        return cur.lastrowid

def facturas_listar(nit_empresa: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM facturas WHERE nit_empresa=? ORDER BY fecha DESC, id DESC",
            (nit_empresa,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["items"] = _json.loads(d["items_json"])
            result.append(d)
        return result

# ─────────────────────────────────────────────
# EMPLEADOS
# ─────────────────────────────────────────────

def empleado_crear(nit_empresa: str, nombre: str, cargo: str,
                   salario: float, fecha_ingreso: str,
                   aux_transporte: bool = True) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO empleados
               (nit_empresa, nombre, cargo, salario, fecha_ingreso, aux_transporte)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nit_empresa, nombre, cargo, salario, str(fecha_ingreso), int(aux_transporte))
        )
        return cur.lastrowid

def empleados_listar(nit_empresa: str) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM empleados WHERE nit_empresa=? AND activo=1 ORDER BY nombre",
            (nit_empresa,)
        ).fetchall()]

def empleado_eliminar(id: int, nit_empresa: str):
    with get_conn() as conn:
        conn.execute("UPDATE empleados SET activo=0 WHERE id=? AND nit_empresa=?",
                     (id, nit_empresa))

# ─────────────────────────────────────────────
# ESTADÍSTICAS RÁPIDAS
# ─────────────────────────────────────────────

def stats_empresa(nit_empresa: str, año: int = None) -> dict:
    año = año or date.today().year
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total_movimientos,
                COALESCE(SUM(CASE WHEN tipo='Ingreso' THEN total ELSE 0 END), 0) as total_ingresos,
                COALESCE(SUM(CASE WHEN tipo='Gasto'   THEN total ELSE 0 END), 0) as total_gastos,
                COALESCE(SUM(CASE WHEN tipo='Ingreso' THEN valor_iva ELSE 0 END), 0) as iva_cobrado,
                COALESCE(SUM(CASE WHEN tipo='Gasto'   THEN valor_iva ELSE 0 END), 0) as iva_pagado
            FROM movimientos
            WHERE nit_empresa=? AND strftime('%Y', fecha)=?
        """, (nit_empresa, str(año))).fetchone()

        facturas = conn.execute(
            "SELECT COUNT(*) as n, COALESCE(SUM(total),0) as t FROM facturas WHERE nit_empresa=? AND strftime('%Y', fecha)=?",
            (nit_empresa, str(año))
        ).fetchone()

    return {
        "total_movimientos": row["total_movimientos"],
        "total_ingresos":    row["total_ingresos"],
        "total_gastos":      row["total_gastos"],
        "utilidad":          row["total_ingresos"] - row["total_gastos"],
        "iva_cobrado":       row["iva_cobrado"],
        "iva_pagado":        row["iva_pagado"],
        "iva_neto":          row["iva_cobrado"] - row["iva_pagado"],
        "total_facturas":    facturas["n"],
        "facturado":         facturas["t"],
    }

# Inicializar al importar
init_db()
