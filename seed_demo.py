"""
seed_demo.py — Poblar base de datos con empresa demo realista
Ejecutar UNA sola vez en el VPS:
    python3 seed_demo.py

Crea la empresa demo y 6 meses de movimientos contables creíbles.
Login demo: demo@consultoriaeje.com / demo2026
"""

import sys
from pathlib import Path

# Asegurar que importa _db.py del mismo directorio
sys.path.insert(0, str(Path(__file__).parent))

import _db as db
from datetime import date

# ─────────────────────────────────────────────
# CONSTANTES 2026
# ─────────────────────────────────────────────
SMMLV     = 1_750_905
AUX_TRANS = 249_095
UVT       = 52_374

# ─────────────────────────────────────────────
# CREAR EMPRESA DEMO
# ─────────────────────────────────────────────
NIT   = "900987654"
EMAIL = "demo@consultoriaeje.com"
PASS  = "demo2026"

print("Inicializando base de datos...")
db.init_db()

# Eliminar empresa demo si ya existe (para re-ejecutar limpio)
with db.get_conn() as conn:
    conn.execute("DELETE FROM movimientos WHERE nit_empresa=?", (NIT,))
    conn.execute("DELETE FROM facturas    WHERE nit_empresa=?", (NIT,))
    conn.execute("DELETE FROM empleados   WHERE nit_empresa=?", (NIT,))
    conn.execute("DELETE FROM empresas    WHERE nit=?",         (NIT,))

ok = db.empresa_crear(
    nit      = NIT,
    nombre   = "Consultoría Empresarial del Eje S.A.S.",
    email    = EMAIL,
    password = PASS,
    ciudad   = "Pereira",
    direccion= "Cra 8 # 19-20 Of. 304, Centro Empresarial Pereira",
    telefono = "3156789012",
    regimen  = "SIMPLE",
    actividad= "Servicios profesionales y consultoría",
)
print(f"Empresa creada: {'✅' if ok else '❌ ya existe'}")

# ─────────────────────────────────────────────
# EMPLEADOS
# ─────────────────────────────────────────────
empleados = [
    ("Ana María Salazar",  "Directora de Proyectos", 4_500_000, "2024-03-01", True),
    ("Carlos Mendoza",     "Consultor Senior",        3_200_000, "2024-06-15", True),
    ("Valentina Ríos",     "Analista Financiera",     2_800_000, "2025-01-10", True),
    ("Jorge Cardona",      "Auxiliar Contable",       SMMLV,     "2025-08-01", True),
]
for nombre, cargo, salario, fecha, aux in empleados:
    db.empleado_crear(NIT, nombre, cargo, salario, fecha, aux)
print(f"Empleados creados: {len(empleados)}")

# ─────────────────────────────────────────────
# MOVIMIENTOS — 6 meses (Ene-Jun 2026)
# ─────────────────────────────────────────────

def mov(fecha, tipo, categoria, descripcion, valor, iva=0):
    valor_iva = round(valor * iva / 100)
    db.movimiento_crear(NIT, fecha, tipo, categoria, descripcion,
                        valor, iva, valor_iva, valor + valor_iva)

# ══ ENERO 2026 — Mes de arranque ══
# Ingresos
mov("2026-01-08", "Ingreso", "Honorarios",               "Honorarios diagnóstico financiero - Ferretería Los Andes",    3_500_000, 19)
mov("2026-01-15", "Ingreso", "Prestación de servicios",  "Consultoría estratégica mensual - Panadería Santa Elena",     2_800_000, 19)
mov("2026-01-22", "Ingreso", "Honorarios",               "Asesoría tributaria cierre 2025 - Droguería Central",         4_200_000, 19)
mov("2026-01-28", "Ingreso", "Prestación de servicios",  "Capacitación gestión financiera - Cámara de Comercio",        1_500_000,  0)
# Gastos
mov("2026-01-05", "Gasto",   "Arriendo",                 "Arriendo oficina enero - Centro Empresarial Pereira",         1_800_000,  0)
mov("2026-01-05", "Gasto",   "Nómina y salarios",        "Nómina enero - 4 empleados",                                 12_250_905,  0)
mov("2026-01-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas enero",                                     185_000,  0)
mov("2026-01-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía enero",                                 95_000, 19)
mov("2026-01-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro enero",                                 149_000, 19)
mov("2026-01-15", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo enero",                             450_000, 19)
mov("2026-01-20", "Gasto",   "Publicidad y marketing",   "Pauta redes sociales enero",                                    300_000, 19)
mov("2026-01-25", "Gasto",   "Transporte y logística",   "Viáticos visitas a clientes enero",                            220_000,  0)
mov("2026-01-31", "Gasto",   "Gastos bancarios",         "Comisiones bancarias enero",                                     38_500,  0)

# ══ FEBRERO 2026 — Mes tranquilo ══
mov("2026-02-05", "Ingreso", "Prestación de servicios",  "Consultoría mensual - Panadería Santa Elena",                 2_800_000, 19)
mov("2026-02-12", "Ingreso", "Honorarios",               "Asesoría restructuración deudas - Muebles y Maderas JK",      2_100_000, 19)
mov("2026-02-20", "Ingreso", "Prestación de servicios",  "Elaboración estados financieros - Supermercado El Progreso",  1_800_000, 19)
mov("2026-02-25", "Ingreso", "Arrendamientos",           "Subarriendo sala de juntas - varias empresas",                  600_000,  0)
mov("2026-02-05", "Gasto",   "Arriendo",                 "Arriendo oficina febrero",                                    1_800_000,  0)
mov("2026-02-05", "Gasto",   "Nómina y salarios",        "Nómina febrero - 4 empleados",                               12_250_905,  0)
mov("2026-02-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas febrero",                                   172_000,  0)
mov("2026-02-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía febrero",                               95_000, 19)
mov("2026-02-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro febrero",                               149_000, 19)
mov("2026-02-14", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo febrero",                           450_000, 19)
mov("2026-02-20", "Gasto",   "Capacitación",             "Curso actualización tributaria DIAN 2026",                      380_000,  0)
mov("2026-02-28", "Gasto",   "Gastos bancarios",         "Comisiones bancarias febrero",                                   41_200,  0)

# ══ MARZO 2026 — Mejor mes del trimestre ══
mov("2026-03-03", "Ingreso", "Honorarios",               "Auditoría financiera Q1 - Constructora Andina",               6_800_000, 19)
mov("2026-03-10", "Ingreso", "Prestación de servicios",  "Consultoría mensual - Panadería Santa Elena",                 2_800_000, 19)
mov("2026-03-15", "Ingreso", "Honorarios",               "Asesoría nómina y prestaciones - Restaurante La Fogata",      1_900_000, 19)
mov("2026-03-18", "Ingreso", "Prestación de servicios",  "Diseño sistema de costos - Taller Metalmecánico Pereira",     3_200_000, 19)
mov("2026-03-25", "Ingreso", "Honorarios",               "Declaración renta 2025 persona natural - 5 clientes",         2_500_000,  0)
mov("2026-03-28", "Ingreso", "Prestación de servicios",  "Capacitación Excel financiero - Grupo empresarial",           1_200_000,  0)
mov("2026-03-05", "Gasto",   "Arriendo",                 "Arriendo oficina marzo",                                      1_800_000,  0)
mov("2026-03-05", "Gasto",   "Nómina y salarios",        "Nómina marzo + prima semestral proporcional",                14_850_905,  0)
mov("2026-03-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas marzo",                                    198_000,  0)
mov("2026-03-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía marzo",                                95_000, 19)
mov("2026-03-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro marzo",                                149_000, 19)
mov("2026-03-14", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo marzo",                            450_000, 19)
mov("2026-03-20", "Gasto",   "Publicidad y marketing",   "Campaña digital Google Ads marzo",                             550_000, 19)
mov("2026-03-22", "Gasto",   "Equipos y herramientas",   "Licencia Office 365 anual",                                    890_000, 19)
mov("2026-03-31", "Gasto",   "Impuestos y tasas",        "ICA bimestre 1 (Ene-Feb) Alcaldía Pereira",                    180_000,  0)
mov("2026-03-31", "Gasto",   "Gastos bancarios",         "Comisiones bancarias marzo",                                    52_000,  0)

# ══ ABRIL 2026 ══
mov("2026-04-07", "Ingreso", "Prestación de servicios",  "Consultoría mensual - Panadería Santa Elena",                 2_800_000, 19)
mov("2026-04-10", "Ingreso", "Honorarios",               "Asesoría tributaria - Clínica Veterinaria Animales & Co",     2_400_000, 19)
mov("2026-04-15", "Ingreso", "Honorarios",               "Declaraciones renta 2025 empresas - 3 clientes",              3_600_000,  0)
mov("2026-04-22", "Ingreso", "Prestación de servicios",  "Outsourcing contable mensual - Distribuidora El Eje",         1_800_000, 19)
mov("2026-04-28", "Ingreso", "Otros ingresos",           "Recuperación cartera morosa - Muebles y Maderas JK",          1_050_000,  0)
mov("2026-04-05", "Gasto",   "Arriendo",                 "Arriendo oficina abril",                                      1_800_000,  0)
mov("2026-04-05", "Gasto",   "Nómina y salarios",        "Nómina abril - 4 empleados",                                 12_250_905,  0)
mov("2026-04-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas abril",                                    165_000,  0)
mov("2026-04-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía abril",                                95_000, 19)
mov("2026-04-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro abril",                                149_000, 19)
mov("2026-04-14", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo abril",                            450_000, 19)
mov("2026-04-18", "Gasto",   "Publicidad y marketing",   "Pauta LinkedIn y Meta abril",                                  420_000, 19)
mov("2026-04-25", "Gasto",   "Transporte y logística",   "Viáticos visitas clientes Manizales",                         310_000,  0)
mov("2026-04-30", "Gasto",   "Gastos bancarios",         "Comisiones bancarias abril",                                    44_800,  0)

# ══ MAYO 2026 — Mes fuerte ══
mov("2026-05-05", "Ingreso", "Honorarios",               "Consultoría restructuración financiera - Hotel Movich",        8_500_000, 19)
mov("2026-05-08", "Ingreso", "Prestación de servicios",  "Consultoría mensual - Panadería Santa Elena",                 2_800_000, 19)
mov("2026-05-12", "Ingreso", "Prestación de servicios",  "Outsourcing contable mensual - Distribuidora El Eje",         1_800_000, 19)
mov("2026-05-15", "Ingreso", "Honorarios",               "Asesoría SIMPLE tributario - 4 nuevos clientes",              3_200_000,  0)
mov("2026-05-20", "Ingreso", "Prestación de servicios",  "Implementación software contable - Papelería El Lápiz",       2_100_000, 19)
mov("2026-05-05", "Gasto",   "Arriendo",                 "Arriendo oficina mayo",                                       1_800_000,  0)
mov("2026-05-05", "Gasto",   "Nómina y salarios",        "Nómina mayo - 4 empleados",                                  12_250_905,  0)
mov("2026-05-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas mayo",                                     178_000,  0)
mov("2026-05-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía mayo",                                 95_000, 19)
mov("2026-05-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro mayo",                                 149_000, 19)
mov("2026-05-13", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo mayo",                             450_000, 19)
mov("2026-05-15", "Gasto",   "Impuestos y tasas",        "ICA bimestre 2 (Mar-Abr) Alcaldía Pereira",                   285_000,  0)
mov("2026-05-18", "Gasto",   "Publicidad y marketing",   "Campaña digital + diseño piezas mayo",                        680_000, 19)
mov("2026-05-22", "Gasto",   "Capacitación",             "Seminario NIIF Pymes - Cámara de Comercio Pereira",           420_000,  0)
mov("2026-05-31", "Gasto",   "Gastos bancarios",         "Comisiones bancarias mayo",                                     61_300,  0)

# ══ JUNIO 2026 — Parcial (hasta hoy) ══
mov("2026-06-03", "Ingreso", "Prestación de servicios",  "Consultoría mensual - Panadería Santa Elena",                 2_800_000, 19)
mov("2026-06-05", "Ingreso", "Honorarios",               "Revisión estados financieros semestral - Constructora Andina",4_500_000, 19)
mov("2026-06-10", "Ingreso", "Prestación de servicios",  "Outsourcing contable mensual - Distribuidora El Eje",         1_800_000, 19)
mov("2026-06-05", "Gasto",   "Arriendo",                 "Arriendo oficina junio",                                      1_800_000,  0)
mov("2026-06-05", "Gasto",   "Nómina y salarios",        "Nómina junio + prima semestral",                             18_250_905,  0)
mov("2026-06-10", "Gasto",   "Servicios públicos",       "Energía, agua y gas junio",                                    182_000,  0)
mov("2026-06-10", "Gasto",   "Internet y telecomunicaciones", "Internet + telefonía junio",                                95_000, 19)
mov("2026-06-12", "Gasto",   "Software y suscripciones", "SalazAnalytics Plan Pro junio",                                149_000, 19)
mov("2026-06-12", "Gasto",   "Contabilidad y revisoría", "Honorarios contador externo junio",                            450_000, 19)

# ─────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────
stats = db.stats_empresa(NIT, 2026)
print("\n" + "="*50)
print("DATOS DEMO CARGADOS EXITOSAMENTE")
print("="*50)
print(f"  Empresa : Consultoría Empresarial del Eje S.A.S.")
print(f"  NIT     : {NIT}")
print(f"  Login   : {EMAIL}")
print(f"  Password: {PASS}")
print("="*50)
print(f"  Movimientos : {stats['total_movimientos']}")
print(f"  Ingresos    : ${stats['total_ingresos']:>15,.0f}")
print(f"  Gastos      : ${stats['total_gastos']:>15,.0f}")
print(f"  Utilidad    : ${stats['utilidad']:>15,.0f}")
print(f"  IVA cobrado : ${stats['iva_cobrado']:>15,.0f}")
print(f"  IVA pagado  : ${stats['iva_pagado']:>15,.0f}")
print(f"  IVA neto    : ${stats['iva_neto']:>15,.0f}")
print("="*50)
print("\nListo para presentar a clientes.")
