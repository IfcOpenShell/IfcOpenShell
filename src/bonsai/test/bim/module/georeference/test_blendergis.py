# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Tests for the BlenderGIS bridge against synthetic, BlenderGIS-shaped scene data.

These tests do not exercise the real BlenderGIS addon (which is not
installed here). The scene property keys and value formats used below (a
plain dict standing in for bpy.context.scene, using the exact "SRID",
"crs x", "crs y", "scale" keys) were confirmed by reading BlenderGIS's own
geoscene.py and core/proj/srs.py source on GitHub. See the module docstring
of blendergis.py for details.
"""

import pytest

from bonsai.bim.module.georeference import blendergis

pytestmark = pytest.mark.georeference


class TestNormaliseCrsName:
    def test_a_bare_epsg_code(self):
        assert blendergis.normalise_crs_name("2154") == "EPSG:2154"

    def test_an_already_formatted_srid(self):
        assert blendergis.normalise_crs_name("EPSG:2154") == "EPSG:2154"

    def test_a_lowercase_authority(self):
        assert blendergis.normalise_crs_name("epsg:2154") == "EPSG:2154"

    def test_a_proj4_string_is_passed_through(self):
        proj4 = "+proj=lcc +lat_1=44 +lat_2=49 +lat_0=46.5"
        assert blendergis.normalise_crs_name(proj4) == proj4


class TestReadBlenderGISScene:
    def test_returning_none_when_no_data_is_present(self):
        assert blendergis.read_blendergis_scene({}) is None

    def test_returning_none_when_only_the_crs_is_set(self):
        assert blendergis.read_blendergis_scene({"SRID": "2154"}) is None

    def test_returning_none_when_only_the_origin_is_set(self):
        assert blendergis.read_blendergis_scene({"crs x": 1.0, "crs y": 2.0}) is None

    def test_reading_a_fully_georeferenced_scene(self):
        scene = {"SRID": "2154", "crs x": 500000.0, "crs y": 6500000.0}
        data = blendergis.read_blendergis_scene(scene)
        assert data.crs_name == "EPSG:2154"
        assert data.eastings == 500000.0
        assert data.northings == 6500000.0
        assert data.scale == 1.0

    def test_reading_a_scene_with_a_non_default_scale(self):
        scene = {"SRID": "2154", "crs x": 0.0, "crs y": 0.0, "scale": 2.0}
        data = blendergis.read_blendergis_scene(scene)
        assert data.scale == 2.0

    def test_reading_longitude_and_latitude_when_present(self):
        scene = {"SRID": "2154", "crs x": 0.0, "crs y": 0.0, "longitude": 2.5, "latitude": 47.5}
        data = blendergis.read_blendergis_scene(scene)
        assert data.longitude == 2.5
        assert data.latitude == 47.5


class TestComputeMapConversion:
    def test_with_no_blender_offset(self):
        data = blendergis.BlenderGISGeoreference(
            crs_name="EPSG:2154", eastings=500000.0, northings=6500000.0, scale=1.0
        )
        conversion = blendergis.compute_map_conversion(data)
        assert conversion == {
            "Eastings": 500000.0,
            "Northings": 6500000.0,
            "OrthogonalHeight": 0.0,
            "XAxisAbscissa": 1.0,
            "XAxisOrdinate": 0.0,
            "Scale": 1.0,
        }

    def test_with_a_blender_offset(self):
        data = blendergis.BlenderGISGeoreference(
            crs_name="EPSG:2154", eastings=500000.0, northings=6500000.0, scale=1.0
        )
        conversion = blendergis.compute_map_conversion(data, blender_offset=(100.0, 200.0, 3.0))
        assert conversion["Eastings"] == 499900.0
        assert conversion["Northings"] == 6499800.0
        assert conversion["OrthogonalHeight"] == -3.0

    def test_with_a_non_default_scale_and_a_blender_offset(self):
        data = blendergis.BlenderGISGeoreference(crs_name="EPSG:2154", eastings=1000.0, northings=2000.0, scale=2.0)
        conversion = blendergis.compute_map_conversion(data, blender_offset=(10.0, 10.0, 0.0))
        assert conversion["Eastings"] == 1000.0 - 2.0 * 10.0
        assert conversion["Northings"] == 2000.0 - 2.0 * 10.0
        assert conversion["Scale"] == 2.0
