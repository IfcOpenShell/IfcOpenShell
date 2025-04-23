# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import bonsai.core.georeference as subject
from test.core.bootstrap import ifc, georeference


class TestAddGeoreferencing:
    def test_run(self, georeference):
        georeference.add_georeferencing().should_be_called()
        subject.add_georeferencing(georeference)


class TestEnableEditingGeoreferencing:
    def test_run(self, georeference):
        georeference.import_projected_crs().should_be_called()
        georeference.import_coordinate_operation().should_be_called()
        georeference.enable_editing().should_be_called()
        subject.enable_editing_georeferencing(georeference)


class TestRemoveGeoreferencing:
    def test_run(self, ifc):
        ifc.run("georeference.remove_georeferencing").should_be_called()
        subject.remove_georeferencing(ifc)


class TestDisableEditingGeoreferencing:
    def test_run(self, georeference):
        georeference.disable_editing().should_be_called()
        subject.disable_editing_georeferencing(georeference)


class TestEditGeoreferencing:
    def test_run(self, ifc, georeference):
        georeference.export_projected_crs().should_be_called().will_return("projected_crs_attributes")
        georeference.export_coordinate_operation().should_be_called().will_return("coordinate_operation_attributes")
        ifc.run(
            "georeference.edit_georeferencing",
            projected_crs="projected_crs_attributes",
            coordinate_operation="coordinate_operation_attributes",
        ).should_be_called()
        georeference.disable_editing().should_be_called()
        georeference.set_model_origin().should_be_called()
        subject.edit_georeferencing(ifc, georeference)


class TestGetCursorLocation:
    def test_run(self, georeference):
        georeference.get_cursor_location().should_be_called().will_return("coordinates")
        georeference.has_blender_offset().should_be_called().will_return(False)
        georeference.set_coordinates("local", "coordinates").should_be_called()
        subject.get_cursor_location(georeference)

    def test_with_a_blender_offset(self, georeference):
        georeference.get_cursor_location().should_be_called().will_return("coordinates")
        georeference.has_blender_offset().should_be_called().will_return(True)
        georeference.set_coordinates("blender", "coordinates").should_be_called()
        subject.get_cursor_location(georeference)


class TestEnableEditingWCS:
    def test_run(self, georeference):
        georeference.import_wcs().should_be_called()
        georeference.enable_editing_wcs().should_be_called()
        subject.enable_editing_wcs(georeference)


class TestDisableEditingWCS:
    def test_run(self, georeference):
        georeference.disable_editing_wcs().should_be_called()
        subject.disable_editing_wcs(georeference)


class TestEditWCS:
    def test_run(self, georeference):
        georeference.export_wcs().should_be_called().will_return("wcs")
        georeference.set_wcs("wcs").should_be_called()
        georeference.disable_editing_wcs().should_be_called()
        georeference.set_model_origin().should_be_called()
        subject.edit_wcs(georeference)


class TestEnableEditingTrueNorth:
    def test_run(self, georeference):
        georeference.import_true_north().should_be_called()
        georeference.enable_editing_true_north().should_be_called()
        subject.enable_editing_true_north(georeference)


class TestDisableEditingTrueNorth:
    def test_run(self, georeference):
        georeference.disable_editing_true_north().should_be_called()
        subject.disable_editing_true_north(georeference)


class TestEditTrueNorth:
    def test_run(self, ifc, georeference):
        georeference.get_true_north_attributes().should_be_called().will_return("true_north")
        ifc.run("georeference.edit_true_north", true_north="true_north").should_be_called()
        georeference.disable_editing_true_north().should_be_called()
        subject.edit_true_north(ifc, georeference)


class TestRemoveTrueNorth:
    def test_run(self, ifc):
        ifc.run("georeference.edit_true_north", true_north=None).should_be_called()
        subject.remove_true_north(ifc)
