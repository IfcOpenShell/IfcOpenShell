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
from unittest.mock import MagicMock

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import numpy as np
from mathutils import Matrix

import bonsai.tool as tool
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo
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

    def test_each_component_has_its_own_points(self):
        self.make_member()
        bpy.ops.bim.apply_structural_load(load_group="0", y=-3.0, z=-4.0)
        member_length = 1.0
        info = ShaderInfo()
        info.get_structural_elements_and_activities()
        (value,) = info.curve_members.values()
        loads = info.process_total_linear_loads(value["activities"], np.eye(3), member_length)["linear loads"]
        assert len(loads["fy"]["polyline"]) == len(loads["fz"]["polyline"]) == 2
