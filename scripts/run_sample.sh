#!/usr/bin/env bash
# run_sample.sh — Ejecuta el pipeline completo con el dataset de muestra
set -euo pipefail
cd "$(dirname "$0")/.."

# Activar virtualenv si existe
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "=== Pipeline Mapa 3D (modo sample) ==="

# Copiar sample como datos fuente
echo "1. Preparando datos de muestra..."
mkdir -p data/raw

if [ -f "data/raw/buenos_aires_3d_base.geojson" ] && [ -t 0 ]; then
    echo "   ⚠  ADVERTENCIA: data/raw/buenos_aires_3d_base.geojson ya existe."
    echo "   Si contiene datos reales de CABA, seran sobrescritos por el sample."
    echo "   Para cancelar: Ctrl+C. Para continuar: Enter."
    read -r _
elif [ -f "data/raw/buenos_aires_3d_base.geojson" ]; then
    echo "   ⚠  ADVERTENCIA: data/raw/buenos_aires_3d_base.geojson ya existe."
    echo "   Sobrescribiendo automaticamente (modo no interactivo)."
    echo "   Para evitar esto, ejecuta en terminal interactiva."
fi

cp data/samples/buenos_aires_3d_sample.geojson data/raw/buenos_aires_3d_base.geojson

# Limpieza
echo "2. Ejecutando limpieza geoespacial..."
python3 scripts/limpieza.py

# Calculo solar
echo "3. Ejecutando calculo solar..."
python3 scripts/calculo_solar.py

# Servir
echo ""
echo "=== Pipeline completado ==="
echo ""
echo "Para compilar PMTiles (requiere tippecanoe):"
echo "  tippecanoe -z 16 -Z 13 -pd -o data/tiles/buenos_aires_completo.pmtiles data/processed/buenos_aires_3d_completo_limpio.geojson --force"
echo ""
echo "Para servir el visor:"
echo "  python3 web/server.py"
echo "  open http://localhost:8000/web/index.html"
