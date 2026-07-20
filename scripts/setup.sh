#!/usr/bin/env bash
# setup.sh — Configura el entorno de desarrollo del mapa 3D
set -euo pipefail

echo "=== Configurando entorno del Mapa 3D de Buenos Aires ==="

# Crear virtualenv si no existe
if [ ! -d ".venv" ]; then
    echo "1. Creando entorno virtual Python..."
    python3 -m venv .venv
fi

# Activar
source .venv/bin/activate

# Instalar dependencias
echo "2. Instalando dependencias..."
pip install --upgrade pip
pip install -r scripts/requirements.txt

echo ""
echo "=== Setup completo ==="
echo ""
echo "Para usar el entorno:"
echo "  source .venv/bin/activate"
echo ""
echo "Para desarrollo rapido con el dataset sample:"
echo "  ./scripts/run_sample.sh"
