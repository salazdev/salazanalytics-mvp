#!/bin/bash
# start.sh — Script de arranque SalazAnalytics
# 1. Espera que /data esté disponible
# 2. Inicializa la BD si está vacía
# 3. Arranca Streamlit

echo "Iniciando SalazAnalytics..."

# Crear /data si no existe (fallback)
mkdir -p /data 2>/dev/null || true

# Verificar si la BD tiene datos
EMPRESAS=$(python3 -c "
import sqlite3, os
db = '/data/salazanalytics.db'
if not os.path.exists(db):
    print('0')
else:
    try:
        conn = sqlite3.connect(db)
        n = conn.execute('SELECT COUNT(*) FROM empresas').fetchone()[0]
        conn.close()
        print(n)
    except:
        print('0')
" 2>/dev/null || echo "0")

echo "Empresas en BD: $EMPRESAS"

if [ "$EMPRESAS" = "0" ]; then
    echo "BD vacía — corriendo seed demo..."
    python3 /app/seed_demo.py
    echo "Seed completado."
else
    echo "BD con datos — saltando seed."
fi

echo "Arrancando Streamlit..."
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
