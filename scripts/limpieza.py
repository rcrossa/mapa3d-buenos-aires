import geopandas as gpd
from shapely.validation import make_valid
import shapely.errors
import logging
import os
import sys
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default paths relative to repo root
INPUT_PATH = os.path.join("data", "raw", "buenos_aires_3d_base.geojson")
OUTPUT_PATH = os.path.join(
    "data", "processed", "buenos_aires_3d_completo_limpio.geojson"
)


def _safe_make_valid(geom):
    """Wrap make_valid with per-row error handling.

    Returns the repaired geometry, or the original if repair fails.
    """
    try:
        if not geom.is_valid:
            return make_valid(geom)
        return geom
    except (shapely.errors.GEOSException, ValueError):
        logger.warning("Could not repair geometry %s, keeping original.", type(geom).__name__)
        return geom


def run(input_path=None, output_path=None):
    """Run the geo cleaning pipeline.

    Args:
        input_path: Path to raw GeoJSON. Defaults to INPUT_PATH.
        output_path: Path for cleaned output. Defaults to OUTPUT_PATH.

    Raises:
        FileNotFoundError: If input file is missing.
        ValueError: If input file is empty.
    """
    src = input_path or INPUT_PATH
    dst = output_path or OUTPUT_PATH

    logger.info("1. Loading master database...")
    if not os.path.exists(src):
        logger.error("File not found: %s", src)
        raise FileNotFoundError(
            f"Input file not found: {src}. Run download_data.sh first."
        )

    gdf = gpd.read_file(src, engine="pyogrio")
    logger.info("-> Buildings loaded: %d", len(gdf))

    if "geometry" not in gdf.columns:
        raise KeyError("Input GeoJSON has no 'geometry' column.")

    if len(gdf) == 0:
        logger.critical("Input file is empty.")
        raise ValueError(f"Input file is empty: {src}")

    # Idempotency guard: prevent re-processing already-cleaned data.
    # Re-running would re-repair geometries (possibly producing different
    # results across Shapely versions), re-explode MultiPolygons, and
    # overwrite pipeline metadata timestamps.
    if "_pipeline_stage" in gdf.columns:
        logger.error(
            "Input file already processed (has '_pipeline_stage' column). "
            "Re-running would re-repair/re-explode and may cause data drift. "
            "Run on the original raw data if you need a fresh clean."
        )
        raise ValueError(
            "Input already cleaned — re-running may cause data drift."
        )

    logger.info("2. Repairing invalid geometries...")
    # Vectorized: only repair invalid geometries (avoids per-row Python dispatch).
    # On the full 100K+ building dataset this is 10-50\u00d7 faster than .apply().
    invalid_mask = ~gdf.is_valid
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        logger.info("-> Found %d invalid geometries, repairing...", invalid_count)
        try:
            gdf.loc[invalid_mask, "geometry"] = make_valid(
                gdf.loc[invalid_mask, "geometry"]
            )
        except (shapely.errors.GEOSException, ValueError) as exc:
            logger.warning(
                "Vectorized repair failed for some geometries: %s. "
                "Falling back to per-row repair.", exc
            )
            gdf["geometry"] = gdf["geometry"].apply(_safe_make_valid)
    else:
        logger.info("-> All geometries valid, skipping repair.")

    logger.info("3. Exploding MultiPolygons to simple Polygons...")
    gdf = gdf.explode(index_parts=False)

    # Fix area_util double-counting: explode duplicates area_util for each
    # polygon part. Divide proportionally so sums stay correct downstream.
    if "area_util" in gdf.columns:
        multi_mask = gdf.index.duplicated(keep=False)
        if multi_mask.any():
            part_counts = (
                gdf.loc[multi_mask]
                .groupby(level=0)
                .size()
            )
            gdf.loc[multi_mask, 'area_util'] = (
                gdf.loc[multi_mask, 'area_util']
                / part_counts.reindex(gdf.loc[multi_mask].index).values
            )
            logger.info(
                "-> Divided area_util proportionally for %d exploded "
                "MultiPolygon rows.",
                multi_mask.sum(),
            )

    logger.info("4. Forcing CRS to WGS84 (EPSG:4326)...")
    if gdf.crs is None:
        logger.warning("Input has no CRS. Assuming EPSG:4326.")
        gdf = gdf.set_crs(epsg=4326)
    else:
        epsg = gdf.crs.to_epsg()
        if epsg is None:
            # Compound or custom CRS (e.g., EPSG:4326+5773)
            logger.warning(
                "Compound/custom CRS detected (to_epsg returned None). "
                "Forcing to EPSG:4326 — vertical datum may be lost."
            )
            gdf = gdf.to_crs(epsg=4326)
        elif epsg != 4326:
            gdf = gdf.to_crs(epsg=4326)

    logger.info("-> Final geometries ready for export: %d", len(gdf))

    # Pipeline metadata for idempotency tracking
    gdf["_pipeline_stage"] = "cleaned"
    gdf["_processed_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("5. Exporting '%s'...", dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    gdf.to_file(dst, driver="GeoJSON", engine="pyogrio")

    logger.info("Cleaning pipeline completed successfully!")


if __name__ == "__main__":
    from scripts.logging_config import setup
    setup()
    try:
        run()
    except (FileNotFoundError, ValueError) as exc:
        logger.error(exc)
        sys.exit(1)
