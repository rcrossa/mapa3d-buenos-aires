#!/usr/bin/env bash
# run_full.sh — Pipeline completo con datos reales de CABA
#   Si estas en la maquina original: copia desde archived/ (~6 GB locales)
#   Si es un clone fresco: requiere ./scripts/download_data.sh primero
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "=== Pipeline Mapa 3D (datos reales CABA) ==="

# Paso 1: Obtener datos fuente
echo "1. Preparando datos fuente..."

source scripts/source_env.sh

FOUND=false
if [ -f "archived/nuevo/buenos_aires_3d_base.geojson" ]; then
    echo "   Encontrado en archived/ (local), copiando..."
    if [ -f "data/raw/buenos_aires_3d_base.geojson" ] \
       && cmp -s "archived/nuevo/buenos_aires_3d_base.geojson" \
                 "data/raw/buenos_aires_3d_base.geojson"; then
        echo "   (identico a archived/, skip copy)"
    else
        cp archived/nuevo/buenos_aires_3d_base.geojson data/raw/
    fi
    FOUND=true
elif [ -f "data/raw/buenos_aires_3d_base.geojson" ]; then
    echo "   Ya existe en data/raw/"
    FOUND=true
else
    echo "   No encontrado. Intentando descargar..."
    if [ -f ".env" ] && [ -n "${DOWNLOAD_URL:-}" ] && [ "$DOWNLOAD_URL" != "https://example.com/datasets" ]; then
        ./scripts/download_data.sh
        FOUND=true
    else
        echo ""
        echo "   ERROR: No se encontraron los datos fuente."
        echo ""
        echo "   Opcion 1 (maquina original):"
        echo "     cp archived/nuevo/buenos_aires_3d_base.geojson data/raw/"
        echo ""
        echo "   Opcion 2 (clone fresco):"
        echo "     cp .env.example .env"
        echo "     # Editar .env con DOWNLOAD_URL y DOWNLOAD_TOKEN"
        echo "     ./scripts/download_data.sh"
        exit 1
    fi
fi

# Limpieza
echo "2. Ejecutando limpieza geoespacial..."
python3 scripts/limpieza.py

# Calculo solar
echo "3. Ejecutando calculo solar..."
python3 scripts/calculo_solar.py

# Compilar PMTiles (si tippecanoe esta instalado)
if command -v tippecanoe &>/dev/null; then
    echo "4. Compilando PMTiles..."
    if tippecanoe -z 16 -Z 13 -pd \
        -o data/tiles/buenos_aires_completo.pmtiles \
        data/processed/buenos_aires_3d_completo_limpio.geojson \
        --force; then
        echo "   PMTiles: $(ls -lh data/tiles/buenos_aires_completo.pmtiles | awk '{print $5}')"
    elif [ -f "archived/nuevo/buenos_aires_completo.pmtiles" ]; then
        echo "   tippecanoe fallo. Usando PMTiles pre-compilados..."
        cp archived/nuevo/buenos_aires_completo.pmtiles data/tiles/
        echo "   PMTiles: $(ls -lh data/tiles/buenos_aires_completo.pmtiles | awk '{print $5}')"
    else
        echo "   ERROR: tippecanoe fallo y no hay PMTiles pre-compilados."
        exit 1
    fi
elif [ -f "archived/nuevo/buenos_aires_completo.pmtiles" ]; then
    echo "4. tippecanoe no instalado. Copiando PMTiles pre-compilados..."
    cp archived/nuevo/buenos_aires_completo.pmtiles data/tiles/
    echo "   PMTiles: $(ls -lh data/tiles/buenos_aires_completo.pmtiles | awk '{print $5}')"
else
    echo "4. tippecanoe no instalado y no hay PMTiles pre-compilados."
    echo "   Instala tippecanoe: brew install tippecanoe"
    echo "   O copia los PMTiles manualmente a data/tiles/"
    exit 1
fi

echo ""
echo "=== Pipeline completado ==="
echo ""
echo "Para servir el visor:"
echo "  source .venv/bin/activate"
echo "  python3 web/server.py"
echo "  open http://localhost:8000/web/index.html"
