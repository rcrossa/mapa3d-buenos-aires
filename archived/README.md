# Archived — Archivos Legacy del Mapa 3D

> **Directorio de archivo histórico.** Estos archivos fueron parte del desarrollo 
> del Mapa 3D + Calculadora Solar de Buenos Aires y se preservan como referencia.
> El producto activo ahora vive en `robertorossa/mapa3d-buenos-aires`.

---

## Inventario

### `visor_automatico.html` (~54 MB)
- **Qué es:** Versión legacy funcional del visor 3D con datos embebidos.
- **Por qué se archivó:** Reemplazado por `web/index.html` + PMTiles en el nuevo repo.
- **⚠️ ADVERTENCIA:** Contiene datos embebidos y lógica que puede **no estar replicada** 
  en `web/index.html` del nuevo repo. **Preservado como referencia funcional — NO borrar.**
- **Reemplazo en nuevo repo:** `web/index.html`

### `nuevo/` (directorio completo)
- **Qué es:** Última versión estructurada del producto antes de la migración. Contenía:
  - `limpieza_completa.py`, `calculo_solar.py` — pipeline de procesamiento
  - `index.html` — visor MapLibre GL JS
  - `server.py` — servidor HTTP con Range Requests
  - `buenos_aires_3d_base.geojson`, `buenos_aires_3d_completo_limpio.geojson` — datasets
  - `buenos_aires_completo.pmtiles` — vector tiles compilados
- **Por qué se archivó:** Migrado y reorganizado al nuevo repo `mapa3d-buenos-aires`.
- **Reemplazo en nuevo repo:** `scripts/`, `web/`, `data/`, `docs/`

### `buenos_aires_3d_base.geojson`
- **Qué es:** Dataset base de edificios de CABA (versión legacy).
- **Por qué se archivó:** Copia antigua. La versión actual se descarga del link privado.
- **Reemplazo en nuevo repo:** `data/raw/buenos_aires_3d_base.geojson` (descargado vía `download_data.sh`)

### `buenos_aires_3d_sample.geojson`
- **Qué es:** Subset de ~50 edificios para desarrollo y tests (versión legacy).
- **Por qué se archivó:** Reemplazado por la versión en el nuevo repo.
- **Reemplazo en nuevo repo:** `data/samples/buenos_aires_3d_sample.geojson`

### `parcelas_catastrales.geojson`
- **Qué es:** Dataset de parcelas catastrales (datos exploratorios).
- **Por qué se archivó:** No forma parte del pipeline principal actual.
- **Reemplazo en nuevo repo:** No tiene reemplazo directo.

### `tejido.dbf`, `tejido.prj`, `tejido.shp`, `tejido.shx`
- **Qué es:** Shapefile del tejido urbano (datos exploratorios).
- **Por qué se archivó:** No forma parte del pipeline principal actual.
- **Reemplazo en nuevo repo:** No tiene reemplazo directo.

### `unificacion_mapa.py`
- **Qué es:** Script exploratorio que sampleaba 50 registros del base.
- **Por qué se archivó:** Reemplazado por `scripts/limpieza.py` (pipeline completo).
- **Reemplazo en nuevo repo:** `scripts/limpieza.py`

### `correction_dataset.py`
- **Qué es:** Script exploratorio que filtraba solo Recoleta para pruebas.
- **Por qué se archivó:** Reemplazado por el pipeline completo con dataset sample.
- **Reemplazo en nuevo repo:** `scripts/limpieza.py` + `data/samples/`

---

## Notas

- **No borrar** archivos de este directorio sin revisar si hay lógica/datos no migrados.
- `visor_automatico.html` es el archivo más crítico — revisar antes de cualquier clean-up futuro.
- Fecha de archivo: 2026-07-20
- Feature: `reorganizacion-mapa3d`
