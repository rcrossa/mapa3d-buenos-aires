import geopandas as gpd
from shapely.validation import make_valid
import os

# Asegurar que el entorno virtual tenga pyogrio instalado: pip install pyogrio
print("1. Cargando la base de datos maestra completa con motor optimizado...")
gdf = gpd.read_file("buenos_aires_3d_base.geojson", engine="pyogrio")
print(f"-> Edificios cargados: {len(gdf)}")

if len(gdf) == 0:
    print("ERROR CRÍTICO: El archivo base está vacío.")
    exit()

print("2. Reparando geometrías inválidas en toda la base...")
# Mantenemos la lógica de reparación pero sobre el dataframe completo
gdf['geometry'] = gdf['geometry'].apply(lambda geom: make_valid(geom) if not geom.is_valid else geom)

print("3. Explotando MultiPolígonos a Polígonos simples...")
gdf = gdf.explode(index_parts=False)

print("4. Forzando Sistema de Coordenadas Geográficas WGS84 (EPSG:4326)...")
if gdf.crs is None or gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

print(f"-> Geometrías finales listas para exportar: {len(gdf)}")

print("5. Exportando 'buenos_aires_3d_completo_limpio.geojson'...")
# Usamos pyogrio para escribir a máxima velocidad
gdf.to_file("buenos_aires_3d_completo_limpio.geojson", driver="GeoJSON", engine="pyogrio")

print("¡Proceso de limpieza de back-end terminado con éxito!")