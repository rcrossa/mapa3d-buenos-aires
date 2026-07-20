"""
Tests for the solar calculation pipeline (scripts/calculo_solar.py).
"""
import json
import os
import sys
import tempfile
import unittest

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

# Ensure repositorio/ is on sys.path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
        self.output_path = self.input_path  # in-place by design

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

        # id=1 has area_util=50 → panels=25 → savings > 0 → payback > 0
        self.assertGreater(row1["payback_anios"], 0)
        # id=2 has area_util=0 → payback should be 0
        self.assertEqual(row2["payback_anios"], 0)

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


if __name__ == "__main__":
    unittest.main()
