"""
Tests for the geo cleaning pipeline (scripts/limpieza.py).
"""
import os
import shutil
import tempfile
import unittest

import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

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
        self.input_file = os.path.join(
            self.raw_dir, "buenos_aires_3d_base.geojson"
        )
        self.output_file = os.path.join(
            self.processed_dir, "buenos_aires_3d_completo_limpio.geojson"
        )
        self.gdf.to_file(self.input_file, driver="GeoJSON")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_run_produces_output(self):
        """Pipeline should produce a valid output GeoJSON."""
        run(input_path=self.input_file, output_path=self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

    def test_crs_is_4326(self):
        """Output CRS must be EPSG:4326."""
        run(input_path=self.input_file, output_path=self.output_file)
        result = gpd.read_file(self.output_file)
        self.assertEqual(result.crs.to_epsg(), 4326)

    def test_explode_multipolygon(self):
        """MultiPolygon input should be exploded to individual Polygons."""
        run(input_path=self.input_file, output_path=self.output_file)
        result = gpd.read_file(self.output_file)
        # 1 Polygon + 1 MultiPolygon(2) = 3 rows after explode
        self.assertEqual(len(result), 3)
        for geom in result.geometry:
            self.assertEqual(geom.geom_type, "Polygon")

    def test_missing_file_raises(self):
        """Missing input file should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            run(input_path="/nonexistent/path.geojson")

    def test_empty_input_raises(self):
        """Empty GeoJSON should raise ValueError."""
        empty_file = os.path.join(self.raw_dir, "empty.geojson")
        gdf = gpd.GeoDataFrame({"id": []}, geometry=[], crs="EPSG:4326")
        gdf.to_file(empty_file, driver="GeoJSON")
        with self.assertRaises(ValueError):
            run(input_path=empty_file)

    def test_crs_none_reprojection(self):
        """Input with no CRS should be assigned EPSG:4326."""
        gdf_nocrs = self.gdf.copy()
        gdf_nocrs.crs = None
        nocrs_file = os.path.join(self.raw_dir, "no_crs.geojson")
        gdf_nocrs.to_file(nocrs_file, driver="GeoJSON")
        run(input_path=nocrs_file, output_path=self.output_file)
        result = gpd.read_file(self.output_file)
        self.assertEqual(result.crs.to_epsg(), 4326)


if __name__ == "__main__":
    unittest.main()
