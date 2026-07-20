import geopandas as gpd

print("1. Cargando edificios de prueba...")
gdf = gpd.read_file("buenos_aires_3d_completo_limpio.geojson")

print("2. Aplicando modelo físico y financiero...")
# Constantes físicas
RADIACION_ANUAL_CABA = 1600  # kWh/m2 al año
EFICIENCIA_PANEL = 0.20      # 20%
PR = 0.80                    # Performance Ratio
AREA_POR_PANEL = 2.0         # m2 por panel estándar

# Constantes financieras (Valores de referencia)
TARIFA_KWH_ARS = 85.00       # Precio del kWh
COSTO_INSTALACION_POR_PANEL = 450000  # Costo del panel + inversor + mano de obra (ARS)

# Cálculos
gdf['paneles_viables'] = (gdf['area_util'] / AREA_POR_PANEL).fillna(0).astype(int)
gdf['energia_anual_kwh'] = gdf['area_util'] * RADIACION_ANUAL_CABA * EFICIENCIA_PANEL * PR
gdf['ahorro_anual_ars'] = gdf['energia_anual_kwh'] * TARIFA_KWH_ARS
gdf['costo_instalacion_ars'] = gdf['paneles_viables'] * COSTO_INSTALACION_POR_PANEL

# Payback (Años en recuperar la inversión). Evitamos división por cero.
import numpy as np
gdf['payback_anios'] = np.where(gdf['ahorro_anual_ars'] > 0, 
                                gdf['costo_instalacion_ars'] / gdf['ahorro_anual_ars'], 
                                0)

print("3. Redondeando valores para la UI web...")
gdf['energia_anual_kwh'] = gdf['energia_anual_kwh'].fillna(0).round(0).astype(int)
gdf['ahorro_anual_ars'] = gdf['ahorro_anual_ars'].fillna(0).round(0).astype(int)
gdf['payback_anios'] = gdf['payback_anios'].round(1) # Dejamos 1 decimal (ej: 4.5 años)

print("4. Guardando base de datos enriquecida...")
gdf.to_file("buenos_aires_3d_completo_limpio.geojson", driver="GeoJSON")
print("¡Cálculo finalizado con éxito!")