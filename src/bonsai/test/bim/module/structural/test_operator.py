# This file was generated with the assistance of an AI coding tool.

import math
from types import SimpleNamespace
from unittest import mock

import bpy
import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.api.unit
import ifcopenshell.util.structural
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.operator import PickStructuralLoads, get_load_unit_symbol
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


class TestEnableEditingStructuralItemAxis(NewFile):
    def test_starting_square_to_a_member_stood_up_along_its_axis(self):
        bpy.ops.bim.create_project()
        props = tool.Root.get_root_props()
        props.ifc_product, props.ifc_class, props.representation_template = (
            "IfcStructuralItem",
            "IfcStructuralCurveMember",
            "EDGE",
        )
        bpy.ops.bim.add_element(skip_dialog=True)
        member = tool.Ifc.get().by_type("IfcStructuralCurveMember")[0]
        obj = tool.Ifc.get_object(member)
        bpy.context.view_layer.objects.active = obj
        obj.data.vertices[1].co = obj.data.vertices[0].co + Vector((0.0, 0.0, 3.0))
        assert member.Axis.DirectionRatios == (0.0, 0.0, 1.0)  # Now parallel to the member.

        bpy.ops.bim.enable_editing_structural_item_axis()
        empty = tool.Structural.get_object_structural_props(obj).axis_empty
        x, y, z = (empty.matrix_world.col[i].to_3d() for i in range(3))
        assert abs(x.dot(Vector((0.0, 0.0, 1.0)))) == pytest.approx(1.0)
        assert y.length == pytest.approx(1.0)
        assert abs(z.dot(x)) < 1e-6

        bpy.ops.bim.edit_structural_item_axis()
        assert abs(Vector(member.Axis.DirectionRatios).normalized().z) < 1e-6

    def add_member(self) -> tuple:
        props = tool.Root.get_root_props()
        props.ifc_product, props.ifc_class, props.representation_template = (
            "IfcStructuralItem",
            "IfcStructuralCurveMember",
            "EDGE",
        )
        bpy.ops.bim.add_element(skip_dialog=True)
        member = tool.Ifc.get().by_type("IfcStructuralCurveMember")[-1]
        obj = tool.Ifc.get_object(member)
        bpy.context.view_layer.objects.active = obj
        return member, obj

    def test_keeping_the_axis_of_a_member_rotated_as_a_whole(self):
        # Axis is relative to the member's placement, as its edge is, so it turns with the member.
        bpy.ops.bim.create_project()
        member, obj = self.add_member()
        obj.rotation_euler = (0.0, math.radians(90), 0.0)
        obj.location = (2.0, 3.0, 4.0)
        bpy.context.view_layer.update()
        bpy.ops.bim.enable_editing_structural_item_axis()
        empty = tool.Structural.get_object_structural_props(obj).axis_empty
        assert tool.Structural.get_object_structural_props(obj).axis_angle == pytest.approx(0.0)
        # At the edge's start, wherever the member is.
        assert (empty.matrix_world.translation - obj.matrix_world @ obj.data.vertices[0].co).length < 1e-6
        bpy.ops.bim.edit_structural_item_axis()
        assert tuple(Vector(member.Axis.DirectionRatios)) == pytest.approx((0.0, 0.0, 1.0), abs=1e-6)

    def test_projecting_an_axis_nearly_along_the_member(self):
        bpy.ops.bim.create_project()
        member, obj = self.add_member()
        angle = math.radians(1)
        ifcopenshell.api.structural.edit_structural_item_axis(
            tool.Ifc.get(), structural_item=member, axis=(math.cos(angle), 0.0, math.sin(angle))
        )
        bpy.ops.bim.enable_editing_structural_item_axis()
        bpy.ops.bim.edit_structural_item_axis()
        assert tuple(Vector(member.Axis.DirectionRatios)) == pytest.approx((0.0, 0.0, 1.0), abs=1e-6)

    def test_rolling_the_axis_about_the_member(self):
        bpy.ops.bim.create_project()
        member, obj = self.add_member()
        obj.rotation_euler = (0.0, 0.0, math.radians(90))  # Along world Y; the roll is about the member itself.
        bpy.context.view_layer.update()
        bpy.ops.bim.enable_editing_structural_item_axis()
        tool.Structural.get_object_structural_props(obj).axis_angle = 90.0
        bpy.ops.bim.edit_structural_item_axis()
        assert tuple(Vector(member.Axis.DirectionRatios)) == pytest.approx((0.0, -1.0, 0.0), abs=1e-6)


class TestAddCurveItem(NewFile):
    def test_adding_a_curve_member_in_ifc2x3_which_has_no_axis(self):
        tool.Project.get_project_props().export_schema = "IFC2X3"
        bpy.ops.bim.create_project()
        props = tool.Root.get_root_props()
        props.ifc_product, props.ifc_class, props.representation_template = (
            "IfcStructuralItem",
            "IfcStructuralCurveMember",
            "EDGE",
        )
        bpy.ops.bim.add_element(skip_dialog=True)
        assert tool.Ifc.get().by_type("IfcStructuralCurveMember")


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


class TestLoadCaseSelfWeight(NewFile):
    def test_edit_and_clear_self_weight(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        load_case = ifc.createIfcStructuralLoadCase(
            GlobalId=ifcopenshell.guid.new(),
            Name="Dead Load",
            PredefinedType="LOAD_CASE",
            ActionType="PERMANENT_G",
            ActionSource="DEAD_LOAD_G",
        )
        props = tool.Structural.get_structural_props()

        bpy.ops.bim.enable_editing_structural_load_case(load_case=load_case.id())
        assert props.load_case_has_self_weight is False
        assert tuple(props.load_case_self_weight) == (0.0, 0.0, -1.0)

        props.load_case_has_self_weight = True
        props.load_case_self_weight = (0.5, 0.0, -1.0)
        bpy.ops.bim.edit_structural_load_case()
        assert list(load_case.SelfWeightCoefficients) == [0.5, 0.0, -1.0]

        bpy.ops.bim.enable_editing_structural_load_case(load_case=load_case.id())
        assert props.load_case_has_self_weight is True
        assert tuple(props.load_case_self_weight) == (0.5, 0.0, -1.0)

        props.load_case_has_self_weight = False
        bpy.ops.bim.edit_structural_load_case()
        assert load_case.SelfWeightCoefficients is None


class TestGetLoadUnitSymbol(NewFile):
    def make_file(self) -> ifcopenshell.file:
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)  # millimetres
        return ifc

    def test_composing_force_over_length_when_no_load_units_are_declared(self):
        self.make_file()
        assert get_load_unit_symbol("IfcStructuralPointConnection") == "N"
        assert get_load_unit_symbol("IfcStructuralCurveMember") == "N/mm"
        assert get_load_unit_symbol("IfcStructuralSurfaceMember") == "N/mm2"

    def test_using_the_declared_load_units(self):
        ifc = self.make_file()
        bpy.context.scene.unit_settings.system = "METRIC"
        ifcopenshell.api.unit.assign_unit(ifc, units=tool.Unit.add_structural_units())
        assert get_load_unit_symbol("IfcStructuralPointConnection") == "kN"
        assert get_load_unit_symbol("IfcStructuralCurveMember") == "kN/m"
        assert get_load_unit_symbol("IfcStructuralSurfaceMember") == "kN/m2"


class TestApplyStructuralLoadAxes(NewFile):
    def make_item(self, ifc_class, z_down=False):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        if z_down:
            # As RFEM places its models: Z down.
            model.SharedPlacement = ifc.createIfcLocalPlacement(
                None,
                ifc.createIfcAxis2Placement3D(
                    ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                    ifc.createIfcDirection((0.0, 0.0, -1.0)),
                    ifc.createIfcDirection((1.0, 0.0, 0.0)),
                ),
            )
        item = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[item], structural_analysis_model=model
        )
        obj = bpy.data.objects.new("Item", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(item, obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        return ifc, item

    def get_activity(self, item):
        return ifcopenshell.util.structural.get_item_activities(item)[0]

    def test_a_force_normal_to_a_surface(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember")
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", z=-2.0)
        activity = self.get_activity(surface)
        assert activity.GlobalOrLocal == "LOCAL_COORDS"
        assert activity.AppliedLoad.PlanarForceZ == -2.0
        assert activity.AppliedLoad.Name.endswith(" local")

    def test_global_by_default(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember")
        bpy.ops.bim.apply_structural_load(load_group="0", z=-2.0)
        assert self.get_activity(surface).GlobalOrLocal == "GLOBAL_COORDS"

    def test_local_values_are_not_turned_into_the_model_axes(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember", z_down=True)
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", z=-2.0)
        assert self.get_activity(surface).AppliedLoad.PlanarForceZ == -2.0

    def test_global_values_are_turned_into_the_model_axes(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember", z_down=True)
        bpy.ops.bim.apply_structural_load(load_group="0", axes="GLOBAL_COORDS", z=-2.0)
        assert self.get_activity(surface).AppliedLoad.PlanarForceZ == 2.0

    def test_a_point_connection_takes_global_axes(self):
        ifc, point = self.make_item("IfcStructuralPointConnection")
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", z=-2.0)
        activity = self.get_activity(point)
        assert activity.GlobalOrLocal == "GLOBAL_COORDS"
        assert not activity.AppliedLoad.Name.endswith(" local")

    def test_editing_a_load_changes_its_axes(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember")
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", z=-2.0)
        activity = self.get_activity(surface)
        case = str(ifcopenshell.util.structural.get_activity_load_cases(activity)[0].id())
        bpy.ops.bim.edit_structural_load_values(
            activity=activity.id(), load_group=case, initial_load_group=case, axes="GLOBAL_COORDS", z=-3.0
        )
        assert activity.GlobalOrLocal == "GLOBAL_COORDS"
        assert activity.AppliedLoad.PlanarForceZ == -3.0
        assert not activity.AppliedLoad.Name.endswith(" local")


class TestApplyingAChosenLoad(NewFile):
    def setup_points(self):
        """D carries a single force in a load case; B and C carry nothing; a curve member M can't take a single force."""
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        case = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Case")
        load = ifcopenshell.api.structural.add_structural_load(
            ifc, name="1300 lbf", ifc_class="IfcStructuralLoadSingleForce"
        )
        objects = {}
        for name, ifc_class in (
            ("B", "IfcStructuralPointConnection"),
            ("C", "IfcStructuralPointConnection"),
            ("D", "IfcStructuralPointConnection"),
            ("M", "IfcStructuralCurveMember"),
        ):
            element = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class, name=name)
            obj = bpy.data.objects.new(name, None)
            bpy.context.scene.collection.objects.link(obj)
            tool.Ifc.link(element, obj)
            objects[name] = obj
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc,
            applied_load=load,
            structural_member=tool.Ifc.get_entity(objects["D"]),
            ifc_class="IfcStructuralPointAction",
        )
        ifcopenshell.api.group.assign_group(ifc, products=[activity], group=case)
        return ifc, case, load, objects

    def select(self, objects, names, active):
        for obj in bpy.context.scene.objects:
            obj.select_set(obj.name in names)
        bpy.context.view_layer.objects.active = objects[active]

    def test_targets_are_items_that_can_take_the_load_and_lack_it(self):
        ifc, case, load, objects = self.setup_points()
        targets = tool.Structural.get_load_targets(list(objects.values()), load, case)
        assert sorted(t.Name for t in targets) == ["B", "C"]  # Not D, which has it; not M, a curve member.

    def test_applying_skips_an_item_that_has_the_load_already(self):
        ifc, case, load, objects = self.setup_points()
        props = tool.Structural.get_structural_props()
        self.select(objects, {"B", "D"}, "D")
        props.applicable_structural_load_types = "IfcStructuralLoadSingleForce"
        props.applicable_structural_loads = str(load.id())
        bpy.ops.bim.add_structural_activity(load_group=case.id())
        users = [i for i in ifc.get_inverse(load) if i.is_a("IfcStructuralActivity")]
        assert sorted(u.AssignedToStructuralItem[0].RelatingElement.Name for u in users) == ["B", "D"]

    def test_the_picker_follows_the_active_items_load(self):
        ifc, case, load, objects = self.setup_points()
        other = ifcopenshell.api.structural.add_structural_load(
            ifc, name="Other", ifc_class="IfcStructuralLoadSingleForce"
        )
        props = tool.Structural.get_structural_props()
        props.active_load_case_id = case.id()
        self.select(objects, {"D"}, "D")
        props.applicable_structural_load_types = "IfcStructuralLoadSingleForce"
        props.applicable_structural_loads = str(other.id())
        tool.Structural.follow_active_item_load()
        assert props.applicable_structural_loads == str(load.id())
        # An item with no load here leaves the picker alone.
        self.select(objects, {"B"}, "B")
        props.applicable_structural_loads = str(other.id())
        tool.Structural.follow_active_item_load()
        assert props.applicable_structural_loads == str(other.id())
