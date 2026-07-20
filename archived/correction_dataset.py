import geopandas as gpd
from shapely.validation import make_valid

print("1. Cargando base de datos...")
gdf = gpd.read_file("buenos_aires_3d_base.geojson")

# Imprimimos las columnas para que verifiques el nombre exacto de la altura
print("Columnas disponibles en tu archivo:", list(gdf.columns))

print("2. Filtrando solo RECOLETA para que pese poco y cargue al instante...")
# Usamos un filtro directo para probar de forma ligera
gdf_test = gdf[gdf['barrio'] == 'RECOLETA'].copy()

print("3. Reparando geometrías...")
gdf_test['geometry'] = gdf_test['geometry'].apply(lambda geom: make_valid(geom) if not geom.is_valid else geom)
gdf_test = gdf_test.explode(index_parts=False)

print("4. Forzando Sistema de Coordenadas Geográficas (Lat/Lon)...")
# Esto asegura que los edificios caigan en Argentina y no en el medio del mar
gdf_test = gdf_test.to_crs(epsg=4326)

print("5. Exportando subset de prueba...")
gdf_test.to_file("buenos_aires_3d_test.geojson", driver="GeoJSON")
print("¡Listo! Archivo 'buenos_aires_3d_test.geojson' generado.")