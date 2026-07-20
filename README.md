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

# Obtener datos y ejecutar pipeline:
#   Opcion A: datos de muestra (50 edificios, no requiere descarga)
./scripts/run_sample.sh

#   Opcion B: datos completos (~1.2 GB, requiere link de descarga)
./scripts/download_data.sh   # copia de archived/ local o descarga web
./scripts/run_full.sh        # pipeline completo + PMTiles

# Servir el visor
source .venv/bin/activate
python3 web/server.py
open http://localhost:8000/web/index.html
```

> **Nota:** Los datasets completos (~6 GB) no estan en git. Deben solicitarse a Roberto Rossa.

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
- [tippecanoe](https://github.com/felt/tippecanoe)
  - macOS: `brew install tippecanoe`
  - Windows: `scoop install tippecanoe` o [descargar binario](https://github.com/felt/tippecanoe/releases)
  - Linux/WSL: `sudo apt install tippecanoe`
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
