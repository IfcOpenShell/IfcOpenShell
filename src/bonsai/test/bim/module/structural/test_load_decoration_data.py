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

import math
from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock

import blf
import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import numpy as np
from mathutils import Matrix, Vector

import bonsai.bim.module.structural.decorator as decorator_module
import bonsai.tool as tool
from bonsai.bim.module.structural.decorator import LoadsDecorator
from bonsai.bim.module.structural.load_decoration_data import ScreenGrid, ShaderInfo, box_crosses_segments
from test.bim.bootstrap import NewFile, NewIfc


class TestLinearLoadsForMemberWithoutMesh(NewFile):
    def _shader_info(self, ifc):
        member = ifc.createIfcStructuralCurveMember(
            GlobalId=ifcopenshell.guid.new(), PredefinedType="RIGID_JOINED_MEMBER"
        )
        action = ifc.createIfcStructuralLinearAction(GlobalId=ifcopenshell.guid.new(), PredefinedType="CONST")
        info = ShaderInfo()
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        return info, member

    def test_member_without_object(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, _ = self._shader_info(ifc)
        info.get_linear_loads()
        assert info.info == []

    def test_member_with_empty_mesh(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, member = self._shader_info(ifc)
        tool.Ifc.link(member, bpy.data.objects.new("Member", bpy.data.meshes.new("Member")))
        info.get_linear_loads()
        assert info.info == []


class TestArrowThickness(NewFile):
    def get_spacing(self) -> float:
        info = ShaderInfo()
        info.shader = SimpleNamespace(new=lambda name: None)  # Headless, there is no GPU to make shaders with.
        info.add_force_arrow(np.zeros(3), np.array((0.0, 0.0, 1.0)), (1, 0, 0, 1), "1 kN", 1.0)
        return dict(info.info[-1]["uniforms"])["spacing"]

    def test_scaling_the_shaft_and_head_together(self):
        tool.Ifc.set(ifcopenshell.file())
        default = self.get_spacing()
        tool.Structural.get_structural_props().arrow_thickness = 2.0
        assert math.isclose(self.get_spacing(), 2 * default)


class TestBoxCrossesSegments:
    # A label's box from (0, 0), 10 wide and 5 high.
    def test_lines_crossing_or_inside(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 2), (15, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((2, 1), (3, 2))])
        assert box_crosses_segments(0, 0, 10, 5, [((-1, 4), (1, 6))])  # Across a corner.

    def test_lines_clear_of_it(self):
        assert not box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8))])
        assert not box_crosses_segments(0, 0, 10, 5, [((12, 0), (20, 10))])
        assert not box_crosses_segments(0, 0, 10, 5, [])

    def test_any_of_several(self):
        assert box_crosses_segments(0, 0, 10, 5, [((-5, 8), (15, 8)), ((5, -5), (5, 10))])


class TestScreenGrid:
    def test_boxes_in_other_cells_or_beyond_the_margin_are_clear(self):
        grid = ScreenGrid(cell=10)
        grid.add_box(0, 0, 25, 5)  # Across three cells.
        assert grid.overlaps_box(20, 2, 4, 4)
        assert not grid.overlaps_box(30, 0, 4, 4)
        assert grid.overlaps_box(27, 0, 4, 4, margin=3)

    def test_a_line_through_cells_it_does_not_end_in(self):
        grid = ScreenGrid(cell=10)
        grid.add_segment((-50, 15), (50, 15))
        assert grid.crosses_segment(0, 10, 5, 10)
        assert not grid.crosses_segment(0, 20, 5, 5)


class TestPlaceLabelsBeside:
    def place(self, loads: list[tuple[float, float]], length: float = 30.0) -> tuple[list, list]:
        """Label downward arrows ending at the points given on screen, at their tips, as point loads are"""
        arrows = [((x, y + length), (x, y)) for x, y in loads]
        placed = ScreenGrid()
        for arrow in arrows:
            placed.add_segment(*arrow)
        context = SimpleNamespace(region=None, region_data=None)
        decorator = LoadsDecorator.__new__(LoadsDecorator)
        boxes = []
        # On screen as in the X-Z plane, so that a position (x, 0, y) is drawn at (x, y).
        with mock.patch.object(decorator_module, "location_3d_to_region_2d", lambda r, v, p: Vector((p[0], p[2]))):
            for x, y in loads:
                bx, by = decorator.place_beside((x, 0, y), (0, 0, -1), x, y, "12.5 kN", context, placed)
                boxes.append((bx, by, *blf.dimensions(0, "12.5 kN")))
        return arrows, boxes

    def test_labels_keep_off_the_arrows_beside_them(self):
        # Rows of loads closer than a label is wide, as along a beam, whose labels would fall on the next row's arrows.
        arrows, boxes = self.place([(40.0 * i, 35.0 * j) for i in range(8) for j in range(4)])
        assert not any(box_crosses_segments(*box, arrows) for box in boxes)

    def test_labels_keep_off_each_other(self):
        _, boxes = self.place([(10.0 * i, 0.0) for i in range(6)])
        for i, (x1, y1, w1, h1) in enumerate(boxes):
            for x2, y2, w2, h2 in boxes[i + 1 :]:
                assert not (x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1)


class TestTemperatureLoads(NewFile):
    def test_curve_member_temperature_load(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        member = ifc.createIfcStructuralCurveMember(
            GlobalId=ifcopenshell.guid.new(), PredefinedType="RIGID_JOINED_MEMBER"
        )
        load = ifc.createIfcStructuralLoadTemperature(DeltaTConstant=25.0, DeltaTY=-5.0, DeltaTZ=0.0)
        action = ifc.createIfcStructuralLinearAction(
            GlobalId=ifcopenshell.guid.new(), AppliedLoad=load, PredefinedType="CONST"
        )
        mesh = bpy.data.meshes.new("Member")
        mesh.from_pydata([(0.0, 0.0, 0.0), (4.0, 0.0, 0.0)], [(0, 1)], [])
        obj = bpy.data.objects.new("Member", mesh)
        tool.Ifc.link(member, obj)

        info = ShaderInfo()
        info.shader.new = lambda pattern: None
        info.temperature_unit = "K"
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        info.get_temperature_loads()

        assert len(info.info) == 1
        assert len(info.text_info) == 1
        assert "ΔT=+25.00 K" in info.text_info[0]["text"]
        assert "ΔTy=-5.00 K" in info.text_info[0]["text"]

    def test_member_without_mesh_skips_cleanly(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        member = ifcopenshell.create_entity("IfcStructuralCurveMember", GlobalId=ifcopenshell.guid.new())
        load = ifc.createIfcStructuralLoadTemperature(DeltaTConstant=10.0)
        action = ifc.createIfcStructuralLinearAction(GlobalId=ifcopenshell.guid.new(), AppliedLoad=load)
        info = ShaderInfo()
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        info.get_temperature_loads()
        assert info.info == []
        assert info.text_info == []


class TestLoadsInATurnedModel(NewFile):
    """Global loads are given in their analysis model's axes, which RFEM points Z down, and drawn in Blender's"""

    def make_activity(self, item_class, activity_class, load_class, attributes, global_or_local="GLOBAL_COORDS"):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        model.SharedPlacement = ifc.createIfcLocalPlacement(
            None,
            ifc.createIfcAxis2Placement3D(
                ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                ifc.createIfcDirection((0.0, 0.0, -1.0)),
                ifc.createIfcDirection((1.0, 0.0, 0.0)),
            ),
        )
        item = ifcopenshell.api.root.create_entity(ifc, ifc_class=item_class)
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[item], structural_analysis_model=model
        )
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class=load_class)
        ifcopenshell.api.structural.edit_structural_load(ifc, structural_load=load, attributes=attributes)
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, ifc_class=activity_class, applied_load=load, structural_member=item, global_or_local=global_or_local
        )
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        return activity

    def test_a_line_load_down_in_the_model_is_drawn_down(self):
        activity = self.make_activity(
            "IfcStructuralCurveMember",
            "IfcStructuralLinearAction",
            "IfcStructuralLoadLinearForce",
            {"LinearForceZ": 5.0, "LinearMomentY": 1.0},
        )
        values = ShaderInfo().parse_linear_loads_to_dict([(activity, 1.0)], np.eye(3))["constant force"]
        assert np.allclose(values, (0.0, 0.0, -5.0, 0.0, -1.0, 0.0))

    def test_an_area_load_down_in_the_model_is_drawn_down(self):
        activity = self.make_activity(
            "IfcStructuralSurfaceMember",
            "IfcStructuralPlanarAction",
            "IfcStructuralLoadPlanarForce",
            {"PlanarForceZ": 5.0},
        )
        assert np.allclose(ShaderInfo().get_planar_loads_values([(activity, 1.0)], np.eye(3)), (0.0, 0.0, -5.0))

    def test_a_point_load_is_turned_once(self):
        activity = self.make_activity(
            "IfcStructuralPointConnection",
            "IfcStructuralPointAction",
            "IfcStructuralLoadSingleForce",
            {"ForceZ": 5.0},
        )
        values = ShaderInfo().get_point_loads_values([(activity, 1.0)], np.eye(3))
        assert np.allclose(values[:3], (0.0, 0.0, -5.0))

    def test_a_local_load_is_not_turned_into_the_model_axes(self):
        activity = self.make_activity(
            "IfcStructuralSurfaceMember",
            "IfcStructuralPlanarAction",
            "IfcStructuralLoadPlanarForce",
            {"PlanarForceZ": 5.0},
            global_or_local="LOCAL_COORDS",
        )
        tool.Structural.get_structural_props().reference_frame = "LOCAL_COORDS"
        assert np.allclose(ShaderInfo().get_planar_loads_values([(activity, 1.0)], np.eye(3)), (0.0, 0.0, 5.0))


class TestLocalAxesTurnWithTheItem(NewFile):
    """An item's topology, Axis and face plane are in its own coordinates: its local axes turn with its object"""

    def make_item(self, ifc_class, item=None, rotation=None):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
        if item:
            element.Representation = ifc.createIfcProductDefinitionShape(
                Representations=[ifc.createIfcTopologyRepresentation(context, "Reference", "Edge", [item(ifc)])]
            )
        obj = bpy.data.objects.new("Item", None)
        bpy.context.scene.collection.objects.link(obj)
        if rotation:
            obj.matrix_world = Matrix.Rotation(math.radians(rotation[0]), 4, rotation[1])
        tool.Ifc.link(element, obj)
        return ifc, element

    def edge(self, ifc):
        start, end = (
            ifc.createIfcVertexPoint(ifc.createIfcCartesianPoint(p)) for p in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
        )
        return ifc.createIfcEdge(start, end)

    def face(self, ifc):
        plane = ifc.createIfcPlane(ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))))
        return ifc.createIfcFaceSurface(Bounds=[], FaceSurface=plane, SameSense=True)

    def test_a_curve_member(self):
        ifc, member = self.make_item("IfcStructuralCurveMember", self.edge, (90, "Z"))
        member.Axis = ifc.createIfcDirection((0.0, 0.0, 1.0))
        rotation = ShaderInfo().get_curve_member_rotation(member)
        assert np.allclose(rotation, ((0, -1, 0), (1, 0, 0), (0, 0, 1)), atol=1e-5)

    def test_a_surface_member(self):
        ifc, surface = self.make_item("IfcStructuralSurfaceMember", self.face, (90, "X"))
        rotation = ShaderInfo().get_surface_member_rotation(surface)
        assert np.allclose(rotation[:, 2], (0, -1, 0), atol=1e-5)

    def test_a_point_connection(self):
        ifc, point = self.make_item("IfcStructuralPointConnection", rotation=(90, "Z"))
        rotation = ShaderInfo().get_point_connection_rotation(point)
        assert np.allclose(rotation[:, 0], (0, 1, 0), atol=1e-5)

    def test_a_local_line_load_is_drawn_in_the_turned_axes(self):
        ifc, member = self.make_item("IfcStructuralCurveMember", self.edge, (90, "Z"))
        member.Axis = ifc.createIfcDirection((0.0, 0.0, 1.0))
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class="IfcStructuralLoadLinearForce")
        ifcopenshell.api.structural.edit_structural_load(ifc, structural_load=load, attributes={"LinearForceX": 5.0})
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc,
            ifc_class="IfcStructuralLinearAction",
            applied_load=load,
            structural_member=member,
            global_or_local="LOCAL_COORDS",
        )
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        info = ShaderInfo()
        rotation = info.get_curve_member_rotation(member)
        values = info.parse_linear_loads_to_dict([(activity, 1.0)], rotation)["constant force"]
        assert np.allclose(values[:3], (0.0, 5.0, 0.0), atol=1e-5)


class TestLoadsPerProjectedLength(NewFile):
    """Snow on a rafter is given per horizontal length: per length of the member projected across the load"""

    def make_load(self, projected_or_true="PROJECTED_LENGTH", global_or_local="GLOBAL_COORDS"):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        context = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        member = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralCurveMember")
        # A rafter at 60 degrees to the horizontal: its horizontal projection is half its length.
        start, end = (
            ifc.createIfcVertexPoint(ifc.createIfcCartesianPoint(p))
            for p in ((0.0, 0.0, 0.0), (1.0, 0.0, math.sqrt(3.0)))
        )
        member.Representation = ifc.createIfcProductDefinitionShape(
            Representations=[
                ifc.createIfcTopologyRepresentation(context, "Reference", "Edge", [ifc.createIfcEdge(start, end)])
            ]
        )
        member.Axis = ifc.createIfcDirection((0.0, 1.0, 0.0))
        obj = bpy.data.objects.new("Member", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(member, obj)
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class="IfcStructuralLoadLinearForce")
        ifcopenshell.api.structural.edit_structural_load(ifc, structural_load=load, attributes={"LinearForceZ": -2.0})
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc,
            ifc_class="IfcStructuralLinearAction",
            applied_load=load,
            structural_member=member,
            global_or_local=global_or_local,
        )
        activity.ProjectedOrTrue = projected_or_true
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        info = ShaderInfo()
        return info, activity, info.get_curve_member_rotation(member)

    def test_it_is_added_to_others_per_true_length(self):
        info, activity, rotation = self.make_load()
        values = info.parse_linear_loads_to_dict([(activity, 1.0)], rotation)["constant force"]
        assert np.allclose(values[:3], (0.0, 0.0, -1.0))

    def test_it_is_drawn_on_its_own_as_given(self):
        info, activity, rotation = self.make_load()
        values = info.parse_linear_loads_to_dict([(activity, 1.0)], rotation, per_true_length=False)
        assert np.allclose(values["constant force"][:3], (0.0, 0.0, -2.0))

    def test_a_load_per_true_length_is_as_given(self):
        info, activity, rotation = self.make_load(projected_or_true="TRUE_LENGTH")
        values = info.parse_linear_loads_to_dict([(activity, 1.0)], rotation)["constant force"]
        assert np.allclose(values[:3], (0.0, 0.0, -2.0))


class TestAreaLoadsPerProjectedArea(NewFile):
    """Snow on a pitched roof is given per plan area: per area of the member projected across the load"""

    def make_load(self, projected_or_true="PROJECTED_LENGTH"):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        member = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralSurfaceMember")
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class="IfcStructuralLoadPlanarForce")
        ifcopenshell.api.structural.edit_structural_load(ifc, structural_load=load, attributes={"PlanarForceZ": -2.0})
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, ifc_class="IfcStructuralPlanarAction", applied_load=load, structural_member=member
        )
        activity.ProjectedOrTrue = projected_or_true
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        # A roof pitched at 60 degrees: its plan area is half its area. Its normal is the third column.
        s, c = math.sin(math.radians(60)), math.cos(math.radians(60))
        rotation = np.array(((c, 0.0, -s), (0.0, 1.0, 0.0), (s, 0.0, c)))
        return ShaderInfo(), activity, rotation

    def test_it_is_added_to_others_per_true_area(self):
        info, activity, rotation = self.make_load()
        assert np.allclose(info.get_planar_loads_values([(activity, 1.0)], rotation), (0.0, 0.0, -1.0))

    def test_it_is_drawn_as_given(self):
        info, activity, rotation = self.make_load()
        values = info.get_planar_loads_values([(activity, 1.0)], rotation, per_true_area=False)
        assert np.allclose(values, (0.0, 0.0, -2.0))

    def test_a_load_per_true_area_is_as_given(self):
        info, activity, rotation = self.make_load(projected_or_true="TRUE_LENGTH")
        assert np.allclose(info.get_planar_loads_values([(activity, 1.0)], rotation), (0.0, 0.0, -2.0))


class TestLineForcesAlongTheirResultant(NewIfc):
    """A line load's force components are drawn as one load along their resultant, as an area load is"""

    def load(self, constant=0.0, polyline=()):
        return {"constant": constant, "quadratic": 0.0, "sinus": 0.0, "polyline": [list(p) for p in polyline]}

    def test_a_uniform_load(self):
        loads = {"fx": self.load(3.0), "fy": self.load(), "fz": self.load(4.0)}
        direction, resultant, largest = ShaderInfo().resolve_linear_forces(loads)
        assert np.allclose(direction, (0.6, 0.0, 0.8))
        assert resultant["constant"] == 5.0 and largest == 5.0

    def test_a_load_turning_along_the_member_stays_in_components(self):
        loads = {
            "fx": self.load(polyline=((0.0, 1.0), (1.0, 0.0))),
            "fy": self.load(),
            "fz": self.load(polyline=((0.0, 0.0), (1.0, 1.0))),
        }
        assert ShaderInfo().resolve_linear_forces(loads) is None

    def make_member(self):
        props = tool.Structural.get_structural_props()
        props.structural_item_class = "IfcStructuralCurveMember"
        bpy.ops.bim.add_structural_item()
        obj = bpy.context.active_object
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        return tool.Ifc.get_entity(obj)

    def get_force_diagrams(self):
        info = ShaderInfo()
        info.shader = MagicMock()
        info.shader.new.side_effect = lambda pattern: pattern
        info.curve_members = {}
        info.get_structural_elements_and_activities()
        info.get_linear_loads()
        return [i["uniforms"][0][1] for i in info.info if i["shader"] != "DISTRIBUTED MOMENT"]

    def test_a_local_load_on_a_tilted_member_is_drawn_once(self):
        member = self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", y=-5.0)
        ifcopenshell.api.structural.edit_structural_item_axis(tool.Ifc.get(), structural_item=member, axis=(0, -1, 1))
        props = tool.Structural.get_structural_props()
        props.reference_frame = "GLOBAL_COORDS"
        assert self.get_force_diagrams() == [(1, 1, 1, 1)]
        props.force_display = "COMPONENTS"
        assert self.get_force_diagrams() == [(0, 1, 0, 1), (0, 0, 1, 1)]

    def test_each_applied_load_is_drawn_on_its_own(self):
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", y=-5.0)
        (case,) = tool.Ifc.get().by_type("IfcStructuralLoadCase")
        bpy.ops.bim.apply_structural_load(load_group=str(case.id()), axes="GLOBAL_COORDS", y=-3.0, z=-4.0)
        props = tool.Structural.get_structural_props()
        props.reference_frame = "GLOBAL_COORDS"
        assert self.get_force_diagrams() == [(1, 1, 1, 1), (1, 1, 1, 1)]
        props.force_display = "COMPONENTS"
        assert self.get_force_diagrams() == [(0, 1, 0, 1), (0, 0, 1, 1)]

    def get_scale(self):
        info = ShaderInfo()
        info.shader = MagicMock()
        info.get_structural_elements_and_activities()
        info.get_linear_loads()
        return {u[1] for i in info.info for u in i["uniforms"] if u[0] == "maxload"}

    def test_a_load_keeps_its_length_as_another_turns(self):
        member = self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", axes="LOCAL_COORDS", y=-5.0)
        (case,) = tool.Ifc.get().by_type("IfcStructuralLoadCase")
        bpy.ops.bim.apply_structural_load(load_group=str(case.id()), axes="GLOBAL_COORDS", z=-4.0)
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        assert self.get_scale() == {5.0}
        # Local Y now points down, along the global load: their sum would be 9.
        ifcopenshell.api.structural.edit_structural_item_axis(tool.Ifc.get(), structural_item=member, axis=(0, -1, 0))
        assert self.get_scale() == {5.0}

    def get_labels(self):
        info = ShaderInfo()
        info.shader = MagicMock()
        info.get_structural_elements_and_activities()
        info.get_linear_loads()
        return {t["text"] for t in info.text_info}

    def test_a_load_per_projected_length_is_labelled_so(self):
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", projected=True, z=-2.0)
        props = tool.Structural.get_structural_props()
        props.reference_frame = "GLOBAL_COORDS"
        labels = self.get_labels()
        assert labels and all(label.endswith(" projected") for label in labels)
        props.force_display = "COMPONENTS"
        # Added to others, it is per true length, and not labelled.
        assert not any(label.endswith(" projected") for label in self.get_labels())

    def test_loads_on_different_members_share_a_scale(self):
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", z=-4.0)
        (case,) = tool.Ifc.get().by_type("IfcStructuralLoadCase")
        bpy.context.scene.cursor.location = (0.0, 5.0, 0.0)
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group=str(case.id()), z=-10.0)
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        assert len(self.get_force_diagrams()) == 2
        assert self.get_scale() == {10.0}

    def test_each_component_has_its_own_points(self):
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", y=-3.0, z=-4.0)
        member_length = 1.0
        info = ShaderInfo()
        info.get_structural_elements_and_activities()
        (value,) = info.curve_members.values()
        loads = info.process_total_linear_loads(value["activities"], np.eye(3), member_length)["linear loads"]
        assert len(loads["fy"]["polyline"]) == len(loads["fz"]["polyline"]) == 2


class TestPointMoments(NewFile):
    def test_a_negligible_moment_is_not_drawn(self):
        # RFEM writes leftovers such as 1.9e-308 where a component is unset, too small to give a direction.
        info = ShaderInfo()
        info.shader = MagicMock()  # No GPU in background mode.
        with np.errstate(divide="raise", invalid="raise"):
            info.get_point_moment_args((1.94069306614094e-308, 0.0, 5.0), (0.0, 0.0, 0.0), np.eye(3))
        assert [i["uniforms"][0][1] for i in info.info] == [(0, 0, 1, 1)]
