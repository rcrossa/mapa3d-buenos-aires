#!/usr/bin/env bash
# download_data.sh — Descarga datasets grandes desde link privado
set -euo pipefail

if [ -f .env ]; then
    source .env
else
    echo "ERROR: No se encuentra .env"
    echo "Copia .env.example a .env y configura DOWNLOAD_URL y DOWNLOAD_TOKEN"
    exit 1
fi

if [ -z "${DOWNLOAD_URL:-}" ] || [ -z "${DOWNLOAD_TOKEN:-}" ]; then
    echo "ERROR: DOWNLOAD_URL y DOWNLOAD_TOKEN deben estar definidos en .env"
    exit 1
fi

mkdir -p data/raw

echo "Descargando buenos_aires_3d_base.geojson..."
curl -H "Authorization: Bearer $DOWNLOAD_TOKEN" \
     -o data/raw/buenos_aires_3d_base.geojson \
     "$DOWNLOAD_URL/buenos_aires_3d_base.geojson"

echo "Datos descargados a data/raw/"
