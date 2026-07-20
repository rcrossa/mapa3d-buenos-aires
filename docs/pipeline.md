# Pipeline de Datos — Mapa 3D Buenos Aires

> Documentacion del flujo completo de procesamiento de datos geoespaciales
> para el Mapa 3D + Calculadora Solar de CABA.

---

## Requisitos del Sistema

| Herramienta | Version | Instalacion |
|-------------|---------|-------------|
| Python | 3.9+ | [python.org](https://python.org) |
| tippecanoe | latest | `brew install tippecanoe` (macOS) |
| curl | preinstalado | Sistema |

### Dependencias Python

```bash
# Automatico (recomendado)
./scripts/setup.sh

# Manual
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

Incluye: geopandas, pyogrio, numpy, pandas, shapely, pyproj, RangeHTTPServer.

---

## Flujo de Trabajo

### Paso 1: Descargar datos fuente

```bash
cp .env.example .env
# Editar .env con DOWNLOAD_URL y DOWNLOAD_TOKEN
./scripts/download_data.sh
```

El dataset base se descarga a `data/raw/`.

### Paso 2: Limpieza y normalizacion

```bash
python3 scripts/limpieza.py
```

- Repara geometrias invalidas (`make_valid`)
- Explota MultiPolygons a Polygons simples
- Fuerza EPSG:4326 (WGS84)

**Entrada:** `data/raw/buenos_aires_3d_base.geojson`
**Salida:** `data/processed/buenos_aires_3d_completo_limpio.geojson`

### Paso 3: Calculo solar y financiero

```bash
python3 scripts/calculo_solar.py
```

Calcula paneles viables, energia anual generada (kWh),
ahorro economico y periodo de recupero (payback).

**Entrada/Salida:** `data/processed/buenos_aires_3d_completo_limpio.geojson` (se enriquece in-place)

### Paso 4: Compilar a Vector Tiles (PMTiles)

```bash
tippecanoe -z 16 -Z 13 -pd \
  -o data/tiles/buenos_aires_completo.pmtiles \
  data/processed/buenos_aires_3d_completo_limpio.geojson \
  --force
```

### Paso 5: Servir el visor

```bash
python3 web/server.py
```

Abrir: http://localhost:8000/web/index.html

---

## Desarrollo con Sample

```bash
# Un solo comando
./scripts/run_sample.sh

# O paso a paso
source .venv/bin/activate
cp data/samples/buenos_aires_3d_sample.geojson data/raw/buenos_aires_3d_base.geojson
python3 scripts/limpieza.py
python3 scripts/calculo_solar.py
```
