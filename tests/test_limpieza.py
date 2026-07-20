"""
Tests for the geo cleaning pipeline (scripts/limpieza.py).
"""
import os
import sys
import tempfile
import unittest

import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

# Ensure repositorio/ is on sys.path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.limpieza import run


class TestLimpieza(unittest.TestCase):
    """Unit tests for the cleaning pipeline."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.raw_dir = os.path.join(self.tmpdir, "data", "raw")
        self.processed_dir = os.path.join(self.tmpdir, "data", "processed")
        os.makedirs(self.raw_dir)
        os.makedirs(self.processed_dir)

        # Build a small GeoDataFrame with mixed geometry types
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        multi = MultiPolygon([poly, Polygon([(20, 0), (30, 0), (30, 10), (20, 10)])])
        self.gdf = gpd.GeoDataFrame(
            {"id": [1, 2], "altura": [5.0, 10.0]},
            geometry=[poly, multi],
            crs="EPSG:4326",
        )
        self.gdf.to_file(
            os.path.join(self.raw_dir, "buenos_aires_3d_base.geojson"),
            driver="GeoJSON",
        )

    def test_run_produces_output(self):
        """Pipeline should produce a valid output GeoJSON."""
        run(
            input_path=os.path.join(self.raw_dir, "buenos_aires_3d_base.geojson"),
            output_path=os.path.join(
                self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
            ),
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
                )
            )
        )

    def test_crs_is_4326(self):
        """Output CRS must be EPSG:4326."""
        out = os.path.join(
            self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
        )
        run(
            input_path=os.path.join(self.raw_dir, "buenos_aires_3d_base.geojson"),
            output_path=out,
        )
        result = gpd.read_file(out)
        self.assertEqual(result.crs.to_epsg(), 4326)

    def test_explode_multipolygon(self):
        """MultiPolygon input should be exploded to individual Polygons."""
        out = os.path.join(
            self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
        )
        run(
            input_path=os.path.join(self.raw_dir, "buenos_aires_3d_base.geojson"),
            output_path=out,
        )
        result = gpd.read_file(out)
        # 1 Polygon + 1 MultiPolygon(2) = 3 rows after explode
        self.assertEqual(len(result), 3)
        for geom in result.geometry:
            self.assertEqual(geom.geom_type, "Polygon")


if __name__ == "__main__":
    unittest.main()
