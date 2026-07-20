# Mapa 3D de Buenos Aires + Calculadora Solar

> Visualizacion 3D de edificios de CABA con analisis de potencial solar.
> Pipeline geoespacial Python → Vector Tiles → Visor MapLibre GL JS.

---

## Quick Start

```bash
git clone git@github.com:rcrossa/mapa3d-buenos-aires.git
cd mapa3d-buenos-aires

# Configurar entorno (crea .venv + instala dependencias)
./scripts/setup.sh

# Ejecutar pipeline con dataset de muestra
./scripts/run_sample.sh

# Servir el visor
source .venv/bin/activate
python3 web/server.py
open http://localhost:8000/web/index.html
```

> Para usar el dataset completo, configurar `.env` con las credenciales
> de descarga y ejecutar `./scripts/download_data.sh`.

---

## Que hace

- Procesa el dataset de edificios de CABA (reparacion geometrica, normalizacion CRS)
- Calcula potencial solar: paneles viables, energia generada, ahorro y payback
- Visualiza en mapa 3D interactivo con mapa de calor por area util

---

## Estructura

```
├── scripts/            # Pipeline Python
│   ├── download_data.sh
│   ├── limpieza.py
│   ├── calculo_solar.py
│   └── requirements.txt
├── web/                # Visor y servidor
│   ├── index.html
│   └── server.py
├── data/
│   ├── raw/            # Datos fuente (gitignored)
│   ├── processed/      # Pipeline output (gitignored)
│   ├── tiles/          # PMTiles (gitignored)
│   └── samples/        # Subset para desarrollo
├── docs/
│   └── pipeline.md     # Documentacion del flujo
├── archived/           # Codigo legacy de referencia
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Requisitos

- Python 3.9+
- [tippecanoe](https://github.com/felt/tippecanoe) (`brew install tippecanoe`)
- curl (preinstalado)
- Credenciales de descarga (solicitar a Roberto Rossa)

---

## Desarrollo rapido con sample

```bash
./scripts/setup.sh       # Solo la primera vez
./scripts/run_sample.sh  # Ejecuta todo el pipeline
```

O paso a paso:

```bash
source .venv/bin/activate
cp data/samples/buenos_aires_3d_sample.geojson data/raw/buenos_aires_3d_base.geojson
python3 scripts/limpieza.py
python3 scripts/calculo_solar.py
python3 web/server.py
```

---

## Licencia

Copyright (c) 2026 Roberto Rossa. Todos los derechos reservados.
Ver [LICENSE](LICENSE).
