import geopandas as gpd
import numpy as np
import os
import sys

INPUT_PATH = os.path.join("data", "processed", "buenos_aires_3d_completo_limpio.geojson")
OUTPUT_PATH = INPUT_PATH  # Sobrescribe el mismo archivo

print("1. Cargando edificios procesados...")
if not os.path.exists(INPUT_PATH):
    print(f"ERROR: No se encuentra {INPUT_PATH}")
    print("Ejecuta primero: python3 scripts/limpieza.py")
    sys.exit(1)

gdf = gpd.read_file(INPUT_PATH)

print("2. Aplicando modelo fisico y financiero...")
# Constantes fisicas
RADIACION_ANUAL_CABA = 1600  # kWh/m2 al anio
EFICIENCIA_PANEL = 0.20      # 20%
PR = 0.80                    # Performance Ratio
AREA_POR_PANEL = 2.0         # m2 por panel estandar

# Constantes financieras (Valores de referencia)
TARIFA_KWH_ARS = 85.00       # Precio del kWh
COSTO_INSTALACION_POR_PANEL = 450000  # ARS

# Calculos
gdf['paneles_viables'] = (gdf['area_util'] / AREA_POR_PANEL).fillna(0).astype(int)
gdf['energia_anual_kwh'] = (
    gdf['area_util'] * RADIACION_ANUAL_CABA * EFICIENCIA_PANEL * PR
)
gdf['ahorro_anual_ars'] = gdf['energia_anual_kwh'] * TARIFA_KWH_ARS
gdf['costo_instalacion_ars'] = gdf['paneles_viables'] * COSTO_INSTALACION_POR_PANEL

gdf['payback_anios'] = np.where(
    gdf['ahorro_anual_ars'] > 0,
    gdf['costo_instalacion_ars'] / gdf['ahorro_anual_ars'],
    0
)

print("3. Redondeando valores para la UI web...")
gdf['energia_anual_kwh'] = gdf['energia_anual_kwh'].fillna(0).round(0).astype(int)
gdf['ahorro_anual_ars'] = gdf['ahorro_anual_ars'].fillna(0).round(0).astype(int)
gdf['payback_anios'] = gdf['payback_anios'].round(1)

print("4. Guardando base de datos enriquecida...")
gdf.to_file(OUTPUT_PATH, driver="GeoJSON")
print("Calculo finalizado con exito!")
