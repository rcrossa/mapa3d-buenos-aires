"""
Tests for the solar calculation pipeline (scripts/calculo_solar.py).
"""
import json
import os
import shutil
import tempfile
import unittest

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

from scripts.calculo_solar import run


class TestCalculoSolar(unittest.TestCase):
    """Unit tests for solar + financial calculations."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.processed_dir = os.path.join(self.tmpdir, "data", "processed")
        os.makedirs(self.processed_dir)

        self.input_path = os.path.join(
            self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
        )
        # Use separate output so we can test non-atomic write path too
        self.output_path = os.path.join(
            self.processed_dir, "enriched.geojson"
        )

        # Build a small GeoDataFrame with area_util values
        gdf = gpd.GeoDataFrame(
            {
                "id": [1, 2, 3],
                "area_util": [50.0, 0.0, 100.0],
                "altura": [5.0, 10.0, 15.0],
            },
            geometry=[
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
                Polygon([(4, 0), (5, 0), (5, 1), (4, 1)]),
            ],
            crs="EPSG:4326",
        )
        gdf.to_file(self.input_path, driver="GeoJSON")

        # Write a minimal config for test constants
        self.config_path = os.path.join(self.tmpdir, "test_config.json")
        with open(self.config_path, "w") as f:
            json.dump(
                {
                    "solar": {
                        "radiacion_anual_caba": 1600,
                        "eficiencia_panel": 0.20,
                        "pr": 0.80,
                        "area_por_panel": 2.0,
                    },
                    "financiero": {
                        "tarifa_kwh_ars": 85.00,
                        "costo_instalacion_por_panel": 450000,
                    },
                },
                f,
            )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_run_produces_columns(self):
        """Pipeline should add expected solar columns."""
        run(
            input_path=self.input_path,
            output_path=self.output_path,
            config_path=self.config_path,
        )
        result = gpd.read_file(self.output_path)
        for col in [
            "paneles_viables",
            "energia_anual_kwh",
            "ahorro_anual_ars",
            "costo_instalacion_ars",
            "payback_anios",
        ]:
            self.assertIn(col, result.columns, f"Missing column: {col}")

    def test_zero_area_no_panels(self):
        """Buildings with area_util=0 should have 0 panels and 0 energy."""
        run(
            input_path=self.input_path,
            output_path=self.output_path,
            config_path=self.config_path,
        )
        result = gpd.read_file(self.output_path)
        row = result[result["id"] == 2].iloc[0]
        self.assertEqual(row["paneles_viables"], 0)
        self.assertEqual(row["energia_anual_kwh"], 0)

    def test_payback_calculation(self):
        """Payback should be cost / savings when savings > 0, else 0."""
        run(
            input_path=self.input_path,
            output_path=self.output_path,
            config_path=self.config_path,
        )
        result = gpd.read_file(self.output_path)
        row1 = result[result["id"] == 1].iloc[0]
        row2 = result[result["id"] == 2].iloc[0]
        self.assertGreater(row1["payback_anios"], 0)
        self.assertEqual(row2["payback_anios"], 0.0)

    def test_energy_formula(self):
        """Energy formula: area * radiacion * eficiencia * PR."""
        run(
            input_path=self.input_path,
            output_path=self.output_path,
            config_path=self.config_path,
        )
        result = gpd.read_file(self.output_path)
        row = result[result["id"] == 1].iloc[0]
        expected = int(50.0 * 1600 * 0.20 * 0.80)  # = 12800
        self.assertEqual(row["energia_anual_kwh"], expected)

    def test_nan_area_util_is_zero_filled(self):
        """NaN in area_util should be treated as 0, not propagate NaN."""
        gdf = gpd.GeoDataFrame(
            {"id": [1], "area_util": [np.nan], "altura": [5.0]},
            geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            crs="EPSG:4326",
        )
        nan_file = os.path.join(self.processed_dir, "nan_input.geojson")
        gdf.to_file(nan_file, driver="GeoJSON")
        out = os.path.join(self.processed_dir, "nan_output.geojson")
        run(input_path=nan_file, output_path=out, config_path=self.config_path)
        result = gpd.read_file(out)
        self.assertEqual(result.iloc[0]["paneles_viables"], 0)
        self.assertEqual(result.iloc[0]["energia_anual_kwh"], 0)
        self.assertEqual(result.iloc[0]["ahorro_anual_ars"], 0)
        self.assertEqual(result.iloc[0]["payback_anios"], 0.0)

    def test_negative_area_util(self):
        """Negative area_util produces negative energy (data warning)."""
        gdf = gpd.GeoDataFrame(
            {"id": [1], "area_util": [-50.0], "altura": [5.0]},
            geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            crs="EPSG:4326",
        )
        neg_file = os.path.join(self.processed_dir, "neg_input.geojson")
        gdf.to_file(neg_file, driver="GeoJSON")
        out = os.path.join(self.processed_dir, "neg_output.geojson")
        run(input_path=neg_file, output_path=out, config_path=self.config_path)
        result = gpd.read_file(out)
        # paneles_viables rounds to int, negative area → negative panels
        self.assertEqual(result.iloc[0]["paneles_viables"], -25)
        self.assertLess(result.iloc[0]["energia_anual_kwh"], 0)

    def test_config_zero_area_raises(self):
        """Config with area_por_panel=0 should raise ValueError."""
        bad_config = os.path.join(self.tmpdir, "bad_config.json")
        with open(bad_config, "w") as f:
            json.dump(
                {
                    "solar": {"area_por_panel": 0},
                    "financiero": {},
                },
                f,
            )
        with self.assertRaises(ValueError):
            run(
                input_path=self.input_path,
                output_path=self.output_path,
                config_path=bad_config,
            )

    def test_missing_file_raises(self):
        """Missing input file should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            run(input_path="/nonexistent/path.geojson")

    def test_missing_area_util_raises(self):
        """Input without 'area_util' column should raise KeyError."""
        gdf = gpd.GeoDataFrame(
            {"id": [1], "altura": [5.0]},
            geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            crs="EPSG:4326",
        )
        bad_file = os.path.join(self.processed_dir, "no_area.geojson")
        gdf.to_file(bad_file, driver="GeoJSON")
        with self.assertRaises(KeyError):
            run(
                input_path=bad_file,
                output_path=self.output_path,
                config_path=self.config_path,
            )

    def test_invalid_config_json_uses_defaults(self):
        """Malformed config.json should log warning and use defaults."""
        bad_json = os.path.join(self.tmpdir, "malformed.json")
        with open(bad_json, "w") as f:
            f.write("{invalid json")
        # Should not raise — falls back to defaults
        run(
            input_path=self.input_path,
            output_path=self.output_path,
            config_path=bad_json,
        )
        result = gpd.read_file(self.output_path)
        self.assertIn("energia_anual_kwh", result.columns)


if __name__ == "__main__":
    unittest.main()
