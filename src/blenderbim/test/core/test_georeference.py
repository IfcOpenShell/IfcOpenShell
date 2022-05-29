# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.core.georeference as subject
from test.core.bootstrap import ifc, georeference


class TestAddGeoreferencing:
    def test_run(self, ifc):
        ifc.run("georeference.add_georeferencing").should_be_called()
        subject.add_georeferencing(ifc)


class TestEnableGeoreferencing:
    def test_run(self, georeference):
        georeference.import_projected_crs().should_be_called()
        georeference.import_map_conversion().should_be_called()
        georeference.import_true_north().should_be_called()
        georeference.enable_editing().should_be_called()
        subject.enable_editing_georeferencing(georeference)


class TestRemoveGeoreferencing:
    def test_run(self, ifc):
        ifc.run("georeference.remove_georeferencing").should_be_called()
        subject.remove_georeferencing(ifc)


class TestEditGeoreferencing:
    def test_run(self, ifc, georeference):
        georeference.get_projected_crs_attributes().should_be_called().will_return("projected_crs_attributes")
        georeference.get_map_conversion_attributes().should_be_called().will_return("map_conversion_attributes")
        georeference.get_true_north_attributes().should_be_called().will_return("true_north_attributes")
        ifc.run(
            "georeference.edit_georeferencing",
            projected_crs="projected_crs_attributes",
            map_conversion="map_conversion_attributes",
            true_north="true_north_attributes",
        ).should_be_called()
        georeference.disable_editing().should_be_called()
        subject.edit_georeferencing(ifc, georeference)


class TestSetIfcGridNorth:
    def test_run(self, georeference):
        georeference.set_ifc_grid_north().should_be_called()
        subject.set_ifc_grid_north(georeference)


class TestSetBlenderGridNorth:
    def test_run(self, georeference):
        georeference.set_blender_grid_north().should_be_called()
        subject.set_blender_grid_north(georeference)


class TestSetIfcTrueNorth:
    def test_run(self, georeference):
        georeference.set_ifc_true_north().should_be_called()
        subject.set_ifc_true_north(georeference)


class TestSetBlenderTrueNorth:
    def test_run(self, georeference):
        georeference.set_blender_true_north().should_be_called()
        subject.set_blender_true_north(georeference)


class TestGetCursorLocation:
    def test_run(self, georeference):
        georeference.get_cursor_location().should_be_called().will_return("coordinates")
        georeference.set_coordinates("input", "coordinates").should_be_called()
        subject.get_cursor_location(georeference)


class TestSetCursorLocation:
    def test_run(self, georeference):
        georeference.get_coordinates("output").should_be_called().will_return("coordinates")
        georeference.set_cursor_location("coordinates").should_be_called()
        subject.set_cursor_location(georeference)


class TestConvertLocalToGlobal:
    def test_run(self, georeference):
        georeference.get_coordinates("input").should_be_called().will_return("coordinates")
        georeference.get_map_conversion().should_be_called().will_return("map_conversion")
        georeference.xyz2enh("coordinates", "map_conversion").should_be_called().will_return("enh")
        georeference.set_coordinates("output", "enh").should_be_called()
        georeference.set_cursor_location("enh").should_be_called()
        subject.convert_local_to_global(georeference)


class TestConvertGlobalToLocal:
    def test_run(self, georeference):
        georeference.get_coordinates("input").should_be_called().will_return("coordinates")
        georeference.get_map_conversion().should_be_called().will_return("map_conversion")
        georeference.enh2xyz("coordinates", "map_conversion").should_be_called().will_return("xyz")
        georeference.set_coordinates("output", "xyz").should_be_called()
        georeference.set_cursor_location("xyz").should_be_called()
        subject.convert_global_to_local(georeference)
