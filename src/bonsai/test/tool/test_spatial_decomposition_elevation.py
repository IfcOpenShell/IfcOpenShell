# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.util.placement
import pytest

import bonsai.tool as tool
from bonsai.tool.spatial import Spatial as subject
from test.bim.bootstrap import NewFile


class TestImportSpatialDecomposition(NewFile):
    def create_raised_storey(self):
        bpy.ops.bim.create_project()
        storey = tool.Ifc.get().by_type("IfcBuildingStorey")[0]
        obj = tool.Ifc.get_object(storey)
        obj.location.z = 3.0
        bpy.context.view_layer.update()
        return storey, obj

    def test_moved_storey_placement_is_synced(self):
        storey, _ = self.create_raised_storey()
        subject.import_spatial_decomposition()
        assert ifcopenshell.util.placement.get_storey_elevation(storey) == pytest.approx(3.0)

    def test_unparseable_elevation_leaves_the_placement_untouched(self):
        storey, obj = self.create_raised_storey()
        tool.Geometry.run_edit_object_placement(obj)
        subject.import_spatial_decomposition()
        container = next(c for c in tool.Spatial.get_spatial_props().containers if c.ifc_definition_id == storey.id())
        container.elevation = "not a distance"
        assert obj.matrix_world.translation.z == pytest.approx(3.0)
        assert ifcopenshell.util.placement.get_storey_elevation(storey) == pytest.approx(3.0)
