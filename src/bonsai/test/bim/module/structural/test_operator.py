# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace
from unittest import mock

import bpy
import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.operator import PickStructuralLoads
from test.bim.bootstrap import NewFile


class TestLoadBoundaryConditions(NewFile):
    def test_filtering_duplicate_names(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Pinned")
        props = tool.Structural.get_structural_props()
        props.filtered_boundary_conditions = True
        bpy.ops.bim.load_boundary_conditions()
        assert sorted(c.name for c in props.boundary_conditions) == ["Pinned"]


class TestLoadStructuralLoads(NewFile):
    def test_unused_only(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        point = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralPointConnection")
        used = ifcopenshell.api.structural.add_structural_load(
            ifc, name="Used", ifc_class="IfcStructuralLoadSingleForce"
        )
        ifcopenshell.api.structural.add_structural_load(ifc, name="Unused", ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, applied_load=used, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        case = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Case")
        ifcopenshell.api.group.assign_group(ifc, products=[activity], group=case)
        props = tool.Structural.get_structural_props()
        props.show_unused_loads_only = True  # Which lists the loads again.
        assert [load.name for load in props.structural_loads] == ["Unused"]
        props.show_unused_loads_only = False
        assert sorted(load.name for load in props.structural_loads) == ["Unused", "Used"]


class TestShowStructuralLoadCase(NewFile):
    def test_showing_and_hiding_a_load_case(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        case = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Case")
        model.LoadedBy = [case]
        LoadGroupDecorationData.is_loaded = False
        props = tool.Structural.get_structural_props()
        props.activity_type = "Action"
        bpy.ops.bim.show_structural_load_case(load_case=case.id())
        assert props.show_loads and props.load_group_to_show == str(case.id())
        # Clicking the open eye of the case shown hides the loads.
        bpy.ops.bim.show_structural_load_case(load_case=case.id())
        assert not props.show_loads


def region(type, x, y, width, height, data=None):
    return SimpleNamespace(type=type, x=x, y=y, width=width, height=height, data=data)


class TestGetViewUnderMouse:
    def get(self, regions, x, y):
        area = SimpleNamespace(type="VIEW_3D", regions=regions)
        context = SimpleNamespace(window=SimpleNamespace(screen=SimpleNamespace(areas=[area])))
        return PickStructuralLoads.get_view_under_mouse(None, context, SimpleNamespace(mouse_x=x, mouse_y=y))

    def test_the_view_of_the_quarter_of_a_quad_view_under_the_mouse(self):
        left, right = region("WINDOW", 0, 0, 100, 100, "left"), region("WINDOW", 100, 0, 100, 100, "right")
        assert self.get([left, right], 150, 50)[1:] == (right, "right")

    def test_not_under_a_sidebar_lying_over_the_view(self):
        view = region("WINDOW", 0, 0, 200, 100, "view")
        sidebar = region("UI", 150, 0, 50, 100)
        assert self.get([view, sidebar], 175, 50) is None
        assert self.get([view, sidebar], 75, 50)[1] is view

    def test_a_hidden_sidebar_takes_nothing(self):
        view = region("WINDOW", 0, 0, 200, 100, "view")
        assert self.get([view, region("UI", 199, 0, 1, 100)], 199, 50)[1] is view


class TestPickLoads:
    def pick(self, x, y):
        LoadsDecorator.shader_info = [{}]
        LoadsDecorator.pickables = [{"tail": (0.0, 0.0, 0.0), "tip": (100.0, 0.0, 0.0), "activity": 7, "info": 0}]
        # Viewed from the front, as if X and Z were the region's x and y.
        project = lambda region, rv3d, point: Vector((point.x, point.z))
        with mock.patch("bonsai.bim.module.structural.decorator.location_3d_to_region_2d", project):
            try:
                return LoadsDecorator.pick(None, None, x, y)
            finally:
                LoadsDecorator.pickables, LoadsDecorator.shader_info = [], []

    def test_an_arrow_within_a_few_pixels(self):
        assert self.pick(60, 5)["activity"] == 7
        assert self.pick(60, 15) is None

    def test_not_at_its_tail_where_its_point_is_selected(self):
        assert self.pick(5, 0) is None
