#!/usr/bin/env bash
# download_data.sh — Obtiene los datasets grandes
#   1. Si existe archived/ local: copia directa (maquina original)
#   2. Si no: descarga desde link privado configurado en .env
set -euo pipefail

mkdir -p data/raw

echo "Obteniendo datos fuente..."

# Opcion 1: Copiar desde archived/ local
if [ -f "archived/nuevo/buenos_aires_3d_base.geojson" ]; then
    echo "-> Encontrado en archived/ (local), copiando..."
    cp archived/nuevo/buenos_aires_3d_base.geojson data/raw/
    echo "   $(ls -lh data/raw/buenos_aires_3d_base.geojson | awk '{print $5}')"

    # Copiar tambien PMTiles pre-compilados si existen
    if [ -f "archived/nuevo/buenos_aires_completo.pmtiles" ]; then
        mkdir -p data/tiles
        cp archived/nuevo/buenos_aires_completo.pmtiles data/tiles/
        echo "-> PMTiles tambien copiados a data/tiles/"
    fi
    echo "Datos listos en data/"
    exit 0
fi

# Opcion 2: Descargar desde link privado
if [ ! -f .env ]; then
    echo "ERROR: No se encuentra .env ni los datos en archived/"
    echo ""
    echo "Si estas en la maquina original, los datos estan en:"
    echo "  archived/nuevo/buenos_aires_3d_base.geojson"
    echo ""
    echo "Si es un clone fresco:"
    echo "  cp .env.example .env"
    echo "  # Editar .env con DOWNLOAD_URL y DOWNLOAD_TOKEN"
    echo "  ./scripts/download_data.sh"
    exit 1
fi

# Safe .env parsing: only reads KEY=VALUE lines, ignores comments and blanks
while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    case "$key" in
        ''|\#*) continue ;;
        DOWNLOAD_URL)     DOWNLOAD_URL="$value" ;;
        DOWNLOAD_TOKEN)   DOWNLOAD_TOKEN="$value" ;;
    esac
done < .env

if [ -z "${DOWNLOAD_URL:-}" ] || [ "$DOWNLOAD_URL" = "https://example.com/datasets" ]; then
    echo "ERROR: DOWNLOAD_URL no configurado en .env"
    echo "Edita .env con la URL real de descarga."
    exit 1
fi

echo "-> Descargando desde $DOWNLOAD_URL ..."
curl -H "Authorization: Bearer ${DOWNLOAD_TOKEN:-}" \
     -o data/raw/buenos_aires_3d_base.geojson \
     "$DOWNLOAD_URL/buenos_aires_3d_base.geojson"

echo "Datos descargados a data/raw/"
