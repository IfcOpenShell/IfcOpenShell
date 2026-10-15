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

import bpy
import ifcopenshell.util.placement
import pytest

import bonsai.tool as tool
from bonsai.tool.spatial import Spatial as subject
from test.bim.bootstrap import NewIfc


class TestImportSpatialDecomposition(NewIfc):
    def create_raised_storey(self):
        storey = tool.Ifc.get().by_type("IfcBuildingStorey")[0]
        obj = tool.Ifc.get_object(storey)
        obj.location.z = 3.0
        bpy.context.view_layer.update()
        return storey, obj

    def test_moved_storey_placement_is_synced(self):
        storey, _ = self.create_raised_storey()
        props = tool.Blender.get_bim_props()
        props.is_dirty = False
        subject.import_spatial_decomposition()
        assert ifcopenshell.util.placement.get_storey_elevation(storey) == pytest.approx(3.0)
        container = next(c for c in tool.Spatial.get_spatial_props().containers if c.ifc_definition_id == storey.id())
        assert container.elevation == tool.Unit.format_distance(3.0)
        assert props.is_dirty

    def test_unparseable_elevation_leaves_the_placement_untouched(self):
        storey, obj = self.create_raised_storey()
        tool.Geometry.run_edit_object_placement(obj)
        subject.import_spatial_decomposition()
        container = next(c for c in tool.Spatial.get_spatial_props().containers if c.ifc_definition_id == storey.id())
        container.elevation = "not a distance"
        assert obj.matrix_world.translation.z == pytest.approx(3.0)
        assert ifcopenshell.util.placement.get_storey_elevation(storey) == pytest.approx(3.0)
        assert container.elevation == tool.Unit.format_distance(3.0)

    def test_unparseable_elevation_restores_storey_elevation_attribute(self):
        storey, obj = self.create_raised_storey()
        tool.Geometry.record_object_position(obj)
        storey.ObjectPlacement = None
        storey.Elevation = 5.0
        subject.import_spatial_decomposition()
        container = next(c for c in tool.Spatial.get_spatial_props().containers if c.ifc_definition_id == storey.id())
        assert container.elevation == tool.Unit.format_distance(5.0)
        container.elevation = "not a distance"
        assert container.elevation == tool.Unit.format_distance(5.0)

    def test_rebuild_does_not_write_placements_to_ifc(self):
        storey, obj = self.create_raised_storey()
        tool.Geometry.run_edit_object_placement(obj)
        subject.import_spatial_decomposition()
        ifc = tool.Ifc.get()
        placements = [e.id() for e in ifc.by_type("IfcLocalPlacement")]
        subject.import_spatial_decomposition()
        assert [e.id() for e in ifc.by_type("IfcLocalPlacement")] == placements
