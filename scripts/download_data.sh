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

source scripts/source_env.sh

if [ -z "${DOWNLOAD_URL:-}" ] || [ "$DOWNLOAD_URL" = "https://example.com/datasets" ]; then
    echo "ERROR: DOWNLOAD_URL no configurado en .env"
    echo "Edita .env con la URL real de descarga."
    exit 1
fi

echo "-> Descargando desde $DOWNLOAD_URL ..."

# Use --fail so HTTP errors (403/404/500) are treated as failures.
# --fail-with-body preserves the error response for debugging.
# Token is passed via a temporary header file to avoid process-list exposure.
AUTH_FILE=$(mktemp)
# Sanitize token: strip newlines/carriage returns to prevent header injection
# (curl -H @file reads lines verbatim; newlines would inject arbitrary headers)
DOWNLOAD_TOKEN="${DOWNLOAD_TOKEN//$'\n'/}"
DOWNLOAD_TOKEN="${DOWNLOAD_TOKEN//$'\r'/}"
printf "Authorization: Bearer %s" "${DOWNLOAD_TOKEN:-}" > "$AUTH_FILE"
HTTP_CODE=$(curl --fail --fail-with-body -s -w '%{http_code}' \
    -H @"$AUTH_FILE" \
    -o data/raw/buenos_aires_3d_base.geojson \
    "$DOWNLOAD_URL/buenos_aires_3d_base.geojson") || {
    rm -f "$AUTH_FILE"
    echo "ERROR: Download failed (HTTP $HTTP_CODE)."
    echo "Check DOWNLOAD_URL and DOWNLOAD_TOKEN in .env"
    rm -f data/raw/buenos_aires_3d_base.geojson
    exit 1
}
rm -f "$AUTH_FILE"

echo "Datos descargados a data/raw/ (HTTP $HTTP_CODE)"

# Validate the downloaded file is valid JSON
if python3 -c "import json; json.load(open('data/raw/buenos_aires_3d_base.geojson'))" 2>/dev/null; then
    echo "   Validacion: archivo JSON valido."
else
    echo "   ADVERTENCIA: El archivo descargado no es JSON valido."
fi
