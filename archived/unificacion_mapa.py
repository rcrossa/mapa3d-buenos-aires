import geopandas as gpd

# Cargamos el consolidado
gdf = gpd.read_file("buenos_aires_3d_base.geojson")

# Forzamos coordenadas correctas y tomamos solo 50 registros para testear
gdf = gdf.to_crs(epsg=4326)
gdf_sample = gdf.head(50)
gdf_sample.to_file("buenos_aires_3d_sample.geojson", driver="GeoJSON")
# Imprimimos el GeoJSON como string de texto limpio
print("\n--- COPIÁ TODO LO DE ABAJO ---\n")
print(gdf_sample.to_json())
print("\n------------------------------\n")