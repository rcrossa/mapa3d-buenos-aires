import copy
import geopandas as gpd
import json
import logging
import math
import numpy as np
import os
import sys
import tempfile
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join(
    "data", "processed", "buenos_aires_3d_completo_limpio.geojson"
)
OUTPUT_PATH = INPUT_PATH  # in-place enrichment
CONFIG_PATH = os.path.join("config.json")

# Sensible defaults (used when config.json is missing)
_DEFAULT_SOLAR = {
    "radiacion_anual_caba": 1600,
    "eficiencia_panel": 0.20,
    "pr": 0.80,
    "area_por_panel": 2.0,
}
_DEFAULT_FINANCIERO = {
    "tarifa_kwh_ars": 85.00,
    "costo_instalacion_por_panel": 450000,
}

_EXPECTED_SOLAR_KEYS = frozenset(_DEFAULT_SOLAR.keys())
_EXPECTED_FINANCIERO_KEYS = frozenset(_DEFAULT_FINANCIERO.keys())


def _load_config(config_path=None):
    """Load solar + financial constants from config.json.

    Returns deep copies so callers cannot mutate the module-level defaults.
    Warns on unknown or missing keys.
    """
    path = config_path or CONFIG_PATH
    solar = copy.deepcopy(_DEFAULT_SOLAR)
    financiero = copy.deepcopy(_DEFAULT_FINANCIERO)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Could not parse %s: %s. Using defaults.", path, exc
            )
            return solar, financiero

        user_solar = cfg.get("solar", {})
        user_fin = cfg.get("financiero", {})

        if not isinstance(user_solar, dict):
            logger.warning(
                "config.json 'solar' is not a dict (got %s). Using defaults.",
                type(user_solar).__name__
            )
            user_solar = {}
        if not isinstance(user_fin, dict):
            logger.warning(
                "config.json 'financiero' is not a dict (got %s). Using defaults.",
                type(user_fin).__name__
            )
            user_fin = {}

        # Warn on unknown keys (typo detection)
        unknown_solar = set(user_solar.keys()) - _EXPECTED_SOLAR_KEYS
        unknown_fin = set(user_fin.keys()) - _EXPECTED_FINANCIERO_KEYS
        for uk in unknown_solar:
            logger.warning("Unknown solar config key: %s (typo?)", uk)
        for uk in unknown_fin:
            logger.warning("Unknown financiero config key: %s (typo?)", uk)

        solar.update(user_solar)
        financiero.update(user_fin)
        logger.info("Loaded config from %s", path)
    else:
        logger.warning("config.json not found, using defaults")

    return solar, financiero


def _validate_config(solar_cfg, fin_cfg):
    """Raise ValueError if any required config value is zero, negative, or non-finite."""
    for key in ("area_por_panel", "radiacion_anual_caba",
                "eficiencia_panel", "pr"):
        val = solar_cfg[key]
        if not isinstance(val, (int, float)) or not math.isfinite(val):
            raise ValueError(
                f"config.json solar.{key} must be a finite number, got {val!r}"
            )
        if val <= 0:
            raise ValueError(
                f"config.json solar.{key} must be > 0, got {val}"
            )
    for key in ("tarifa_kwh_ars", "costo_instalacion_por_panel"):
        val = fin_cfg[key]
        if not isinstance(val, (int, float)) or not math.isfinite(val):
            raise ValueError(
                f"config.json financiero.{key} must be a finite number, got {val!r}"
            )
        if val < 0:
            raise ValueError(
                f"config.json financiero.{key} must be >= 0, got {val}"
            )


def run(input_path=None, output_path=None, config_path=None):
    """Run solar calculation pipeline.

    Args:
        input_path: Path to cleaned GeoJSON. Defaults to INPUT_PATH.
        output_path: Path for enriched output. Defaults to OUTPUT_PATH.
                     Writes atomically (temp file + rename) if same as input.
        config_path: Path to config.json. Defaults to CONFIG_PATH.

    Raises:
        FileNotFoundError: If input file is missing.
        ValueError: If config values are invalid.
        KeyError: If required column 'area_util' is missing.
    """
    src = input_path or INPUT_PATH
    dst = output_path or OUTPUT_PATH
    solar_cfg, fin_cfg = _load_config(config_path)
    _validate_config(solar_cfg, fin_cfg)

    logger.info("1. Loading processed buildings...")
    if not os.path.exists(src):
        logger.error("File not found: %s", src)
        raise FileNotFoundError(
            f"Input file not found: {src}. Run limpieza.py first."
        )

    gdf = gpd.read_file(src)
    logger.info("-> Buildings loaded: %d", len(gdf))

    # Idempotency guard: prevent re-processing already-enriched data.
    # Re-running on enriched output would double all energy/financial values.
    if "energia_anual_kwh" in gdf.columns:
        logger.error(
            "Input file already contains 'energia_anual_kwh' column. "
            "Re-running would double all values. "
            "Run limpieza.py first to regenerate clean input."
        )
        raise ValueError(
            "Input already enriched — re-running would corrupt data."
        )

    if "area_util" not in gdf.columns:
        logger.error("Required column 'area_util' missing from input.")
        raise KeyError(
            "Column 'area_util' not found in input GeoJSON. "
            "Did limpieza.py run successfully?"
        )

    if "altura" not in gdf.columns:
        logger.warning(
            "Column 'altura' missing. 3D extrusion will render at height 0."
        )

    logger.info("2. Applying physical and financial model...")
    rad = solar_cfg["radiacion_anual_caba"]
    eff = solar_cfg["eficiencia_panel"]
    pr_val = solar_cfg["pr"]
    area = solar_cfg["area_por_panel"]
    tarifa = fin_cfg["tarifa_kwh_ars"]
    costo = fin_cfg["costo_instalacion_por_panel"]

    # Defensive: prevent ZeroDivisionError even if validation is somehow bypassed
    if area <= 0:
        raise ValueError(
            f"area_por_panel must be > 0, got {area}. Check config.json."
        )

    # Fill NaN in area_util before any computation to prevent NaN propagation
    area_util = gdf["area_util"].fillna(0)

    neg_count = (area_util < 0).sum()
    if neg_count > 0:
        logger.warning(
            "Found %d rows with negative area_util. Results may be invalid.",
            neg_count
        )

    # Range validation: detect suspiciously large values (possible wrong units)
    if (area_util > 10000).any():
        logger.warning(
            "Found %d rows with area_util > 10000 m\u00b2. "
            "This may indicate wrong units (cm\u00b2 instead of m\u00b2). "
            "Verify input data.",
            (area_util > 10000).sum()
        )

    gdf["paneles_viables"] = (area_util / area).astype(int)

    # Detect truncation: roofs with positive area that rounded to zero panels
    truncated = (area_util > 0) & (gdf["paneles_viables"] == 0)
    if truncated.sum() > 0:
        logger.warning(
            "Found %d rows with area_util > 0 but paneles_viables = 0 "
            "(area < %.1f m\u00b2 per panel). These roofs have solar "
            "potential but are too small for the configured panel size.",
            truncated.sum(), area
        )
    gdf["energia_anual_kwh"] = area_util * rad * eff * pr_val
    gdf["ahorro_anual_ars"] = gdf["energia_anual_kwh"] * tarifa
    gdf["costo_instalacion_ars"] = gdf["paneles_viables"] * costo

    # Compute payback: cost / savings, only for buildings with positive savings.
    # Avoids ZeroDivisionError on 0/0 (NaN area→0 energy→0 savings→0/0).
    gdf["payback_anios"] = 0.0
    positive = gdf["ahorro_anual_ars"] > 0
    if positive.any():
        gdf.loc[positive, "payback_anios"] = (
            gdf.loc[positive, "costo_instalacion_ars"]
            / gdf.loc[positive, "ahorro_anual_ars"]
        )

    logger.info("3. Rounding values for web UI...")
    gdf["energia_anual_kwh"] = (
        gdf["energia_anual_kwh"].fillna(0).round(0).astype(int)
    )
    gdf["ahorro_anual_ars"] = (
        gdf["ahorro_anual_ars"].fillna(0).round(0).astype(int)
    )
    gdf["costo_instalacion_ars"] = (
        gdf["costo_instalacion_ars"].fillna(0).round(0).astype(int)
    )
    gdf["payback_anios"] = gdf["payback_anios"].fillna(0).round(1)

    # Pipeline metadata for idempotency tracking
    gdf["_pipeline_stage"] = "enriched"
    gdf["_processed_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("4. Saving enriched database...")
    try:
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    except PermissionError as e:
        logger.error("Cannot create output directory: %s", e)
        raise

    # Atomic write: temp file + rename to avoid corrupting data on crash
    write_atomic = (
        os.path.realpath(os.path.abspath(src))
        == os.path.realpath(os.path.abspath(dst))
    )
    if write_atomic:
        dst_dir = os.path.dirname(dst) or "."
        tmp_fd, tmp_path = tempfile.mkstemp(
            suffix=".geojson", dir=dst_dir
        )
        os.close(tmp_fd)
        try:
            gdf.to_file(tmp_path, driver="GeoJSON")
            try:
                os.replace(tmp_path, dst)
            except OSError:
                # Cross-device: fall back to copy + unlink
                import shutil
                shutil.copy2(tmp_path, dst)
                os.unlink(tmp_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    else:
        gdf.to_file(dst, driver="GeoJSON")

    logger.info("Solar calculation completed successfully!")


if __name__ == "__main__":
    from scripts.logging_config import setup
    setup()
    try:
        run()
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)
