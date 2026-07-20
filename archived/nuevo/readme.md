# README — Mapa 3D (Buenos Aires)

Requisitos y flujo de trabajo:

1. Generar el archivo base:

     - Tener `buenos_aires_3d_base.geojson` generado.
     - Ejecutar `limpieza_completa.py` → produce `buenos_aires_3d_completo_limpio.geojson`.
     - Ejecutar `calculo_solar.py` sobre el archivo limpio para enriquecerlo con cálculos solares y financieros (sobrescribe/actualiza `buenos_aires_3d_completo_limpio.geojson`).

2. Compilar a PMTiles (tippecanoe):

     Ejecutar:

     ```bash
     tippecanoe -z 16 -Z 13 -pd -o buenos_aires_completo.pmtiles buenos_aires_3d_completo_limpio.geojson --force
     ```

     Luego colocar `buenos_aires_completo.pmtiles` en el mismo directorio que `index.html` para que el visor cargue el archivo.

Librerías y herramientas instaladas:

- geopandas
- numpy
- pandas
- rasterio
- pyproj
- shapely
- tippecanoe (Homebrew, macOS)
- rangehttpserver (pip)

Detalles:

1) Herramientas del sistema (macOS / Homebrew)

     - Tippecanoe
         - Comando: `brew install tippecanoe`
         - Uso: Compilar GeoJSON masivos a Vector Tiles (.pmtiles). Opciones como `-pd` permiten descartar polígonos irrelevantes en zooms lejanos.

2) Entorno virtual de Python (back-end)

     - Pyogrio
         - Comando: `pip install pyogrio`
         - Uso: I/O rápido para GeoPandas (basado en GDAL/OGR).

     - RangeHTTPServer
         - Comando: `pip install RangeHTTPServer`
         - Uso: Servir archivos con soporte de HTTP Range Requests (requerido por PMTiles).

     - GeoPandas y Shapely
         - Comando: `pip install geopandas shapely`
         - Uso: Limpieza topológica (make_valid), explode, reproyección (EPSG:4326) y modelado de cálculos a inyectar en el GeoJSON.

3) Front-end / Visor (CDN)

     - MapLibre GL JS (v3.6.2)
         - Uso: Renderizado WebGL y estilado 3D de edificios.

     - PMTiles (pmtiles@2.11.0)
         - Uso: Cliente para leer archivos .pmtiles mediante peticiones de rango HTTP.

Fin.