import geopandas as gpd
from shapely.validation import make_valid
import logging
import os
import sys

logger = logging.getLogger(__name__)

# Default paths relative to repo root
INPUT_PATH = os.path.join("data", "raw", "buenos_aires_3d_base.geojson")
OUTPUT_PATH = os.path.join("data", "processed", "buenos_aires_3d_completo_limpio.geojson")


def run(input_path=None, output_path=None):
    """Run the geo cleaning pipeline.

    Args:
        input_path: Path to raw GeoJSON. Defaults to INPUT_PATH.
        output_path: Path for cleaned output. Defaults to OUTPUT_PATH.
    """
    src = input_path or INPUT_PATH
    dst = output_path or OUTPUT_PATH

    logger.info("1. Loading master database...")
    if not os.path.exists(src):
        logger.error("File not found: %s", src)
        logger.info("Run first: ./scripts/download_data.sh")
        sys.exit(1)

    gdf = gpd.read_file(src, engine="pyogrio")
    logger.info("-> Buildings loaded: %d", len(gdf))

    if len(gdf) == 0:
        logger.critical("Input file is empty.")
        sys.exit(1)

    logger.info("2. Repairing invalid geometries...")
    gdf['geometry'] = gdf['geometry'].apply(
        lambda geom: make_valid(geom) if not geom.is_valid else geom
    )

    logger.info("3. Exploding MultiPolygons to simple Polygons...")
    gdf = gdf.explode(index_parts=False)

    logger.info("4. Forcing CRS to WGS84 (EPSG:4326)...")
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    logger.info("-> Final geometries ready for export: %d", len(gdf))

    logger.info("5. Exporting '%s'...", dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    gdf.to_file(dst, driver="GeoJSON", engine="pyogrio")

    logger.info("Cleaning pipeline completed successfully!")


if __name__ == "__main__":
    from scripts.logging_config import setup
    setup()
    run()
