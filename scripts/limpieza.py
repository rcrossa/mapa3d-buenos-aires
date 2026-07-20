import geopandas as gpd
from shapely.validation import make_valid
import os
import sys

# Rutas relativas a la raiz del repo
INPUT_PATH = os.path.join("data", "raw", "buenos_aires_3d_base.geojson")
OUTPUT_PATH = os.path.join("data", "processed", "buenos_aires_3d_completo_limpio.geojson")

print("1. Cargando la base de datos maestra completa...")
if not os.path.exists(INPUT_PATH):
    print(f"ERROR: No se encuentra {INPUT_PATH}")
    print("Ejecuta primero: ./scripts/download_data.sh")
    sys.exit(1)

gdf = gpd.read_file(INPUT_PATH, engine="pyogrio")
print(f"-> Edificios cargados: {len(gdf)}")

if len(gdf) == 0:
    print("ERROR CRITICO: El archivo base esta vacio.")
    sys.exit(1)

print("2. Reparando geometrias invalidas en toda la base...")
gdf['geometry'] = gdf['geometry'].apply(
    lambda geom: make_valid(geom) if not geom.is_valid else geom
)

print("3. Explotando MultiPoligonos a Poligonos simples...")
gdf = gdf.explode(index_parts=False)

print("4. Forzando Sistema de Coordenadas Geograficas WGS84 (EPSG:4326)...")
if gdf.crs is None or gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

print(f"-> Geometrias finales listas para exportar: {len(gdf)}")

print(f"5. Exportando '{OUTPUT_PATH}'...")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
gdf.to_file(OUTPUT_PATH, driver="GeoJSON", engine="pyogrio")

print("Proceso de limpieza terminado con exito!")
