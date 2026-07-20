import geopandas as gpd
import json
import logging
import numpy as np
import os
import sys

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join("data", "processed", "buenos_aires_3d_completo_limpio.geojson")
OUTPUT_PATH = INPUT_PATH  # in-place enrichment
CONFIG_PATH = os.path.join("config.json")

# Sensible defaults (used when config.json is missing)
DEFAULT_SOLAR = {
    "radiacion_anual_caba": 1600,
    "eficiencia_panel": 0.20,
    "pr": 0.80,
    "area_por_panel": 2.0,
}
DEFAULT_FINANCIERO = {
    "tarifa_kwh_ars": 85.00,
    "costo_instalacion_por_panel": 450000,
}


def _load_config(config_path=None):
    """Load solar + financial constants from config.json, falling back to defaults."""
    path = config_path or CONFIG_PATH
    solar = dict(DEFAULT_SOLAR)
    financiero = dict(DEFAULT_FINANCIERO)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        solar.update(cfg.get("solar", {}))
        financiero.update(cfg.get("financiero", {}))
        logger.info("Loaded config from %s", path)
    else:
        logger.warning("config.json not found, using defaults")
    return solar, financiero


def run(input_path=None, output_path=None, config_path=None):
    """Run solar calculation pipeline.

    Args:
        input_path: Path to cleaned GeoJSON. Defaults to INPUT_PATH.
        output_path: Path for enriched output. Defaults to OUTPUT_PATH.
        config_path: Path to config.json. Defaults to CONFIG_PATH.
    """
    src = input_path or INPUT_PATH
    dst = output_path or OUTPUT_PATH
    solar_cfg, fin_cfg = _load_config(config_path)

    logger.info("1. Loading processed buildings...")
    if not os.path.exists(src):
        logger.error("File not found: %s", src)
        logger.info("Run first: python3 scripts/limpieza.py")
        sys.exit(1)

    gdf = gpd.read_file(src)

    logger.info("2. Applying physical and financial model...")
    rad = solar_cfg["radiacion_anual_caba"]
    eff = solar_cfg["eficiencia_panel"]
    pr = solar_cfg["pr"]
    area = solar_cfg["area_por_panel"]
    tarifa = fin_cfg["tarifa_kwh_ars"]
    costo = fin_cfg["costo_instalacion_por_panel"]

    gdf["paneles_viables"] = (gdf["area_util"] / area).fillna(0).astype(int)
    gdf["energia_anual_kwh"] = (
        gdf["area_util"] * rad * eff * pr
    )
    gdf["ahorro_anual_ars"] = gdf["energia_anual_kwh"] * tarifa
    gdf["costo_instalacion_ars"] = gdf["paneles_viables"] * costo

    gdf["payback_anios"] = np.where(
        gdf["ahorro_anual_ars"] > 0,
        gdf["costo_instalacion_ars"] / gdf["ahorro_anual_ars"],
        0,
    )

    logger.info("3. Rounding values for web UI...")
    gdf["energia_anual_kwh"] = gdf["energia_anual_kwh"].fillna(0).round(0).astype(int)
    gdf["ahorro_anual_ars"] = gdf["ahorro_anual_ars"].fillna(0).round(0).astype(int)
    gdf["payback_anios"] = gdf["payback_anios"].round(1)

    logger.info("4. Saving enriched database...")
    gdf.to_file(dst, driver="GeoJSON")
    logger.info("Solar calculation completed successfully!")


if __name__ == "__main__":
    from scripts.logging_config import setup
    setup()
    run()
