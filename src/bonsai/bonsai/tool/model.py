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
#
# This file was modified with the assistance of an AI coding tool.

from __future__ import annotations

import collections.abc
import json
from collections.abc import Callable, Iterable, Sequence
from copy import deepcopy
from math import atan, cos, degrees, pi, radians
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
    Union,
    assert_never,
)

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.grid
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import mathutils
import numpy as np
import shapely
from ifcopenshell.util.shape_builder import ShapeBuilder, np_to_3d
from mathutils import Matrix, Vector

import bonsai.core.geometry
import bonsai.core.model
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim import import_ifc
from bonsai.tool.cad import VTX_PRECISION, WELD_TOLERANCE

T = TypeVar("T")
V_ = tool.Blender.V_

if TYPE_CHECKING:
    import ifcsverchok.nodes.ifc.shape_builder.shape_output
    import sverchok.node_tree
    from sverchok.core.node_group import SvGroupTreeNode

    from bonsai.bim.module.model.prop import (
        BIMArrayProperties,
        BIMDoorProperties,
        BIMDuctSegmentProperties,
        BIMExternalParametricGeometryProperties,
        BIMModelProperties,
        BIMPipeSegmentProperties,
        BIMPolylineProperties,
        BIMRailingProperties,
        BIMRoofProperties,
        BIMSlabProperties,
        BIMStairProperties,
        BIMSverchokProperties,
        BIMWallProperties,
        BIMWindowProperties,
    )


class Model(bonsai.core.tool.Model):
    @classmethod
    def get_model_props(cls) -> BIMModelProperties:
        return bpy.context.scene.BIMModelProperties

    @classmethod
    def get_door_props(cls, obj: bpy.types.Object) -> BIMDoorProperties:
        return obj.BIMDoorProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_window_props(cls, obj: bpy.types.Object) -> BIMWindowProperties:
        return obj.BIMWindowProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_stair_props(cls, obj: bpy.types.Object) -> BIMStairProperties:
        return obj.BIMStairProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_wall_props(cls, obj: bpy.types.Object) -> BIMWallProperties:
        return obj.BIMWallProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_roof_props(cls, obj: bpy.types.Object) -> BIMRoofProperties:
        return obj.BIMRoofProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_railing_props(cls, obj: bpy.types.Object) -> BIMRailingProperties:
        return obj.BIMRailingProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_slab_props(cls, obj: bpy.types.Object) -> BIMSlabProperties:
        return obj.BIMSlabProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_pipe_segment_props(cls, obj: bpy.types.Object) -> BIMPipeSegmentProperties:
        return obj.BIMPipeSegmentProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_duct_segment_props(cls, obj: bpy.types.Object) -> BIMDuctSegmentProperties:
        return obj.BIMDuctSegmentProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_sverchok_props(cls, obj: bpy.types.Object) -> BIMSverchokProperties:
        return obj.BIMSverchokProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_array_props(cls, obj: bpy.types.Object) -> BIMArrayProperties:
        return obj.BIMArrayProperties

    @classmethod
    def get_epg_props(cls, obj: bpy.types.Object) -> BIMExternalParametricGeometryProperties:
        return obj.BIMExternalParametricGeometryProperties

    @classmethod
    def get_polyline_props(cls) -> BIMPolylineProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMPolylineProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def resolve_active_props_for_edit(
        cls,
        context: bpy.types.Context,
        props_getter: Callable[[bpy.types.Object], Any],
        *,
        subtype: Optional[tuple[str, Any]] = None,
    ) -> Optional[tuple[bpy.types.Object, Any]]:
        """Resolve ``(obj, props)`` for an operator that acts on the active
        object only while a parametric edit is active.

        Returns ``None`` (the operator should ``return {"CANCELLED"}``) when
        any of these fail:
        - no active object,
        - ``props.is_editing`` is False,
        - ``subtype`` is given as ``(attr, value)`` and ``props.<attr> != value``.
        """
        obj = context.active_object
        if not obj:
            return None
        props = props_getter(obj)
        if not getattr(props, "is_editing", False):
            return None
        if subtype is not None:
            attr, value = subtype
            if getattr(props, attr, None) != value:
                return None
        return obj, props

    @classmethod
    def convert_si_to_unit(cls, value: T) -> T:
        if isinstance(value, (tuple, list)):
            return [v / cls.unit_scale for v in value]
        return value / cls.unit_scale

    @classmethod
    def convert_unit_to_si(cls, value: T) -> T:
        if isinstance(value, (tuple, list)):
            return [v * cls.unit_scale for v in value]
        return value * cls.unit_scale

    @classmethod
    def convert_data_to_project_units(cls, data: dict[str, Any], non_si_props: Sequence[str] = ()) -> dict[str, Any]:
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for prop_name in data:
            if prop_name in non_si_props:
                continue
            prop_value = data[prop_name]
            if isinstance(prop_value, collections.abc.Iterable):
                data[prop_name] = [v / si_conversion for v in prop_value]
            else:
                data[prop_name] = prop_value / si_conversion
        return data

    @classmethod
    def convert_data_to_si_units(cls, data: dict[str, Any], non_si_props: Sequence[str] = ()) -> dict[str, Any]:
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for prop_name in data:
            if prop_name in non_si_props:
                continue
            # `None` is used by `custom_first_last_tread_run`.
            prop_value: Iterable[float | None] | float = data[prop_name]
            if isinstance(prop_value, collections.abc.Iterable):
                data[prop_name] = [v if v is None else v * si_conversion for v in prop_value]
            else:
                data[prop_name] = prop_value * si_conversion
        return data

    @classmethod
    def get_constituents_props_data(cls, element: ifcopenshell.entity_instance) -> dict[str, str]:
        constituents = ("lining", "framing", "glazing")
        props: dict[str, str] = {f"{constituent}_material": "0" for constituent in constituents}
        material = ifcopenshell.util.element.get_material(element)
        if not material or not material.is_a("IfcMaterialConstituentSet"):
            return props
        for constituent in material.MaterialConstituents:
            name = (constituent.Name or "").lower()
            if name in constituents:
                props[f"{name}_material"] = str(constituent.Material.id())
        return props

    @classmethod
    def convert_mesh_to_curve(
        cls, position: Matrix, edge_indices: list[tuple[int, int]]
    ) -> ifcopenshell.entity_instance:
        position_i = position.inverted()
        ifc_file = tool.Ifc.get()
        if len(edge_indices) == 2:
            diameter = edge_indices[0]
            p1 = cls.bm.verts[diameter[0]].co
            p2 = cls.bm.verts[diameter[1]].co
            center = cls.convert_si_to_unit(list(position_i @ p1.lerp(p2, 0.5)))
            radius = cls.convert_si_to_unit((p1 - p2).length / 2)
            return ifc_file.createIfcCircle(
                ifc_file.createIfcAxis2Placement2D(ifc_file.createIfcCartesianPoint(center[0:2])), radius
            )
        if ifc_file.schema == "IFC2X3":
            points = []
            for edge in edge_indices:
                local_point = (position_i @ Vector(cls.bm.verts[edge[0]].co)).to_2d()
                points.append(ifc_file.createIfcCartesianPoint(cls.convert_si_to_unit(local_point)))
            points.append(points[0])
            return ifc_file.createIfcPolyline(points)
        segments = []
        for segment in edge_indices:
            if len(segment) == 2:
                segments.append(ifc_file.createIfcLineIndex([i + 1 for i in segment]))
            elif len(segment) == 3:
                segments.append(ifc_file.createIfcArcIndex([i + 1 for i in segment]))
        return ifc_file.createIfcIndexedPolyCurve(cls.points, segments, False)

    @classmethod
    def export_points(cls, position: Matrix, indices: list[Vector]) -> ifcopenshell.entity_instance:
        position_i = position.inverted()
        points = []
        for point in indices:
            local_point = (position_i @ point).to_2d()
            points.append(cls.convert_si_to_unit(list(local_point)))
        return tool.Ifc.get().createIfcCartesianPointList2D(points)

    @classmethod
    def export_annotation_fill_area(cls, obj: bpy.types.Object) -> ifcopenshell.entity_instance | None:
        result = cls.auto_detect_annotation_fill_area(obj, obj.data)
        if isinstance(result, dict) and result["annotation_fill_area"]:
            return tool.Ifc.get().add(result["annotation_fill_area"])

    @classmethod
    def export_profile(
        cls, obj: bpy.types.Object, position: Optional[Matrix] = None, x_angle: Optional[float] = None
    ) -> ifcopenshell.entity_instance | None:
        """Returns `None` in case if profile was invalid."""
        if position is None:
            position = Matrix()

        result = cls.auto_detect_profiles(obj, obj.data, position, x_angle)
        if isinstance(result, dict) and result["profile_def"]:
            return tool.Ifc.get().add(result["profile_def"])

    @classmethod
    def export_curves(
        cls, obj: bpy.types.Object, position: Optional[Matrix] = None
    ) -> list[ifcopenshell.entity_instance] | None:
        if position is None:
            position = Matrix()

        results = []
        result = cls.auto_detect_curves(obj, obj.data, position)
        if isinstance(result, dict) and result["curves"]:
            for curve in result["curves"]:
                results.append(tool.Ifc.get().add(curve))
        return results

    @classmethod
    def export_surface(cls, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
        ifc_file = tool.Ifc.get()
        builder = ShapeBuilder(ifc_file)
        p1, p2, p3 = [v.co.copy() for v in obj.data.vertices[0:3]]

        edge1 = p2 - p1
        edge2 = p3 - p1
        normal = edge1.cross(edge2)
        z_axis = normal.normalized()
        x_axis = p2 - p1
        x_axis.normalize()
        y_axis = z_axis.cross(x_axis)

        position = Matrix()
        position.col[0][:3] = x_axis
        position.col[1][:3] = y_axis
        position.col[2][:3] = z_axis
        position.translation = p1

        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        result = cls.auto_detect_profiles(obj, obj.data, position)

        if not isinstance(result, dict):  # Ugly
            return

        profile_def = result["profile_def"]
        if profile_def.is_a("IfcCompositeProfileDef"):
            profile_def = profile_def.Profiles[0]

        cls.bm = bmesh.new()
        cls.bm.from_mesh(obj.data)
        cls.bm.verts.ensure_lookup_table()
        cls.bm.edges.ensure_lookup_table()

        surface = tool.Ifc.get().createIfcCurveBoundedPlane()
        placement = builder.create_axis2_placement_3d([o / cls.unit_scale for o in p1], z_axis, x_axis)
        surface.BasisSurface = ifc_file.create_entity("IfcPlane", placement)

        surface.OuterBoundary = tool.Ifc.get().add(profile_def.OuterCurve)
        if profile_def.is_a("IfcArbitraryProfileDefWithVoids"):
            surface.InnerBoundaries = [tool.Ifc.get().add(c) for c in profile_def.InnerCurves]

        cls.bm.free()
        return surface

    @classmethod
    def generate_occurrence_name(cls, element_type: ifcopenshell.entity_instance, ifc_class: str) -> str:
        prefs = tool.Blender.get_addon_preferences()
        if prefs.occurrence_name_style == "CLASS":
            return ifc_class[3:]
        elif prefs.occurrence_name_style == "TYPE":
            return element_type.Name or "Unnamed"
        elif prefs.occurrence_name_style == "CUSTOM":
            try:
                # Power users gonna power
                return eval(prefs.occurrence_name_function) or "Instance"
            except:
                return "Instance"
        else:
            assert_never(prefs.occurrence_name_style)

    @classmethod
    def get_extrusion(cls, representation: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """Return first found IfcExtrudedAreaSolid"""
        if not representation.Items:
            return None
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanResult"):
                item = item.FirstOperand
            else:
                break

    @classmethod
    def get_sibling_occurrence_count(cls, element: ifcopenshell.entity_instance) -> int:
        """Number of *other* products sharing this element's body representation.

        Returns the count of products bound to the same resolved body rep, minus
        ``element`` itself and minus its type (if any). Zero when the element has
        no body rep, no resolved rep, or no siblings. A non-zero result means a
        parametric edit on ``element`` will silently mutate other instances'
        geometry."""
        body_rep = tool.Geometry.get_body_representation(element)
        if not body_rep:
            return 0
        resolved = ifcopenshell.util.representation.resolve_representation(body_rep)
        if not resolved:
            return 0
        elements = tool.Geometry.get_elements_by_representation(resolved)
        elements.discard(element)
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type is not None:
            elements.discard(element_type)
        return len(elements)

    unit_scale: float
    vertices: list[Vector]
    edges: list[Sequence[int]]
    arcs: list[Sequence[int]]
    circles: list[Sequence[int]]

    @classmethod
    def import_axis(
        cls,
        axis: Union[ifcopenshell.entity_instance, tuple[Vector, Vector]],
        obj=None,
        position: Optional[Matrix] = None,
    ) -> bpy.types.Object:
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        if isinstance(axis, tuple):
            cls.vertices.extend(
                [
                    position @ Vector(cls.convert_unit_to_si(axis[0])).to_3d(),
                    position @ Vector(cls.convert_unit_to_si(axis[1])).to_3d(),
                ]
            )
            cls.edges.append([0, 1])
        else:
            cls.convert_curve_to_mesh(obj, position, axis)

        mesh = bpy.data.meshes.new("Axis")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        tool.Geometry.get_mesh_props(mesh).subshape_type = "AXIS"

        if obj is None:
            obj = bpy.data.objects.new("Axis", mesh)
        else:
            obj.data = mesh

        return obj

    @classmethod
    def import_annotation_fill_area(
        cls, annotation_fill_area: ifcopenshell.entity_instance, obj: Optional[bpy.types.Object] = None
    ) -> bpy.types.Object:
        return cls.import_profile(annotation_fill_area, obj)

    @classmethod
    def import_profile(
        cls,
        profile: ifcopenshell.entity_instance,
        obj: Optional[bpy.types.Object] = None,
        position: Optional[Matrix] = None,
        x_angle: Optional[float] = None,
    ) -> Union[bpy.types.Object, None]:
        """Creates new profile mesh and assigns it to `obj`,
        if `obj` is `None` then new "Profile" object will be created.

        Need to make sure to remove temporary mesh/object after use to avoid orphan data.
        """
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        profiles = profile.Profiles if profile.is_a("IfcCompositeProfileDef") else [profile]
        for profile in profiles:
            if profile.is_a("IfcArbitraryClosedProfileDef"):
                cls.convert_curve_to_mesh(obj, position, profile.OuterCurve, x_angle=x_angle)
                if profile.is_a("IfcArbitraryProfileDefWithVoids"):
                    for inner_curve in profile.InnerCurves:
                        cls.convert_curve_to_mesh(obj, position, inner_curve, x_angle=x_angle)
            elif profile.is_a() == "IfcRectangleProfileDef":
                cls.import_rectangle(obj, position, profile)
            elif profile.is_a() == "IfcAnnotationFillArea":
                cls.convert_curve_to_mesh(obj, position, profile.OuterBoundary)
                for inner_boundary in profile.InnerBoundaries or []:
                    cls.convert_curve_to_mesh(obj, position, inner_boundary)

        if not cls.vertices or not cls.edges:
            return None

        mesh = bpy.data.meshes.new("Profile")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        tool.Geometry.get_mesh_props(mesh).subshape_type = "PROFILE"

        if obj is None:
            obj = bpy.data.objects.new("Profile", mesh)
        else:
            old_data = obj.data
            obj.data = mesh
            if old_data and not old_data.users:
                bpy.data.meshes.remove(old_data)

        for arc in cls.arcs:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(arc, 1, "REPLACE")

        for circle in cls.circles:
            group = obj.vertex_groups.new(name="IFCCIRCLE")
            group.add(circle, 1, "REPLACE")

        return obj

    @classmethod
    def import_curve(
        cls,
        curve: ifcopenshell.entity_instance,
        obj: Optional[bpy.types.Object] = None,
        position: Optional[Matrix] = None,
    ) -> bpy.types.Object:
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        if tool.Geometry.is_curvelike_item(curve):
            cls.convert_curve_to_mesh(obj, position, curve)

        mesh = bpy.data.meshes.new("Curve")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        tool.Geometry.get_mesh_props(mesh).subshape_type = "PROFILE"

        if obj is None:
            obj = bpy.data.objects.new("Curve", mesh)
        else:
            old_data = obj.data
            obj.data = mesh
            if old_data and not old_data.users:
                bpy.data.meshes.remove(old_data)

        for arc in cls.arcs:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(arc, 1, "REPLACE")

        for circle in cls.circles:
            group = obj.vertex_groups.new(name="IFCCIRCLE")
            group.add(circle, 1, "REPLACE")

        return obj

    @classmethod
    def import_surface(
        cls, surface: ifcopenshell.entity_instance, obj: Optional[bpy.types.Object] = None
    ) -> bpy.types.Object:
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        if surface.is_a("IfcCurveBoundedPlane"):
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(surface.BasisSurface.Position).tolist())
            position.translation *= cls.unit_scale

            cls.convert_curve_to_mesh(obj, position, surface.OuterBoundary)
            for inner_boundary in surface.InnerBoundaries:
                cls.convert_curve_to_mesh(obj, position, inner_boundary)

        mesh = bpy.data.meshes.new("Surface")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        tool.Geometry.get_mesh_props(mesh).subshape_type = "PROFILE"

        if obj is None:
            obj = bpy.data.objects.new("Surface", mesh)
        else:
            obj.data = mesh

        for arc in cls.arcs:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(arc, 1, "REPLACE")

        for circle in cls.circles:
            group = obj.vertex_groups.new(name="IFCCIRCLE")
            group.add(circle, 1, "REPLACE")

        return obj

    class UnsupportedCurveForConversion(Exception):
        pass

    @classmethod
    def convert_curve_to_mesh(
        cls,
        obj: Union[bpy.types.Object, None],  # Unused argument.
        position: Matrix,
        curve: ifcopenshell.entity_instance,
        x_angle: Optional[float] = None,
    ) -> None:
        offset = len(cls.vertices)

        if curve.is_a("IfcPolyline"):
            curve_points: tuple[ifcopenshell.entity_instance, ...] = curve.Points
            # Polyline must have 2 points to be valid.
            is_closed = np.allclose(curve_points[0].Coordinates, curve_points[-1].Coordinates)

            points_to_add = curve_points[:-1] if is_closed else curve_points
            for point in points_to_add:
                global_point = position @ Vector(cls.convert_unit_to_si(point.Coordinates)).to_3d()
                cls.vertices.append(global_point)

            cls.edges.extend([(i, i + 1) for i in range(offset, len(cls.vertices) - 1)])
            if is_closed:
                cls.edges[-1] = (len(cls.vertices) - 1, offset)  # Close the loop

        elif curve.is_a("IfcCompositeCurve"):
            # This is a first pass incomplete implementation only for simple polylines, and misses many details.
            for segment in curve.Segments:
                cls.convert_curve_to_mesh(obj, position, segment.ParentCurve)

        elif curve.is_a("IfcIndexedPolyCurve"):
            for local_point in curve.Points.CoordList:
                global_point = position @ Vector(cls.convert_unit_to_si(local_point)).to_3d()
                if x_angle:
                    global_point = Vector((global_point[0], global_point[1] * cos(x_angle), global_point[2]))
                cls.vertices.append(global_point)
            if curve.Segments:
                for segment in curve.Segments:
                    if segment.is_a("IfcArcIndex"):
                        cls.arcs.append([i - 1 + offset for i in segment[0]])
                        cls.edges.append([i - 1 + offset for i in segment[0][:2]])
                        cls.edges.append([i - 1 + offset for i in segment[0][1:]])
                    else:
                        segment = [i - 1 + offset for i in segment[0]]
                        cls.edges.extend(zip(segment, segment[1:]))
            else:
                is_closed = False
                if cls.vertices[offset] == cls.vertices[-1]:
                    is_closed = True
                    del cls.vertices[-1]
                cls.edges.extend([(i, i + 1) for i in range(offset, len(cls.vertices) - 1)])
                if is_closed:
                    cls.edges.append([len(cls.vertices) - 1, offset])  # Close the loop
        elif curve.is_a("IfcCircle"):
            circle_position = Matrix(ifcopenshell.util.placement.get_axis2placement(curve.Position).tolist())
            circle_position.translation *= cls.unit_scale
            radius = cls.convert_unit_to_si(curve.Radius)
            cls.vertices.extend(
                [
                    position @ circle_position @ Vector((0, 0 - radius, 0.0)),
                    position @ circle_position @ Vector((0, 0 + radius, 0.0)),
                ]
            )
            cls.circles.append([offset, offset + 1])
            cls.edges.append((offset, offset + 1))
        else:
            raise cls.UnsupportedCurveForConversion(f"Profile has unsupported curve type: {curve}.")

    @classmethod
    def import_rectangle(cls, obj: bpy.types.Object, position: Matrix, profile: ifcopenshell.entity_instance) -> None:
        if profile.Position:
            p_position = Matrix(ifcopenshell.util.placement.get_axis2placement(profile.Position).tolist())
            p_position.translation *= cls.unit_scale
        else:
            p_position = Matrix()

        x = cls.convert_unit_to_si(profile.XDim)
        y = cls.convert_unit_to_si(profile.YDim)

        cls.vertices.extend(
            [
                position @ p_position @ Vector((-x / 2, -y / 2, 0.0)),
                position @ p_position @ Vector((x / 2, -y / 2, 0.0)),
                position @ p_position @ Vector((x / 2, y / 2, 0.0)),
                position @ p_position @ Vector((-x / 2, y / 2, 0.0)),
            ]
        )
        cls.edges.extend([(i, i + 1) for i in range(0, len(cls.vertices))])
        cls.edges[-1] = (len(cls.vertices) - 1, 0)  # Close the loop

    @classmethod
    def load_openings(cls, openings: list[ifcopenshell.entity_instance]) -> Iterable[bpy.types.Object]:
        if not openings:
            return []
        elements = set(openings)
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        ifc_importer.create_generic_elements(elements)
        ifc_importer.setup_arrays(openings_to_import=elements)
        for opening_obj in ifc_importer.added_data.values():
            tool.Collector.assign(opening_obj, should_clean_users_collection=False)
        return ifc_importer.added_data.values()

    @classmethod
    def purge_scene_openings(cls) -> None:
        """Purge removed scene openings."""
        props = cls.get_model_props()
        openings = props.openings
        for i in range(len(openings) - 1, -1, -1):
            if not openings[i].obj:
                openings.remove(i)

    @classmethod
    def save_custom_offset_to_pset(cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
        """Save custom offset settings to BBIM_MaterialLayer pset."""
        props = tool.Material.get_object_material_props(obj)

        if not props.use_custom_offset:
            # Remove pset if custom offset is disabled
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_MaterialLayer")
            if pset:
                pset_entity = tool.Ifc.get().by_id(pset["id"])
                ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset_entity)
            return

        # Determine which reference to save based on usage type
        usage_type = tool.Model.get_usage_type(element)
        custom_wall_reference = None
        custom_slab_reference = None

        if usage_type == "LAYER2":
            custom_wall_reference = props.custom_wall_reference
        elif usage_type == "LAYER3":
            custom_slab_reference = props.custom_slab_reference

        # Get or create pset
        pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_MaterialLayer")
        if pset_data:
            pset = tool.Ifc.get().by_id(pset_data["id"])
        else:
            pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_MaterialLayer")

        # Save properties (store in SI units)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        properties = {
            "UseCustomOffset": props.use_custom_offset,
            "CustomOffset": props.custom_offset / unit_scale,
            "CustomWallReference": custom_wall_reference if custom_wall_reference else "",
            "CustomSlabReference": custom_slab_reference if custom_slab_reference else "",
        }
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties=properties)

    @classmethod
    def load_custom_offset_from_pset(cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
        """Load custom offset settings from BBIM_MaterialLayer pset."""
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_MaterialLayer")
        if not pset:
            return

        props = tool.Material.get_object_material_props(obj)
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        # Load properties
        props.use_custom_offset = pset.get("UseCustomOffset", False)
        props.custom_offset = pset.get("CustomOffset", 0.0) * unit_scale  # Convert from SI

        # Load the appropriate reference based on usage type
        usage_type = tool.Model.get_usage_type(element)
        if usage_type == "LAYER2":
            custom_wall_ref = pset.get("CustomWallReference", "")
            if custom_wall_ref:
                props.custom_wall_reference = custom_wall_ref
        elif usage_type == "LAYER3":
            custom_slab_ref = pset.get("CustomSlabReference", "")
            if custom_slab_ref:
                props.custom_slab_reference = custom_slab_ref

    class MaterialLayerParameters(TypedDict):
        """Float values are in project units."""

        layer_set_direction: Literal["AXIS1", "AXIS2", "AXIS3"]
        thickness: float
        offset: float
        direction_sense: Literal["NEGATIVE", "POSITIVE"]

    @classmethod
    def get_material_layer_parameters(cls, element: ifcopenshell.entity_instance) -> MaterialLayerParameters:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        layer_set_direction = "AXIS2"
        offset = 0.0
        thickness = 0.0
        direction_sense = "POSITIVE"
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialLayerSetUsage"):
                layer_set_direction = material.LayerSetDirection
                offset = material.OffsetFromReferenceLine * unit_scale
                direction_sense = material.DirectionSense
                material = material.ForLayerSet
            if material.is_a("IfcMaterialLayerSet"):
                thickness = sum([l.LayerThickness for l in material.MaterialLayers]) * unit_scale
        return cls.MaterialLayerParameters(
            layer_set_direction=layer_set_direction,
            thickness=thickness,
            offset=offset,
            direction_sense=direction_sense,
        )

    @classmethod
    def get_material_layer_custom_offset(
        cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object
    ) -> Optional[float]:
        """Get custom offset value, reading from pset if props are not set."""
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        layer_params = tool.Model.get_material_layer_parameters(element)
        layer_offset = layer_params["offset"]
        thickness = layer_params["thickness"]
        props = tool.Material.get_object_material_props(obj)

        # Try to load from pset if not already in props
        if not props.use_custom_offset:
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_MaterialLayer")
            if pset and pset.get("UseCustomOffset", False):
                # Load from pset
                custom_offset = pset.get("CustomOffset", 0.0) * unit_scale
                usage_type = tool.Model.get_usage_type(element)

                if usage_type == "LAYER2":
                    custom_offset_reference = pset.get("CustomWallReference", "CENTER")
                elif usage_type == "LAYER3":
                    custom_offset_reference = pset.get("CustomSlabReference", "MIDDLE")
                else:
                    return None
            else:
                return None
        else:
            # Use current props
            custom_offset = props.custom_offset
            if tool.Model.get_usage_type(element) == "LAYER2":
                custom_offset_reference = props.custom_wall_reference
            elif tool.Model.get_usage_type(element) == "LAYER3":
                custom_offset_reference = props.custom_slab_reference
            else:
                return None

        direction_sense = layer_params["direction_sense"]

        if direction_sense == "POSITIVE" and custom_offset_reference in {"INTERIOR", "TOP"}:
            layer_offset = custom_offset - thickness
        if direction_sense == "POSITIVE" and custom_offset_reference in {"CENTER", "MIDDLE"}:
            layer_offset = custom_offset - (thickness / 2)
        if (direction_sense == "POSITIVE" and custom_offset_reference in {"EXTERIOR", "BOTTOM"}) or (
            direction_sense == "NEGATIVE" and custom_offset_reference in {"EXTERIOR", "TOP"}
        ):
            layer_offset = custom_offset
        if direction_sense == "NEGATIVE" and custom_offset_reference in {"CENTER", "MIDDLE"}:
            layer_offset = custom_offset + (thickness / 2)
        if direction_sense == "NEGATIVE" and custom_offset_reference in {"INTERIOR", "BOTTOM"}:
            layer_offset = custom_offset + thickness

        return layer_offset / unit_scale

    @classmethod
    def get_booleans(
        cls,
        element: Optional[ifcopenshell.entity_instance] = None,
        representation: Optional[ifcopenshell.entity_instance] = None,
    ) -> list[ifcopenshell.entity_instance]:
        """Either element or representation must be provided."""
        assert element or representation, "Either element or representation must be provided."
        if representation is None:
            assert element
            representation = tool.Geometry.get_body_representation(element)
            if not representation:
                return []
        booleans = []
        items = list(representation.Items)
        while items:
            item = items.pop()
            if item.is_a("IfcBooleanResult"):
                booleans.append(item)
                items.append(item.FirstOperand)
        return booleans

    @classmethod
    def get_connected_slab_objs(cls, wall: ifcopenshell.entity_instance) -> list[bpy.types.Object]:
        """Return Blender objects for slabs connected to wall via IfcRelConnectsElements(TOP)."""
        result = []
        for rel in wall.ConnectedFrom:
            if rel.is_a("IfcRelConnectsElements") and rel.Description == "TOP":
                slab_obj = tool.Ifc.get_object(rel.RelatingElement)
                if slab_obj:
                    result.append(slab_obj)
        return result

    @classmethod
    def get_connected_wall_objs(cls, slab: ifcopenshell.entity_instance) -> list[bpy.types.Object]:
        """Return Blender objects for LAYER2 walls connected to slab via IfcRelConnectsElements(TOP)."""
        result = []
        for rel in slab.ConnectedTo:
            if rel.is_a("IfcRelConnectsElements") and rel.Description == "TOP":
                wall_obj = tool.Ifc.get_object(rel.RelatedElement)
                if wall_obj:
                    result.append(wall_obj)
        return result

    @classmethod
    def has_underside_connection(cls, element: ifcopenshell.entity_instance) -> bool:
        """Return True if element has an IfcRelConnectsElements(TOP) relationship."""
        return any(rel.is_a("IfcRelConnectsElements") and rel.Description == "TOP" for rel in element.ConnectedFrom)

    @classmethod
    def strip_underside_booleans(cls, wall: ifcopenshell.entity_instance) -> bool:
        """Remove slab-trim ``IfcBooleanResult`` items from a wall's body chain.

        Returns ``True`` if any boolean was removed, so the caller knows whether
        a Blender-side body reload is needed to surface the geometry change.

        Hook for the duplicate path (Shift+D): the source wall's clip booleans
        don't make sense on a copy pulled away from the slab. Booleans whose
        ``SecondOperand.is_a("IfcTessellatedFaceSet")`` are removed — same
        imprecise discriminator the rest of the wall-to-underside machinery
        uses (manual cuts authored from tessellated meshes would also be
        stripped, but most manual cuts use ``IfcExtrudedAreaSolid`` / CSG
        primitives and are unaffected).

        Cannot reuse ``remove_wall_to_underside_booleans`` here because the
        duplicate's ``BBIM_Boolean.Data`` holds the source wall's stale ids —
        ``get_manual_booleans`` returns empty on the copy and the helper
        early-returns. The duplicate hook works directly off the chain.
        """
        representation = tool.Geometry.get_body_representation(wall)
        if not representation:
            return False
        chain = cls.get_booleans(wall, representation)
        to_remove = [b for b in chain if (sec := b.SecondOperand) is not None and sec.is_a("IfcTessellatedFaceSet")]
        for b in to_remove:
            tool.Geometry.remove_representation_item(b.SecondOperand, wall)
        # Sweep the now-stale BBIM_Boolean entries on the copy (their ids point
        # at booleans that were never in this wall's chain — they survived the
        # ifcopenshell deep copy as JSON text in the pset payload).
        pset_data = ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean")
        if pset_data:
            representation = tool.Geometry.get_body_representation(wall)
            chain_ids = {b.id() for b in cls.get_booleans(wall, representation)} if representation else set()
            stored_ids = set(json.loads(pset_data["Data"]))
            stale_ids = stored_ids - chain_ids
            if stale_ids:
                cls.unmark_manual_booleans(wall, list(stale_ids))
        return bool(to_remove)

    @classmethod
    def remove_wall_to_underside_booleans(cls, wall: ifcopenshell.entity_instance) -> None:
        """Remove all IfcBooleanResult items previously added by extend_walls_to_underside."""
        manual_booleans = cls.get_manual_booleans(wall)
        if not manual_booleans:
            return
        ifc_file = tool.Ifc.get()
        for b in manual_booleans:
            sec = b.SecondOperand
            if sec is None:
                # The IfcPolygonalFaceSet was already deleted externally.  Splice the
                # orphaned IfcBooleanResult out of the chain so the representation stays valid.
                parents = list(ifc_file.get_inverse(b))
                for parent in parents:
                    if parent.is_a("IfcBooleanResult") and parent.FirstOperand == b:
                        parent.FirstOperand = b.FirstOperand
                    elif parent.is_a("IfcShapeRepresentation"):
                        new_items = tuple((set(parent.Items) - {b}) | {b.FirstOperand})
                        parent.Items = new_items
                cls.unmark_manual_booleans(wall, [b.id()])
                ifc_file.remove(b)
            elif sec.is_a("IfcTessellatedFaceSet"):
                tool.Geometry.remove_representation_item(sec, wall)

    @classmethod
    def get_manual_booleans(
        cls, element: ifcopenshell.entity_instance, representation: Optional[ifcopenshell.entity_instance] = None
    ) -> list[ifcopenshell.entity_instance]:
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        if not pset:
            return []
        boolean_ids = json.loads(pset["Data"])
        if representation is None:
            representation = tool.Geometry.get_body_representation(element)
            if not representation:
                return []
        all_chain_booleans = cls.get_booleans(element, representation)
        booleans = [b for b in all_chain_booleans if b.id() in boolean_ids]
        return booleans

    @classmethod
    def mark_manual_booleans(
        cls, element: ifcopenshell.entity_instance, booleans: list[ifcopenshell.entity_instance]
    ) -> None:
        pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        boolean_ids = [b.id() for b in booleans]
        if pset_data:
            pset = tool.Ifc.get().by_id(pset_data["id"])
            data = json.loads(pset_data["Data"])
            data.extend(boolean_ids)
            data = list(set(data))
        else:
            pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_Boolean")
            data = boolean_ids
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})

    @classmethod
    def unmark_manual_booleans(cls, element: ifcopenshell.entity_instance, boolean_ids: list[int]) -> None:
        """Remove boolean ids from ``element``'s 'BBIM_Boolean' pset.

        :param boolean_ids: List of boolean ids to remove.
            Ids are used instead of entities to make it possible to unmark already removed booleans.
            Provided ids may not be marked as manual booleans previously.
        """
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        if not pset:
            return
        data = set(json.loads(pset["Data"]))
        data -= set(boolean_ids)
        data = list(data)
        pset = tool.Ifc.get().by_id(pset["id"])
        if data:
            data = tool.Ifc.get().createIfcText(json.dumps(data))
            ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data})
        else:
            ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

    @classmethod
    def get_flow_segment_axis(cls, obj: bpy.types.Object) -> tuple[Vector, Vector]:
        z_values = [v[2] for v in obj.bound_box]
        return (obj.matrix_world @ Vector((0, 0, min(z_values))), obj.matrix_world @ Vector((0, 0, max(z_values))))

    @classmethod
    def get_flow_segment_profile(
        cls, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if material and material.is_a("IfcMaterialProfileSet") and len(material.MaterialProfiles) == 1:
            return material.MaterialProfiles[0].Profile

    @classmethod
    def get_usage_type(
        cls, element: ifcopenshell.entity_instance
    ) -> Optional[Literal["LAYER1", "LAYER2", "LAYER3", "PROFILE"]]:
        material = ifcopenshell.util.element.get_material(element, should_inherit=False)
        if material:
            if material.is_a("IfcMaterialLayerSetUsage"):
                return f"LAYER{material.LayerSetDirection[-1]}"
            elif material.is_a("IfcMaterialLayerSet"):
                axis = ifcopenshell.util.element.get_pset(element, "EPset_Parametric", "LayerSetDirection")
                if axis is None:
                    if element.is_a() in (
                        "IfcSlabType",
                        "IfcRoofType",
                        "IfcRampType",
                        "IfcPlateType",
                        "IfcSlab",
                        "IfcRoof",
                        "IfcRamp",
                        "IfcPlate",
                    ):
                        axis = "AXIS3"
                    elif element.is_a() in ("IfcWallType", "IfcWall"):
                        axis = "AXIS2"
                    else:
                        return
                return f"LAYER{axis[-1]}"
            elif material.is_a("IfcMaterialProfileSetUsage"):
                # TODO: remove after we support editing profile usages with IfcRevolvedAreaSolid.
                # Revolved area check should happen inside bim.enable_editing_extrusion_axis
                # but keep it here to trigger import_representation_items,
                # so users will be able to at least move IfcRevolvedAreaSolid, until there will be a full support.
                body = tool.Geometry.get_body_representation(element)
                if body and any(
                    i.is_a("IfcRevolvedAreaSolid") for i in ifcopenshell.util.representation.resolve_base_items(body)
                ):
                    return
                return "PROFILE"
            elif material.is_a("IfcMaterialProfileSet"):
                return "PROFILE"

    @classmethod
    def get_wall_axis(
        cls, obj: bpy.types.Object, layers: Optional[MaterialLayerParameters] = None
    ) -> dict[str, list[Vector]]:
        """Each item of a resulting dictionary is a list of 2 2D vectors."""
        x_values = [v[0] for v in obj.bound_box]
        min_x = min(x_values)
        max_x = max(x_values)
        axes = {}
        if layers:
            direction = 1 if layers["direction_sense"] == "POSITIVE" else -1
            axes = {
                "base": [
                    (obj.matrix_world @ Vector((min_x, layers["offset"], 0.0))).to_2d(),
                    (obj.matrix_world @ Vector((max_x, layers["offset"], 0.0))).to_2d(),
                ],
                "side": [
                    (
                        obj.matrix_world @ Vector((min_x, layers["offset"] + (layers["thickness"] * direction), 0.0))
                    ).to_2d(),
                    (
                        obj.matrix_world @ Vector((max_x, layers["offset"] + (layers["thickness"] * direction), 0.0))
                    ).to_2d(),
                ],
            }
        axes["reference"] = [
            (obj.matrix_world @ Vector((min_x, 0.0, 0.0))).to_2d(),
            (obj.matrix_world @ Vector((max_x, 0.0, 0.0))).to_2d(),
        ]
        return axes

    @classmethod
    def get_connected_walls(cls, walls: list[bpy.types.Object]) -> list[bpy.types.Object]:
        """
        Loop through walls by retrieving the next connected wall using the connection path.
        If the function encounters the first wall again, it will return the list of connected walls.
        """

        first_wall = tool.Ifc.get_entity(walls[0])
        previous_wall = None
        current_wall = first_wall
        ordered_walls = [first_wall]

        for i in range(len(walls)):
            paths = []
            paths.extend([path for path in current_wall.ConnectedTo])
            paths.extend([path for path in current_wall.ConnectedFrom])

            if len(paths) <= 1:
                return []

            for path in paths:
                next_wall = path.RelatedElement if path.RelatedElement != current_wall else path.RelatingElement
                if next_wall == previous_wall:
                    continue

                if next_wall != current_wall and next_wall != first_wall and next_wall not in ordered_walls:
                    ordered_walls.append(next_wall)
                    previous_wall = current_wall
                    current_wall = next_wall
                    break

                if next_wall == first_wall:
                    return [tool.Ifc.get_object(wall) for wall in ordered_walls]
        return []

    @classmethod
    def get_polygons_from_wall_axis(cls, walls: list[bpy.types.Object]) -> list[shapely.Polygon]:
        """
        Get the polygons formed by the intersection of the wall axis reference and side.
        The polygon with the larger area will be considered the external polygon.
        This function only works with closed loops.
        """
        points1 = []
        points2 = []
        for w1, w2 in zip(walls, walls[1:] + [walls[0]]):
            layers1 = tool.Model.get_material_layer_parameters(tool.Ifc.get_entity(w1))
            layers2 = tool.Model.get_material_layer_parameters(tool.Ifc.get_entity(w2))
            axis1 = tool.Model.get_wall_axis(w1, layers1)
            axis2 = tool.Model.get_wall_axis(w2, layers2)
            intersection1 = tool.Cad.intersect_edges_v2(axis1["reference"], axis2["reference"])
            intersection2 = tool.Cad.intersect_edges_v2(axis1["side"], axis2["side"])
            if intersection1[0] is None or intersection2[0] is None:
                for v1 in axis1["reference"]:
                    for v2 in axis2["reference"]:
                        if tool.Cad.are_vectors_equal(v1, v2, 1e-5):
                            intersection1 = [v1]
                for v1 in axis1["side"]:
                    for v2 in axis2["side"]:
                        if tool.Cad.are_vectors_equal(v1, v2, 1e-5):
                            intersection2 = [v1]

            points1.append(intersection1[0])
            points2.append(intersection2[0])

        poly1 = shapely.Polygon(points1)
        poly2 = shapely.Polygon(points2)

        return poly1 if poly1.area > poly2.area else poly2

    @classmethod
    def handle_array_on_copied_element(
        cls, element: ifcopenshell.entity_instance, array_data: Optional[dict[str, Any]] = None
    ) -> None:
        """Post-copy hook: decide what to do with the BBIM_Array pset a copy
        inherits from its source.

        - ``array_data=None`` — detach the copy from any array. Removes the
          inherited BBIM_Array pset and any CHILD_OF constraint.
        - ``array_data`` provided — promote the copy to a fresh array parent
          with an empty children list, using the provided layer config.
        """

        if array_data is None:
            array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not array_pset:
                return

            # TODO: Non-strictness is temporary. It was added due
            # to a bug infecting ifc models since it occurred,
            # can be reverted later.
            array_pset_data = array_pset.get("Data", None)
            array_pset = tool.Ifc.get().by_id(array_pset["id"])
            ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=array_pset)

            # remove constraints
            obj = tool.Ifc.get_object(element)
            assert isinstance(obj, bpy.types.Object)
            if not array_pset_data:  # skip array parents
                constraint = next((c for c in obj.constraints if c.type == "CHILD_OF"), None)
                if constraint:
                    matrix = obj.matrix_world.copy()
                    obj.constraints.remove(constraint)
                    # Keep the matrix before removing the constraint,
                    # otherwise object will jump to some previous position.
                    obj.matrix_world = matrix
                tool.Blender.lock_transform(obj, False)

        else:
            obj = tool.Ifc.get_object(element)
            array_pset = tool.Pset.get_element_pset(element, "BBIM_Array")
            default_data = tool.Ifc.get().createIfcText('[{"children": []}]')
            ifcopenshell.api.pset.edit_pset(
                tool.Ifc.get(),
                pset=array_pset,
                properties={"Parent": element.GlobalId, "Data": default_data},
            )

            tool.Model.regenerate_array(obj, array_data)

            array_pset = tool.Pset.get_element_pset(element, "BBIM_Array")
            json_data = tool.Ifc.get().createIfcText(json.dumps(array_data))
            ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=array_pset, properties={"Data": json_data})

            for i in range(len(array_data)):
                tool.Array.set_children_lock_state(element, i, True)
            tool.Array.constrain_children_to_parent(element)

    @classmethod
    def regenerate_array(
        cls, parent_obj: bpy.types.Object, data: list[dict[str, Any]], array_layers_to_apply: Iterable[int] = tuple()
    ) -> None:
        """`array_layers_to_apply` - list of array layer indices to apply"""
        with tool.Geometry.batch_host_recut():
            cls._regenerate_array_body(parent_obj, data, array_layers_to_apply)

    @classmethod
    def _prune_orphan_array_children(cls, array: dict[str, Any]) -> None:
        """Drop GUIDs from ``array['children']`` whose IFC entity or Blender
        object is no longer alive, and cascade-remove the orphan IFC entity
        if it still exists. Outliner / keyboard delete of a Bonsai-managed
        object bypasses ``bim.delete``'s cascade, leaving dangling opening
        and filling references that later confuse regen and crash the
        ``batch_host_recut`` drain."""
        live_guids: list[str] = []
        ifc_file = tool.Ifc.get()
        for guid in array["children"]:
            try:
                element = ifc_file.by_guid(guid)
            except RuntimeError:
                continue
            obj = tool.Ifc.get_object(element)
            try:
                is_live = obj is not None and obj.data is not None
            except ReferenceError:
                is_live = False
            if is_live:
                live_guids.append(guid)
                continue
            try:
                ifcopenshell.api.root.remove_product(ifc_file, product=element)
            except (RuntimeError, ifcopenshell.Error):
                pass
        array["children"] = live_guids

    @classmethod
    def _regenerate_array_body(
        cls, parent_obj: bpy.types.Object, data: list[dict[str, Any]], array_layers_to_apply: Iterable[int]
    ) -> None:
        parent_element = tool.Ifc.get_entity(parent_obj)

        if pset := ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array"):
            ifcopenshell.api.pset.remove_pset(
                tool.Ifc.get(), product=parent_element, pset=tool.Ifc.get().by_id(pset["id"])
            )

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj_stack = [parent_obj]

        for array_i, array in enumerate(data):
            cls._prune_orphan_array_children(array)
            child_i = 0
            existing_children = set(array["children"])
            total_existing_children = len(array["children"])
            children_elements = []
            children_objs = []

            # calculate offset
            if array["method"] == "DISTRIBUTE":
                divider = 1 if ((array["count"] - 1) == 0) else (array["count"] - 1)
                base_offset = Vector([array["x"], array["y"], array["z"]]) / divider * unit_scale
            else:
                base_offset = Vector([array["x"], array["y"], array["z"]]) * unit_scale

            target_new_in_this_layer = (array["count"] - 1) * len(obj_stack)
            missing_count = max(0, target_new_in_this_layer - total_existing_children)
            new_entities_pool: list[ifcopenshell.entity_instance] = []
            if missing_count > 0:
                batch_old_to_new = tool.Geometry.duplicate_ifc_object_n_times(parent_obj, missing_count)
                new_entities_pool = batch_old_to_new.get(parent_element, [])
            new_entities_iter = iter(new_entities_pool)

            for i in range(array["count"]):
                if i == 0:
                    continue
                offset = base_offset * i

                for obj in obj_stack:
                    # IndexError when child_i is past the recorded children list
                    # (count grew); RuntimeError when by_guid finds no entity (the
                    # child was deleted outside the array op); AssertionError when
                    # the IFC entity exists but its Blender object was unlinked.
                    # All three fall through to duplication.
                    try:
                        global_id = array["children"][child_i]
                        child_element = tool.Ifc.get().by_guid(global_id)
                        child_obj = tool.Ifc.get_object(child_element)
                        assert child_obj
                    except (IndexError, RuntimeError, AssertionError):
                        try:
                            child_element = next(new_entities_iter)
                        except StopIteration:
                            # Stale-GUID mid-list left the pool exhausted; fall back
                            # to a one-off duplicate so the layer can still complete.
                            old_to_new, _ = tool.Geometry.duplicate_ifc_objects([parent_obj])
                            child_element = next(iter(old_to_new.values()))[0]
                        child_obj = tool.Ifc.get_object(child_element)

                    # add child pset
                    if not (child_pset := tool.Pset.get_element_pset(child_element, "BBIM_Array")):
                        child_pset = ifcopenshell.api.pset.add_pset(
                            tool.Ifc.get(), product=child_element, name="BBIM_Array"
                        )
                    ifcopenshell.api.pset.edit_pset(
                        tool.Ifc.get(),
                        pset=child_pset,
                        properties={"Data": None, "Parent": parent_element.GlobalId},
                        should_purge=False,
                    )

                    # set child object position
                    new_matrix = obj.matrix_world.copy()
                    if array["use_local_space"]:
                        current_obj_translation = obj.matrix_world @ offset
                    else:
                        current_obj_translation = obj.matrix_world.translation + offset
                    new_matrix.translation = current_obj_translation
                    child_obj.matrix_world = new_matrix

                    children_objs.append(child_obj)
                    children_elements.append(child_element)
                    child_i += 1

            obj_stack.extend(children_objs)
            array["children"] = [e.GlobalId for e in children_elements]

            # handle elements unused in the array after regeneration
            removed_children = set(existing_children) - set(array["children"])
            for removed_child in removed_children:
                try:
                    element = tool.Ifc.get().by_guid(removed_child)
                except RuntimeError:
                    continue
                # Strip any wall/slab opening cut by this child before deletion,
                # so the host's HasOpenings shrinks symmetrically with count.
                if getattr(element, "FillsVoids", None):
                    ifcopenshell.api.feature.remove_feature(
                        tool.Ifc.get(), feature=element.FillsVoids[0].RelatingOpeningElement
                    )
                obj = tool.Ifc.get_object(element)
                if obj:
                    tool.Geometry.delete_ifc_object(obj)

            if array.get("per_child_opening", array.get("mirror_to_host", True)) and children_elements:
                cls.mirror_parent_void_fillings_to_children(parent_element, children_elements)

            if array_i in array_layers_to_apply:
                for child_element in children_elements:
                    pset = tool.Pset.get_element_pset(child_element, "BBIM_Array")
                    ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=child_element, pset=pset)
                    cls.unshare_opening_representation(child_element)

                array["children"] = []
                array["count"] = 1

            bpy.context.view_layer.update()

        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=parent_element, name="BBIM_Array")
        json_data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.pset.edit_pset(
            tool.Ifc.get(), pset=pset, properties={"Data": json_data, "Parent": parent_element.GlobalId}
        )

        tool.Blender.set_object_selection(parent_obj, True)

    @classmethod
    def mirror_parent_void_fillings_to_children(
        cls,
        parent_element: ifcopenshell.entity_instance,
        children_elements: Sequence[ifcopenshell.entity_instance],
    ) -> None:
        """Replicate the parent's FillsVoids → host chain onto each array child.

        For each child, tears down any stale opening, creates a new
        IfcOpeningElement at the child's current placement, reuses the parent's
        opening representation as a MappedRepresentation, and adds the
        void + filling pair so the host element is cut once per child.

        No-op when the parent is not a filling, when the host element cannot
        be resolved, or when the children list is empty. Opt out via the
        per-layer ``per_child_opening`` flag on ``BBIM_Array.Data`` (legacy
        key ``mirror_to_host`` still honoured for round-trip with older files).
        """
        host = tool.Spatial.get_host_element(parent_element)
        if host is None or not children_elements:
            return

        ifc_file = tool.Ifc.get()
        parent_opening = parent_element.FillsVoids[0].RelatingOpeningElement
        parent_opening_rep = ifcopenshell.util.representation.get_representation(
            parent_opening, "Model", "Body", "MODEL_VIEW"
        )
        if parent_opening_rep is None:
            return
        parent_opening_rep = ifcopenshell.util.representation.resolve_representation(parent_opening_rep)

        for child in children_elements:
            if getattr(child, "FillsVoids", None):
                ifcopenshell.api.feature.remove_feature(ifc_file, feature=child.FillsVoids[0].RelatingOpeningElement)
            child_obj = tool.Ifc.get_object(child)
            if child_obj is None:
                continue

            new_opening = ifcopenshell.api.root.create_entity(
                ifc_file,
                ifc_class="IfcOpeningElement",
                predefined_type="OPENING",
                name="Opening",
            )
            ifcopenshell.api.geometry.edit_object_placement(
                ifc_file,
                product=new_opening,
                matrix=np.array(child_obj.matrix_world),
                is_si=True,
            )
            mapped_representation = ifcopenshell.api.geometry.map_representation(
                ifc_file, representation=parent_opening_rep
            )
            ifcopenshell.api.geometry.assign_representation(
                ifc_file, product=new_opening, representation=mapped_representation
            )
            ifcopenshell.api.feature.add_feature(ifc_file, feature=new_opening, element=host)
            ifcopenshell.api.feature.add_filling(ifc_file, opening=new_opening, element=child)

        # Openings affect every sub-element of an aggregate, not just the named host.
        voided_objs: list[bpy.types.Object] = []
        host_obj = tool.Ifc.get_object(host)
        if host_obj is not None:
            voided_objs.append(host_obj)
        for subelement in tool.Aggregate.get_parts_recursively(host):
            subobj = tool.Ifc.get_object(subelement)
            if subobj is not None:
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if not voided_obj.data:
                continue
            voided_element = tool.Ifc.get_entity(voided_obj)
            if voided_element is None:
                continue
            context = tool.Geometry.get_active_representation_context(voided_obj)
            representation = tool.Geometry.get_representation_by_context(voided_element, context)
            if representation is None:
                continue
            tool.Geometry.recut_host(voided_obj, representation)

    @classmethod
    def unshare_opening_representation(cls, filling: ifcopenshell.entity_instance) -> None:
        """Detach a filling's opening representation from any shared mapped body.

        Required when a Bonsai array child is promoted to an independent
        object: the array's per-child opening mirror builds each child's
        opening representation as an ``IfcMappedRepresentation`` over the
        parent opening's body. Without this detach, a later edit replacing
        the parent body rewrites the shared ``IfcRepresentationMap`` and
        reshapes the former-child's opening too."""
        if not getattr(filling, "FillsVoids", None):
            return
        tool.Geometry.detach_representation(filling.FillsVoids[0].RelatingOpeningElement)

    @classmethod
    def replace_object_ifc_representation(
        cls,
        ifc_context: ifcopenshell.entity_instance,
        obj: bpy.types.Object,
        new_representation: ifcopenshell.entity_instance,
    ) -> None:
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        ifc_file = tool.Ifc.get()
        ifc_element = tool.Ifc.get_entity(obj)
        assert ifc_element
        old_representation = ifcopenshell.util.representation.get_representation(
            ifc_element, ifc_context.ContextType, ifc_context.ContextIdentifier, ifc_context.TargetView
        )

        if old_representation:
            old_representation = tool.Geometry.resolve_mapped_representation(old_representation)
            for inverse in ifc_file.get_inverse(old_representation):
                ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)
            ifcopenshell.api.geometry.remove_representation(ifc_file, representation=old_representation)
        else:
            ifcopenshell.api.geometry.assign_representation(
                ifc_file, product=ifc_element, representation=new_representation
            )
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=new_representation,
        )

    @classmethod
    def update_thumbnail_for_element(cls, element: ifcopenshell.entity_instance, refresh: bool = False) -> None:
        if bpy.app.background:
            return

        from PIL import Image, ImageDraw

        from bonsai.bim.module.model.data import AuthoringData

        obj = tool.Ifc.get_object(element)
        if not obj:
            return  # Nothing to process

        if not refresh and element.id() in AuthoringData.type_thumbnails:
            return  # Already processed

        assert isinstance(obj, bpy.types.Object)
        # Since Blender 4.5 have to use `preview_ensure` instead of `asset_generate_preview`, see #6839.
        obj.preview_ensure()

        if obj.data:
            # If object has .data we can use default Blender preview.
            # No need to preview to update, Blender will do it in background,
            # `preview.icon_id` doesn't change after `asset_generate_preview()`.
            obj.asset_generate_preview()
        # Avoid issues with sqlite files.
        elif type(tool.Ifc.get()) is not ifcopenshell.file:
            return
        else:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            size = 128
            img = Image.new("RGBA", (size, size))
            draw = ImageDraw.Draw(img)

            material = ifcopenshell.util.element.get_material(element)
            if material and material.is_a("IfcMaterialProfileSet"):
                profile = material.MaterialProfiles[0].Profile
                tool.Profile.draw_image_for_ifc_profile(draw, profile, size)

            elif material and material.is_a("IfcMaterialLayerSet"):
                thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                total_thickness = sum(thicknesses)
                si_total_thickness = total_thickness * unit_scale
                if si_total_thickness <= 0.051:
                    width = 10
                elif si_total_thickness <= 0.11:
                    width = 20
                elif si_total_thickness <= 0.21:
                    width = 30
                elif si_total_thickness <= 0.31:
                    width = 40
                else:
                    width = 50

                height = 100

                is_horizontal = cls.get_usage_type(element) == "LAYER3"
                if is_horizontal:
                    width, height = height, width

                x_offset = (size / 2) - (width / 2)
                y_offset = (size / 2) - (height / 2)
                draw.rectangle([x_offset, y_offset, width + x_offset, height + y_offset], outline="white", width=5)
                current_thickness = 0
                del thicknesses[-1]
                for thickness in thicknesses:
                    current_thickness += thickness
                    if is_horizontal:
                        y = (current_thickness / total_thickness) * height
                        line = [x_offset, y_offset + y, x_offset + width, y_offset + y]
                    else:
                        x = (current_thickness / total_thickness) * width
                        line = [x_offset + x, y_offset, x_offset + x, y_offset + height]
                    draw.line(line, fill="white", width=2)
            elif False:
                # TODO: things like parametric duct segments
                pass
            elif not element.RepresentationMaps:
                # Empties are represented by a generic thumbnail
                width = height = 100
                x_offset = (size / 2) - (width / 2)
                y_offset = (size / 2) - (height / 2)
                draw.line([x_offset, y_offset, width + x_offset, height + y_offset], fill="white", width=2)
                draw.line([x_offset, y_offset + height, width + x_offset, y_offset], fill="white", width=2)
                draw.rectangle([x_offset, y_offset, width + x_offset, height + y_offset], outline="white", width=5)
            else:
                draw.line([0, 0, size, size], fill="red", width=2)
                draw.line([0, size, size, 0], fill="red", width=2)

            pixels = [item for sublist in img.getdata() for item in sublist]

            obj.preview.image_size = size, size
            obj.preview.image_pixels_float = pixels

        AuthoringData.type_thumbnails[element.id()] = obj.preview.icon_id

    @classmethod
    def mark_thumbnail_for_update(cls, element: ifcopenshell.entity_instance) -> None:
        """Mark the thumbnail for the provided element as outdated.

        Allows postponing the thumbnail update until it is actually needed by the user.
        """
        from bonsai.bim.module.model.data import AuthoringData

        element_id = element.id()
        if element_id not in AuthoringData.type_thumbnails:
            return
        del AuthoringData.type_thumbnails[element_id]

    @classmethod
    def get_selected_ifc_objects(cls) -> list[bpy.types.Object]:
        return [obj for obj in tool.Blender.get_selected_objects() if tool.Ifc.get_entity(obj)]

    @classmethod
    def has_selected_ifc_objects(cls, include_active: bool = True) -> bool:
        return any(tool.Ifc.get_entity(obj) for obj in tool.Blender.get_selected_objects(include_active=include_active))

    @classmethod
    def get_selected_mesh_objects(cls) -> list[bpy.types.Object]:
        objects = tool.Blender.get_selected_objects()
        return [obj for obj in objects if obj.type == "MESH"]

    @classmethod
    def get_selected_mesh_ifc_objects(cls) -> list[bpy.types.Object]:
        return [obj for obj in tool.Model.get_selected_mesh_objects() if tool.Ifc.get_entity(obj)]

    @classmethod
    def has_selected_mesh_ifc_objects(cls) -> bool:
        return any(tool.Ifc.get_entity(obj) for obj in tool.Model.get_selected_mesh_objects())

    BBIM_PARAMETRIC_PSETS = (
        "BBIM_Window",
        "BBIM_Door",
        "BBIM_Roof",
        "BBIM_Railing",
        "BBIM_Stair",
    )

    @classmethod
    def get_modeling_bbim_pset_data(cls, object: bpy.types.Object, pset_name: str) -> Union[dict[str, Any], None]:
        """get modelling BBIM pset data (eg, BBIM_Roof) and loads it's `Data` as json to `data_dict`"""
        element = tool.Ifc.get_entity(object)
        if not element:
            return
        pset_data = ifcopenshell.util.element.get_pset(element, pset_name)
        if not pset_data:
            return
        pset_data["data_dict"] = json.loads(pset_data.get("Data", "[]") or "[]")
        return pset_data

    @classmethod
    def edit_element_placement(cls, element: ifcopenshell.entity_instance, matrix: Matrix) -> None:
        """Useful for moving objects like ports or openings -
        the method will ensure it will be moved in blender scene too if it exists"""
        obj = tool.Ifc.get_object(element)
        if obj:
            obj.matrix_world = matrix
            return
        ifcopenshell.api.geometry.edit_object_placement(tool.Ifc.get(), product=element, matrix=matrix, is_si=True)

    @classmethod
    def sync_object_ifc_position(cls, obj: bpy.types.Object) -> None:
        """make sure IFC position will be in sync with the Blender object position, if object was moved in Blender"""
        tool.Geometry.commit_placement_if_moved(obj)

    @classmethod
    def get_element_matrix(cls, element: ifcopenshell.entity_instance, keep_local: bool = False) -> Matrix:
        placement = element.ObjectPlacement
        if keep_local:
            placement = ifcopenshell.util.placement.get_axis2placement(placement.RelativePlacement)
        else:
            placement = ifcopenshell.util.placement.get_local_placement(placement)
        return Matrix(placement)

    @classmethod
    def reload_body_representation(cls, obj_or_objects: Union[bpy.types.Object, Iterable[bpy.types.Object]]) -> None:
        """Update body representation including all decomposed objects"""
        if isinstance(obj_or_objects, collections.abc.Iterable):
            objects = set(obj_or_objects)
        else:
            objects = {obj_or_objects}

        # decompose objects
        decomposed_objs = objects.copy()
        for obj in objects:
            for subelement in ifcopenshell.util.element.get_decomposition(tool.Ifc.get_entity(obj)):
                subobj = tool.Ifc.get_object(subelement)
                if subobj:
                    decomposed_objs.add(subobj)

        # update representation
        for obj in decomposed_objs:
            if not obj.data:
                continue
            element = tool.Ifc.get_entity(obj)
            body = tool.Geometry.get_body_representation(element)
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=body,
            )

    @classmethod
    def is_parametric_roof_active(cls) -> bool:
        from bonsai.bim.module.model.data import RoofData

        return bool((RoofData.is_loaded or not RoofData.load()) and RoofData.data["pset_data"])

    @classmethod
    def is_parametric_railing_active(cls) -> bool:
        from bonsai.bim.module.model.data import RailingData

        return bool((RailingData.is_loaded or not RailingData.load()) and RailingData.data["pset_data"])

    @classmethod
    def is_parametric_window_active(cls) -> bool:
        from bonsai.bim.module.model.data import WindowData

        return bool((WindowData.is_loaded or not WindowData.load()) and WindowData.data["pset_data"])

    @classmethod
    def is_parametric_door_active(cls) -> bool:
        from bonsai.bim.module.model.data import DoorData

        return bool((DoorData.is_loaded or not DoorData.load()) and DoorData.data["pset_data"])

    CustomTreadRunType = Union[tuple[float, float], tuple[None, None]]

    @classmethod
    def get_active_stair_calculated_params(cls, pset_data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        assert (obj := bpy.context.active_object)
        props = tool.Model.get_stair_props(obj)

        if props.is_editing:
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            number_of_treads = props.number_of_treads
            height = props.height / si_conversion
            tread_run = props.tread_run / si_conversion
            first_tread_run = props.custom_first_last_tread_run[0] / si_conversion
            last_tread_run = props.custom_first_last_tread_run[1] / si_conversion
            nosing_length = props.nosing_length / si_conversion
            use_custom_first_last_tread_run = not props.custom_tread_lock
        else:
            assert pset_data
            number_of_treads: int = pset_data["number_of_treads"]
            height: float = pset_data["height"]
            tread_run: float = pset_data["tread_run"]
            # use .get to not break the old .ifc models
            custom_first_last_tread_run: tool.Model.CustomTreadRunType = pset_data.get(
                "custom_first_last_tread_run", (0, 0)
            )
            first_tread_run, last_tread_run = custom_first_last_tread_run
            nosing_length = pset_data.get("nosing_length", 0)
            use_custom_first_last_tread_run = not pset_data.get("custom_tread_lock", True)

        calculated_params: dict[str, Any] = {}
        number_of_rises = number_of_treads + 1
        calculated_params["Number of Risers"] = number_of_rises
        calculated_params["Tread Rise"] = round(height / number_of_rises, 5)

        # Calculate total length taking into account custom first/last tread runs :
        length = 0.0
        default_rises = number_of_rises
        if use_custom_first_last_tread_run and first_tread_run is not None:
            default_rises -= 1
            length += first_tread_run
        if use_custom_first_last_tread_run and last_tread_run is not None:
            default_rises -= 1
            length += last_tread_run
        length += tread_run * default_rises

        # Handle nosing length effects on total length
        # Nosing overlaps don't affect tread run spacing,
        # but the first tread's nosing extends the total length
        if nosing_length > 0:  # nosing overlaps
            length += nosing_length
        if nosing_length < 0:  # tread gaps between treads
            length += abs(nosing_length) * number_of_treads

        calculated_params["Length"] = round(length, 5)
        pitch = height / length
        pitch_formatted = str(round(pitch * 100, 1)) + " % / " + str(round(degrees(atan(pitch)), 1)) + " deg"
        calculated_params["Pitch"] = str(pitch_formatted)

        return calculated_params

    StairType = Literal["CONCRETE", "WOOD/STEEL", "GENERIC"]

    DoorType = Literal[
        "SINGLE_SWING_LEFT",
        "SINGLE_SWING_RIGHT",
        "DOUBLE_SWING_LEFT",
        "DOUBLE_SWING_RIGHT",
        "DOUBLE_DOOR_SINGLE_SWING",
        "SLIDING_TO_LEFT",
        "SLIDING_TO_RIGHT",
        "DOUBLE_DOOR_SLIDING",
    ]

    WindowType = Literal[
        "SINGLE_PANEL",
        "DOUBLE_PANEL_HORIZONTAL",
        "DOUBLE_PANEL_VERTICAL",
        "TRIPLE_PANEL_BOTTOM",
        "TRIPLE_PANEL_TOP",
        "TRIPLE_PANEL_LEFT",
        "TRIPLE_PANEL_RIGHT",
        "TRIPLE_PANEL_HORIZONTAL",
        "TRIPLE_PANEL_VERTICAL",
    ]

    RoofGenerationMethod = Literal["HEIGHT", "ANGLE"]

    RailingType = Literal["FRAMELESS_PANEL", "WALL_MOUNTED_HANDRAIL"]

    @classmethod
    def generate_stair_2d_profile(
        cls,
        number_of_treads: int,
        height: float,
        width: float,
        tread_run: float,
        stair_type: StairType,
        # WOOD/STEEL CONCRETE STAIR ARGUMENTS
        tread_depth: Union[float, None] = None,
        # CONCRETE STAIR ARGUMENTS
        has_top_nib: Union[bool, None] = None,
        top_slab_depth: Union[float, None] = None,
        base_slab_depth: Union[float, None] = None,
        custom_first_last_tread_run: Union[tuple[float, float], tuple[None, None]] = (None, None),
        nosing_length: float = 0.0,
        # CONCRETE GENERIC STAIR ARGUMENTS
        nosing_depth: float = 0.0,
    ) -> tuple[list[Vector], list[tuple[int, ...]], list[[list[int]]]]:
        """returns a tuple of stair profile data: (vertices, edges, faces)"""
        vertices: list[Vector] = []
        edges: list[tuple[int, ...]] = []
        faces: list[[list[int]]] = []

        number_of_risers = number_of_treads + 1
        tread_rise = height / number_of_risers
        nosing_overlap = max(nosing_length, 0)
        nosing_tread_gap = -min(nosing_length, 0)
        nosing_overlap_offset = -V_(nosing_overlap, 0)
        first_tread_run = custom_first_last_tread_run[0] if custom_first_last_tread_run[0] is not None else tread_run

        def define_generic_stair_treads():
            vertices.append(Vector([0, 0]))
            nonlocal nosing_depth, nosing_overlap
            # avoid weird geometry
            nosing_depth = min(nosing_depth, tread_rise)
            nosing_overlap = min(nosing_overlap, tread_run)

            default_tread_edges = np.array(((0, 1), (1, 2)))
            # horizontal tread line
            if nosing_overlap == 0:
                default_tread_verts = (V_(0, tread_rise), V_(tread_run, tread_rise))
            elif nosing_depth == 0:
                default_tread_verts = (V_(-nosing_overlap, tread_rise), V_(tread_run, tread_rise))
            else:  # nosing_overlap > 0 nosing_depth > 0
                # kind of L shape:
                # (2)●───────────────────────────●(3)
                #    |
                #    |
                #    ●──────────────●
                #  (1)              (0)
                default_tread_verts = (
                    V_(0, tread_rise - nosing_depth),
                    V_(-nosing_overlap, tread_rise - nosing_depth),
                    V_(-nosing_overlap, tread_rise),
                    V_(tread_run, tread_rise),
                )
                add_edges = ((2, 3), (3, 4))
                default_tread_edges = np.concatenate((default_tread_edges, add_edges))
            default_tread_offset = Vector([tread_run, tread_rise])

            def get_tread_data(i):
                # Check if this is first or last tread with custom run
                current_tread_run = None
                if i == 0 and custom_first_last_tread_run[0] is not None:
                    current_tread_run = custom_first_last_tread_run[0]
                elif i == number_of_risers - 1 and custom_first_last_tread_run[1] is not None:
                    current_tread_run = custom_first_last_tread_run[1]

                if current_tread_run is not None:
                    tread_offset = default_tread_offset.copy()
                    tread_offset.x = current_tread_run

                    # Handle zero-width treads
                    if current_tread_run == 0:
                        # For zero width, just return vertical offset with no horizontal tread
                        return tread_offset, ()

                    tread_verts = deepcopy(default_tread_verts)
                    tread_verts[-1].x = current_tread_run
                    return tread_offset, tread_verts

                return default_tread_offset, default_tread_verts

            # treads
            current_offset = V_(0, 0)
            for i in range(number_of_risers):
                last_vert_i = len(vertices) - 1
                tread_offset, tread_verts = get_tread_data(i)

                # Skip adding vertices/edges for zero-width treads
                if tread_verts:
                    current_tread_verts = [v + current_offset for v in tread_verts]
                    edges.extend(default_tread_edges + last_vert_i)
                    vertices.extend(current_tread_verts)

                current_offset += tread_offset

        if stair_type == "WOOD/STEEL":
            assert tread_depth is not None

            # full tread rectangle
            def get_tread_verts(size: Vector) -> list[Vector]:
                coords = ShapeBuilder.get_rectangle_coords(position=V_(0, -(tread_depth - tread_rise)), size=size)
                return [Vector(x) for x in coords]

            default_tread_verts = get_tread_verts(size=V_(tread_run + nosing_overlap, tread_depth))
            default_tread_offset = V_(tread_run + nosing_tread_gap, tread_rise)

            def get_tread_data(i):
                # Check if this is first or last tread with custom run
                current_tread_run = None
                if i == 0 and custom_first_last_tread_run[0] is not None:
                    current_tread_run = custom_first_last_tread_run[0]
                elif i == number_of_risers - 1 and custom_first_last_tread_run[1] is not None:
                    current_tread_run = custom_first_last_tread_run[1]

                if current_tread_run is not None:
                    tread_offset = default_tread_offset.copy()
                    tread_offset.x = current_tread_run + nosing_tread_gap

                    # Handle zero-width treads
                    if current_tread_run == 0:
                        return tread_offset, ()

                    tread_verts = get_tread_verts(size=V_(current_tread_run + nosing_overlap, tread_depth))
                    return tread_offset, tread_verts

                return default_tread_offset, default_tread_verts

            # each tread is a separate shape
            cur_offset = V_(0, 0)
            tread_index = 0

            for i in range(number_of_risers):
                tread_offset, tread_verts = get_tread_data(i)

                # Skip adding vertices/edges for zero-width treads
                if tread_verts:
                    cur_trade_shape = [v + cur_offset + nosing_overlap_offset for v in tread_verts]
                    vertices.extend(cur_trade_shape)

                    cur_vertex = tread_index * 4
                    verts_to_add = (
                        (cur_vertex, cur_vertex + 1),
                        (cur_vertex + 1, cur_vertex + 2),
                        (cur_vertex + 2, cur_vertex + 3),
                        (cur_vertex + 3, cur_vertex),
                    )
                    edges.extend(verts_to_add)
                    tread_index += 1

                cur_offset += tread_offset

        elif stair_type == "GENERIC":
            define_generic_stair_treads()

            # close the shape
            last_vert_i = len(vertices)
            vertices.append(vertices[-1] * V_(1, 0))
            edges.extend([(last_vert_i - 1, last_vert_i), (last_vert_i, 0)])

            # flip edges direction for ccw polygon winding order
            edges = [e[::-1] for e in edges]

        elif stair_type == "CONCRETE":
            define_generic_stair_treads()

            assert has_top_nib is not None
            assert top_slab_depth is not None
            assert base_slab_depth is not None
            assert tread_depth is not None

            # add the nibs
            # basically we define stair bottom line as a line at `tread_depth` distance
            # from the tread diagonal line
            # we're going it define that line, sample it and abrupt it in case it meets a slab
            # graph: https://www.desmos.com/calculator/bilmnti3cp
            tread_diagonal_dir = V_(tread_run, tread_rise).normalized()
            # td_vector is clockwise orthogonal vector
            td_vector = tread_diagonal_dir.yx * V_(1, -1) * tread_depth

            stair_tan = tread_rise / tread_run
            # s0 is just a sampled point from the bottom line
            # we stick to the third point as the first point
            # is affected by customized tread run
            s0 = V_(first_tread_run, tread_rise) + td_vector
            # comes from y = stair_tan * x + b
            b = s0.y - stair_tan * s0.x

            def get_point_on_2d_line(
                x: Union[float, None] = None,
                y: Union[float, None] = None,
            ) -> Vector:
                if x is not None and y is None:
                    y = stair_tan * x + b
                elif x is None and y is not None:
                    x = (y - b) / stair_tan
                else:
                    assert False
                return V_(x, y)

            # top nib
            last_vert = vertices[-1]
            last_vertex_i = len(vertices) - 1
            # NOTE: has_top_nib = False and top_slab_depth are different things
            if has_top_nib:
                vertices.append(last_vert + Vector((0, -top_slab_depth)))
                vertices.append(get_point_on_2d_line(y=last_vert.y - top_slab_depth))
                edges.append((last_vertex_i, last_vertex_i + 1))
                edges.append((last_vertex_i + 1, last_vertex_i + 2))
            else:
                new_vert = get_point_on_2d_line(last_vert.x)
                vertices.append(new_vert)
                edges.append((last_vertex_i, last_vertex_i + 1))

            top_nib_end = len(vertices) - 1

            # bottom nib
            start_vert = vertices[0]
            base_point = get_point_on_2d_line(x=start_vert.x)
            if base_point.y > -base_slab_depth:
                # stair doesn't meet the slab
                vertices.append(base_point)
                edges.append((len(vertices) - 1, 0))
                bottom_nib_end = len(vertices) - 1
            else:
                # slab overlaps stair
                vertices.append(get_point_on_2d_line(y=start_vert.y - base_slab_depth))
                vertices.append(start_vert + Vector((0, -base_slab_depth)))
                last_vertex_i = len(vertices) - 1
                edges.append((last_vertex_i, 0))
                edges.append((last_vertex_i - 1, last_vertex_i))
                bottom_nib_end = len(vertices) - 2

            # close the shape
            edges.append((top_nib_end, bottom_nib_end))

            # flip edges direction for ccw polygon winding order
            edges = [e[::-1] for e in edges]
        else:
            raise Exception(f"Unsupported stair type: {stair_type}")

        vertices = [v.to_3d().xzy for v in vertices]
        return (vertices, edges, faces)

    @classmethod
    def regenerate_filling_opening_body(cls, filling: ifcopenshell.entity_instance) -> Optional[bpy.types.Object]:
        """Regenerate only the mapped source used by ``filling``'s opening so
        it matches ``filling``'s current parametric dimensions.

        Returns the voided host Blender object so the caller can recut it,
        or ``None`` if ``filling`` has no opening to refresh or the host is
        an aggregate (no mesh data to recut against)."""
        from bonsai.bim.module.model.opening import FilledOpeningGenerator

        if not filling.FillsVoids:
            return None

        ifc_file = tool.Ifc.get()
        opening = filling.FillsVoids[0].RelatingOpeningElement
        voided_obj = tool.Ifc.get_object(opening.VoidsElements[0].RelatingBuildingElement)
        if voided_obj is None or voided_obj.data is None:
            return None

        old_representation = tool.Geometry.get_body_representation(opening)
        if old_representation is None:
            return voided_obj
        old_representation = tool.Geometry.resolve_mapped_representation(old_representation)

        ifcopenshell.api.geometry.unassign_representation(ifc_file, product=opening, representation=old_representation)

        filling_obj = tool.Ifc.get_object(filling)
        new_representation = FilledOpeningGenerator().generate_opening_from_filling(
            filling, filling_obj, voided_obj.dimensions[1]
        )

        for inverse in ifc_file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        ifcopenshell.api.geometry.remove_representation(ifc_file, representation=old_representation)

        return voided_obj

    @classmethod
    def regenerate_simple_opening_bodies(cls, element: ifcopenshell.entity_instance) -> set:
        """Regenerate every distinct mapped opening source within ``element``'s
        type-occurrence family so each one matches the family's current
        parametric dimensions.

        Most occurrences share a single mapped source — refreshing it once
        propagates to every filling via inverse-substitution. Some families,
        especially those imported from foreign authoring tools, fragment into
        several mapped sources for the same type; dedup is by source id so
        every distinct source gets one refresh. Returns the set of Blender
        objects whose host representation needs a viewport-level recut
        (callers handle the recut themselves)."""
        ifc_file = tool.Ifc.get()
        fillings = list(tool.Array.get_parametric_propagation_targets(element))

        voided_objs: set = set()
        seen_source_ids: set[int] = set()
        for filling in fillings:
            if not filling.FillsVoids:
                continue

            opening = filling.FillsVoids[0].RelatingOpeningElement
            voided_obj = tool.Ifc.get_object(opening.VoidsElements[0].RelatingBuildingElement)
            if voided_obj is not None:
                voided_objs.add(voided_obj)

            body = tool.Geometry.get_body_representation(opening)
            if body is None:
                continue
            source = tool.Geometry.resolve_mapped_representation(body)
            if source.id() in seen_source_ids:
                continue
            seen_source_ids.add(source.id())

            cls.regenerate_filling_opening_body(filling)

        return voided_objs

    @classmethod
    def update_simple_openings(cls, element: ifcopenshell.entity_instance) -> None:
        voided_objs = cls.regenerate_simple_opening_bodies(element)
        fillings = {e: tool.Ifc.get_object(e) for e in tool.Array.get_parametric_propagation_targets(element)}

        tool.Model.reload_body_representation(voided_objs)
        if fillings:
            with bpy.context.temp_override(selected_objects=list(fillings.values())):
                bpy.ops.bim.recalculate_fill()

    @classmethod
    def apply_ifc_material_changes(
        cls,
        elements: list[ifcopenshell.entity_instance],
        assigned_material: Optional[ifcopenshell.entity_instance] = None,
    ) -> None:
        """Update mesh blender materials for provided elements after material assignment/unassignment.

        `assigned_material` argument is there just to indicate whether we apply material changes
        after material assignment or material unassignment.
        """
        for element in elements:
            if not (obj := tool.Ifc.get_object(element)) or not (data := obj.data):
                continue
            representation = tool.Ifc.get().by_id(tool.Geometry.get_mesh_props(data).ifc_definition_id)
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                apply_openings=True,
            )

    @classmethod
    def get_occurrences_without_material_override(
        cls, element_type: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        occurrences = [
            e
            for e in ifcopenshell.util.element.get_types(element_type)
            if not tool.Geometry.has_material_style_override(e)
        ]
        return occurrences

    @classmethod
    def add_representation(cls, obj: bpy.types.Object, context: ifcopenshell.entity_instance) -> None:
        ifc_file = tool.Ifc.get()
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc_file,
            context=context,
            blender_object=obj,
            geometry=mesh,
            coordinate_offset=tool.Geometry.get_cartesian_point_offset(obj),
            total_items=tool.Geometry.get_total_representation_items(obj),
            should_force_faceted_brep=tool.Geometry.should_force_faceted_brep(),
            should_force_triangulation=tool.Geometry.should_force_triangulation(),
            should_generate_uvs=tool.Geometry.should_generate_uvs(obj),
            ifc_representation_class=None,
            profile_set_usage=None,
        )
        assert representation
        tool.Model.replace_object_ifc_representation(context, obj, representation)

    @classmethod
    def add_body_representation(cls, obj: bpy.types.Object) -> None:
        ifc_file = tool.Ifc.get()
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert body
        cls.add_representation(obj, body)

    @classmethod
    def auto_detect_annotation_fill_area(cls, obj: bpy.types.Object, mesh: bpy.types.Mesh) -> dict | None:
        result = cls.auto_detect_profiles(obj, mesh)
        fill_area = None
        if isinstance(result, dict) and (profile_def := result["profile_def"]):
            if profile_def.is_a("IfcArbitraryClosedProfileDef"):
                fill_area = result["ifc_file"].createIfcAnnotationFillArea(profile_def.OuterCurve)
            elif profile_def.is_a("IfcArbitraryProfileDefWithVoids"):
                fill_area = result["ifc_file"].createIfcAnnotationFillArea(
                    profile_def.OuterCurve, profile_def.InnerCurves
                )
            if fill_area:
                return {"ifc_file": result["ifc_file"], "annotation_fill_area": fill_area}

    @classmethod
    def auto_detect_profiles(
        cls,
        obj: bpy.types.Object,
        mesh: bpy.types.Mesh,
        position: Matrix | None = None,
        x_angle: Optional[float] = None,
    ) -> tuple | dict | None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()
        position_i = position.inverted()

        groups = {"IFCARCINDEX": [], "IFCCIRCLE": []}
        for i, group in enumerate(obj.vertex_groups):
            if "IFCARCINDEX" in group.name:
                groups["IFCARCINDEX"].append(i)
            elif "IFCCIRCLE" in group.name:
                groups["IFCCIRCLE"].append(i)

        bm = bmesh.new()
        bm.from_mesh(mesh)
        # Looser than auto_detect_curves' VTX_PRECISION: profiles must close into
        # a single loop, so nearly-coincident endpoints should snap together.
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD_TOLERANCE)
        bmesh.ops.delete(bm, geom=bm.faces, context="FACES_ONLY")

        # https://docs.blender.org/api/blender_python_api_2_63_8/bmesh.html#CustomDataAccess
        # This is how we access vertex groups via bmesh, apparently, it's not very intuitive
        deform_layer = bm.verts.layers.deform.active

        # Sanity check
        group_verts = {"IFCARCINDEX": {}, "IFCCIRCLE": {}}
        if deform_layer:
            for vert in bm.verts:
                vert_group_indices = tool.Blender.bmesh_get_vertex_groups(vert, deform_layer)
                is_circle = False
                for group_index in vert_group_indices:
                    group_type = "IFCARCINDEX" if group_index in groups["IFCARCINDEX"] else "IFCCIRCLE"
                    group_verts[group_type].setdefault(group_index, 0)
                    group_verts[group_type][group_index] += 1
                    if group_type == "IFCCIRCLE":
                        is_circle = True
                if is_circle:
                    pass  # Circles are allowed to be unclosed
                elif len(vert.link_edges) != 2:  # Unclosed loop or forked loop
                    return (False, "UNCLOSED_LOOP")

        for group_type, group_counts in group_verts.items():
            if group_type == "IFCARCINDEX":
                for group_count in group_counts.values():
                    if group_count != 3:  # Each arc needs 3 verts
                        return (False, "3POINT_ARC")
            elif group_type == "IFCCIRCLE":
                for group_count in group_counts.values():
                    if group_count != 2:  # Each circle needs 2 verts
                        return (False, "CIRCLE")

        loop_edges = list(bm.edges)

        # Create loops from edges
        loops: list[list[bmesh.types.BMEdge]] = []
        while loop_edges:
            edge = loop_edges.pop()
            loop = [edge]
            has_found_connected_edge = True
            while has_found_connected_edge:
                has_found_connected_edge = False
                for edge in loop_edges.copy():
                    edge_verts = set(edge.verts)
                    if edge_verts & set(loop[0].verts):
                        loop.insert(0, edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
                    elif edge_verts & set(loop[-1].verts):
                        loop.append(edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
            loops.append(loop)

        tmp = ifcopenshell.file(schema=tool.Ifc.get().schema)

        def is_in_group(v: bmesh.types.BMVert, group_name: str) -> bool:
            for group_index in groups[group_name]:
                if group_index in v[deform_layer]:
                    return True
            return False

        def get_group_index(v: bmesh.types.BMVert, group_name: str) -> Union[int, None]:
            for group_index in groups[group_name]:
                if group_index in v[deform_layer]:
                    return group_index

        # Convert all loops into IFC curves
        curves: list[ifcopenshell.entity_instance] = []
        for loop in loops:

            if len(loop) == 1 and all([is_in_group(v, "IFCCIRCLE") for v in loop[0].verts]):
                v1, v2 = loop[0].verts
                mid = v1.co.lerp(v2.co, 0.5)
                mid = ((position_i @ mid) / unit_scale).to_2d()
                v1 = ((position_i @ v1.co) / unit_scale).to_2d()
                radius = (mid - v1).length
                curves.append(
                    tmp.createIfcCircle(tmp.createIfcAxis2Placement2D(tmp.createIfcCartesianPoint(list(mid))), radius)
                )
            else:
                loop_verts: list[bmesh.types.BMVert] = []
                for i, edge in enumerate(loop):
                    if i == 0 and len(loop) == 1:
                        loop_verts.append(edge.verts[0])
                        loop_verts.append(edge.verts[1])
                    elif i == 0:
                        if edge.verts[0] in loop[i + 1].verts:
                            loop_verts.append(edge.verts[1])
                            loop_verts.append(edge.verts[0])
                        elif edge.verts[1] in loop[i + 1].verts:
                            loop_verts.append(edge.verts[0])
                            loop_verts.append(edge.verts[1])
                    else:
                        loop_verts.append(edge.other_vert(loop_verts[-1]))

                if is_closed := loop_verts[0] == loop_verts[-1]:
                    loop_verts.pop()

                    # Handle loop_verts possibly starting halfway through an arc
                    if deform_layer:
                        if gi := tool.Blender.bmesh_get_vertex_groups(loop_verts[0], deform_layer):
                            if not (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[1], deform_layer)):
                                loop_verts.insert(0, loop_verts.pop())
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (set(gi) & set(gi2)):
                                loop_verts.insert(0, loop_verts.pop())
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[2], deform_layer)):
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (set(gi) & set(gi2)):
                                loop_verts.insert(0, loop_verts.pop())

                if tmp.schema != "IFC2X3" and any([is_in_group(v, "IFCARCINDEX") for v in loop_verts]):
                    # We need to specify segments
                    coord_list = [list(((position_i @ v.co) / unit_scale).to_2d()) for v in loop_verts]
                    points = tmp.createIfcCartesianPointList2D(coord_list)
                    i = 0
                    segments = []
                    total_verts = len(loop_verts)
                    while i < total_verts:
                        v = loop_verts[i]
                        if (
                            (i + 1 != total_verts)
                            and (gi := tool.Blender.bmesh_get_vertex_groups(v, deform_layer))
                            and (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[i + 1], deform_layer))
                            and (set(gi) & set(gi2))
                        ):
                            segments.append(tmp.createIfcArcIndex([i + 1, i + 2, i + 3]))
                            i += 2
                        else:
                            segments.append(tmp.createIfcLineIndex([i + 1, i + 2]))
                            i += 1
                    if is_closed:
                        # Close the loop
                        last_segment_indices = list(segments[-1][0])
                        last_segment_indices[-1] = 1
                        segments[-1][0] = last_segment_indices
                    curves.append(tmp.createIfcIndexedPolyCurve(points, segments))
                elif tmp.schema == "IFC2X3":
                    points = [
                        tmp.createIfcCartesianPoint(list(((position_i @ v.co) / unit_scale).to_2d()))
                        for v in loop_verts
                    ]
                    if is_closed:
                        points.append(points[0])
                    curves.append(tmp.createIfcPolyline(points))
                else:  # Pure straight polyline, no segments required
                    coord_list = [list(((position_i @ v.co) / unit_scale).to_2d()) for v in loop_verts]
                    if x_angle:
                        coord_list = [(c[0], c[1] / cos(x_angle)) for c in coord_list]
                    if is_closed:
                        coord_list.append(coord_list[0])
                    points = tmp.createIfcCartesianPointList2D(coord_list)
                    curves.append(tmp.createIfcIndexedPolyCurve(points))

        # Sort IFC curves into either closed, or closed with void profile defs
        profile_defs: list[ifcopenshell.entity_instance] = []
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)

        # First convert to Shapely
        polygons = {}
        for curve in curves:
            geometry = ifcopenshell.geom.create_shape(settings, curve)
            assert isinstance(geometry, W.Triangulation)
            v = ifcopenshell.util.shape.get_vertices(geometry, is_2d=True)
            v = np.round(v, 4)  # Round to nearest 0.1mm, otherwise things like circles don't polygonise reliably
            edges = ifcopenshell.util.shape.get_edges(geometry)
            boundary_lines = [shapely.LineString([v[e[0]], v[e[1]]]) for e in edges]
            unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
            closed_polygons = shapely.polygonize(unioned_boundaries.geoms)
            for polygon in closed_polygons.geoms:
                polygons[curve] = polygon
                break

        # Check for contains properly (IFC doesn't allow common boundary points)
        outer_inner = {}
        inner_outer = {}
        for curve, polygon in polygons.items():
            for curve2, polygon2 in polygons.items():
                if curve == curve2:
                    continue
                if polygon.contains_properly(polygon2):
                    outer_inner.setdefault(curve, []).append(curve2)
                    inner_outer.setdefault(curve2, []).append(curve)

        # Odd-even rule for nested curves
        nested_level = {c: len(inner_outer[c]) if c in inner_outer else 0 for c in curves}
        for curve in sorted(curves, key=lambda c: nested_level[c]):
            level = nested_level[curve]
            if level % 2 == 0:
                if curve in outer_inner:
                    inners = [c for c in outer_inner[curve] if nested_level[c] == level + 1]
                    profile_defs.append(tmp.createIfcArbitraryProfileDefWithVoids("AREA", None, curve, inners))
                else:
                    profile_defs.append(tmp.createIfcArbitraryClosedProfileDef("AREA", None, curve))

        if (total_profile_defs := len(profile_defs)) == 0:
            return
        elif total_profile_defs == 1:
            profile_def = profile_defs[0]
        else:
            profile_def = tmp.createIfcCompositeProfileDef("AREA", None, profile_defs)
        return {"ifc_file": tmp, "profile_def": profile_def}

    @classmethod
    def auto_detect_curves(
        cls, obj: bpy.types.Object, mesh: bpy.types.Mesh, position: Matrix | None = None
    ) -> Union[tuple, dict]:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()
        position_i = position.inverted()
        assert isinstance(position_i, Matrix)

        groups = {"IFCARCINDEX": [], "IFCCIRCLE": []}
        for i, group in enumerate(obj.vertex_groups):
            if "IFCARCINDEX" in group.name:
                groups["IFCARCINDEX"].append(i)
            elif "IFCCIRCLE" in group.name:
                groups["IFCCIRCLE"].append(i)

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=VTX_PRECISION)
        bmesh.ops.delete(bm, geom=bm.faces, context="FACES_ONLY")

        # https://docs.blender.org/api/blender_python_api_2_63_8/bmesh.html#CustomDataAccess
        # This is how we access vertex groups via bmesh, apparently, it's not very intuitive
        deform_layer = bm.verts.layers.deform.active

        # Sanity check
        group_verts = {"IFCARCINDEX": {}, "IFCCIRCLE": {}}
        if deform_layer:
            for vert in bm.verts:
                vert_group_indices = tool.Blender.bmesh_get_vertex_groups(vert, deform_layer)
                for group_index in vert_group_indices:
                    group_type = "IFCARCINDEX" if group_index in groups["IFCARCINDEX"] else "IFCCIRCLE"
                    group_verts[group_type].setdefault(group_index, 0)
                    group_verts[group_type][group_index] += 1
                if len(vert.link_edges) > 2:  # Forked loop
                    return (False, "FORKED_LOOP")

        for group_type, group_counts in group_verts.items():
            if group_type == "IFCARCINDEX":
                for group_count in group_counts.values():
                    if group_count != 3:  # Each arc needs 3 verts
                        return (False, "3POINT_ARC")
            elif group_type == "IFCCIRCLE":
                for group_count in group_counts.values():
                    if group_count != 2:  # Each circle needs 2 verts
                        return (False, "CIRCLE")

        loop_edges = list(bm.edges)

        # Create loops from edges
        loops: list[list[bmesh.types.BMEdge]] = []
        while loop_edges:
            edge = loop_edges.pop()
            loop = [edge]
            has_found_connected_edge = True
            while has_found_connected_edge:
                has_found_connected_edge = False
                for edge in loop_edges.copy():
                    edge_verts = set(edge.verts)
                    if edge_verts & set(loop[0].verts):
                        loop.insert(0, edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
                    elif edge_verts & set(loop[-1].verts):
                        loop.append(edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
            loops.append(loop)

        tmp = ifcopenshell.file(schema=tool.Ifc.get().schema)

        def is_in_group(v: bmesh.types.BMVert, group_name: str) -> bool:
            for group_index in groups[group_name]:
                if group_index in v[deform_layer]:
                    return True
            return False

        def get_group_index(v, group_name):
            for group_index in groups[group_name]:
                if group_index in v[deform_layer]:
                    return group_index

        # Convert all loops into IFC curves
        curves = []
        for loop in loops:

            if len(loop) == 1 and all([is_in_group(v, "IFCCIRCLE") for v in loop[0].verts]):
                v1, v2 = loop[0].verts
                mid = v1.co.lerp(v2.co, 0.5)
                mid = ((position_i @ mid) / unit_scale).to_2d()
                v1 = ((position_i @ v1.co) / unit_scale).to_2d()
                radius = (mid - v1).length
                curves.append(
                    tmp.createIfcCircle(tmp.createIfcAxis2Placement2D(tmp.createIfcCartesianPoint(list(mid))), radius)
                )
            else:
                loop_verts: list[bmesh.types.BMVert] = []
                for i, edge in enumerate(loop):
                    if i == 0 and len(loop) == 1:
                        loop_verts.append(edge.verts[0])
                        loop_verts.append(edge.verts[1])
                    elif i == 0:
                        if edge.verts[0] in loop[i + 1].verts:
                            loop_verts.append(edge.verts[1])
                            loop_verts.append(edge.verts[0])
                        elif edge.verts[1] in loop[i + 1].verts:
                            loop_verts.append(edge.verts[0])
                            loop_verts.append(edge.verts[1])
                    else:
                        loop_verts.append(edge.other_vert(loop_verts[-1]))

                if is_closed := loop_verts[0] == loop_verts[-1]:
                    loop_verts.pop()

                    # Handle loop_verts possibly starting halfway through an arc
                    if deform_layer:
                        if gi := tool.Blender.bmesh_get_vertex_groups(loop_verts[0], deform_layer):
                            if not (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[1], deform_layer)):
                                loop_verts.insert(0, loop_verts.pop())
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (set(gi) & set(gi2)):
                                loop_verts.insert(0, loop_verts.pop())
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[2], deform_layer)):
                                loop_verts.insert(0, loop_verts.pop())
                            elif not (set(gi) & set(gi2)):
                                loop_verts.insert(0, loop_verts.pop())

                if tmp.schema != "IFC2X3" and any([is_in_group(v, "IFCARCINDEX") for v in loop_verts]):
                    # We need to specify segments
                    coord_list: list[list[float]] = [
                        list(((position_i @ v.co) / unit_scale).to_2d()) for v in loop_verts
                    ]
                    points = tmp.createIfcCartesianPointList2D(coord_list)
                    i = 0
                    segments = []
                    total_verts = len(loop_verts)
                    while i < total_verts:
                        v = loop_verts[i]
                        if (
                            (i + 1 != total_verts)
                            and (gi := tool.Blender.bmesh_get_vertex_groups(v, deform_layer))
                            and (gi2 := tool.Blender.bmesh_get_vertex_groups(loop_verts[i + 1], deform_layer))
                            and (set(gi) & set(gi2))
                        ):
                            segments.append(tmp.createIfcArcIndex([i + 1, i + 2, i + 3]))
                            i += 2
                        else:
                            segments.append(tmp.createIfcLineIndex([i + 1, i + 2]))
                            i += 1
                    if is_closed:
                        # Close the loop
                        last_segment_indices = list(segments[-1][0])
                        last_segment_indices[-1] = 1
                        segments[-1][0] = last_segment_indices
                    curves.append(tmp.createIfcIndexedPolyCurve(points, segments))
                elif tmp.schema == "IFC2X3":
                    points = [
                        tmp.createIfcCartesianPoint(list(((position_i @ v.co) / unit_scale).to_2d()))
                        for v in loop_verts
                    ]
                    if is_closed:
                        points.append(points[0])
                    curves.append(tmp.createIfcPolyline(points))
                else:  # Pure straight polyline, no segments required
                    coord_list = [list(((position_i @ v.co) / unit_scale).to_2d()) for v in loop_verts]
                    if is_closed:
                        coord_list.append(coord_list[0])
                    points = tmp.createIfcCartesianPointList2D(coord_list)
                    curves.append(tmp.createIfcIndexedPolyCurve(points))

        return {"ifc_file": tmp, "curves": curves}

    @classmethod
    def get_booleaned_obj(cls, obj: bpy.types.Object) -> Union[bpy.types.Object, None]:
        """Get boolean obj, return `None` if either it's not a tracked boolean
        or it's not referring to an object (e.g. potential boolean object)."""
        if obj.type != "MESH":
            return
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        return tool.Geometry.get_mesh_props(mesh).obj

    @classmethod
    def get_tracked_opening_type(cls, obj: bpy.types.Object) -> Union[Literal["OPENING", "BOOLEAN"], None]:
        """Get tracked opening type, return `None` if object is not a tracked opening."""
        props = cls.get_model_props()
        for opening in props.openings:
            if opening.obj == obj:
                return opening.name
        return None

    @classmethod
    def bm_sort_out_geom(
        cls, geom_data: list[Union[bmesh.types.BMVert, bmesh.types.BMEdge, bmesh.types.BMFace]]
    ) -> dict[str, Any]:
        geom_dict = {"verts": [], "edges": [], "faces": []}

        for el in geom_data:
            if isinstance(el, bmesh.types.BMVert):
                geom_dict["verts"].append(el)
            elif isinstance(el, bmesh.types.BMFace):
                geom_dict["faces"].append(el)
            else:
                geom_dict["edges"].append(el)
        return geom_dict

    @classmethod
    def add_filled_opening(cls, voided_obj: bpy.types.Object, filling_obj: bpy.types.Object) -> None:
        from bonsai.bim.module.model.opening import FilledOpeningGenerator

        FilledOpeningGenerator().generate(filling_obj, voided_obj)

    @classmethod
    def add_extrusion_position(cls, extrusion: ifcopenshell.entity_instance, position: Vector) -> None:
        ifc_file = tool.Ifc.get()
        builder = ShapeBuilder(ifc_file)
        new_position = builder.create_axis2_placement_3d(position)
        extrusion.Position = new_position

    @classmethod
    def reset_extrusion_position(cls, extrusion: ifcopenshell.entity_instance) -> None:
        ifc_file = extrusion.file

        if ifc_file.schema == "IFC2X3":
            # Position is not optional.
            extrusion.Position.Location.Coordinates = (0.0, 0.0, 0.0)
            return

        position = extrusion.Position
        if position is None:
            return
        extrusion.Position = None
        ifcopenshell.util.element.remove_deep2(ifc_file, position)

    @classmethod
    def get_existing_x_angle(cls, extrusion: ifcopenshell.entity_instance) -> float:
        """Signed slope of the extrusion's direction in the y-z plane (radians).

        Assumes extrusion directions lie in the y-z plane (LAYER2 wall and
        LAYER3 slab convention). For inverted extrusions (z ≤ 0), adds π to
        preserve angular continuity for callers consuming the angle via
        cos/sin."""
        x, y, z = extrusion.ExtrudedDirection.DirectionRatios
        vector = Vector((0, 1))
        x_angle = vector.angle_signed(Vector((y, z)))
        return x_angle if z > 0 else (x_angle + pi)

    @classmethod
    def create_axis_curve(cls, obj: bpy.types.Object, grid_axis: ifcopenshell.entity_instance) -> None:
        m = tool.Surveyor.get_absolute_matrix(obj)
        assert isinstance(obj.data, bpy.types.Mesh)
        points = [m @ np.array(v.co.to_4d()) for v in obj.data.vertices[0:2]]
        ifcopenshell.api.grid.create_axis_curve(
            tool.Ifc.get(), p1=np_to_3d(points[0]), p2=np_to_3d(points[1]), is_si=True, grid_axis=grid_axis
        )

    @classmethod
    def draw_material_ui_select(cls, layout: bpy.types.UILayout, material_id: str) -> None:
        material_id_int = int(material_id)
        if not material_id_int:
            return
        op = layout.operator("bim.material_ui_select", icon="ZOOM_SELECTED", text="")
        op.material_id = material_id_int

    @classmethod
    def get_slab_clipping_bmesh(cls, obj: bpy.types.Object) -> bmesh.types.BMesh | None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=radians(1), verts=bm.verts, edges=bm.edges)
        bm.faces.ensure_lookup_table()

        clipping_bm = bmesh.new()
        vertex_map = {}

        kept = 0
        for face in bm.faces:
            face.normal_update()
            normal = face.normal.to_4d()
            normal.w = 0
            world_normal_z = (obj.matrix_world @ normal).z
            if world_normal_z >= -0.5:
                continue
            kept += 1
            new_verts = []
            for vert in face.verts:
                if not (new_vert := vertex_map.get(vert.index, None)):
                    new_vert = clipping_bm.verts.new(obj.matrix_world @ vert.co / unit_scale)
                    vertex_map[vert.index] = new_vert
                new_verts.append(new_vert)
            clipping_bm.faces.new(new_verts)

        if not len(clipping_bm.faces):
            return

        bmesh.ops.recalc_face_normals(clipping_bm, faces=clipping_bm.faces)
        clipping_bm.faces.ensure_lookup_table()
        return clipping_bm  # clipping_bm is in project units

    @classmethod
    def clip_wall_to_slab(cls, wall: ifcopenshell.entity_instance, clipping_bm: bmesh.types.BMesh) -> None:
        matrix_i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement))
        bm = clipping_bm.copy()
        bmesh.ops.transform(bm, matrix=Matrix(matrix_i.tolist()), verts=bm.verts)

        bm.verts.ensure_lookup_table()
        zs = [v.co.z for v in bm.verts]
        min_z = min(zs)
        max_z = max(zs)

        ifc_file = tool.Ifc.get()
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)

        # Build one IfcPolygonalFaceSet clip solid per clipping face.
        # Each solid uses a rectangle on the slope plane rather than the exact face
        # footprint.  The original approach (exact footprint) caused a kissing-solid /
        # boundary-coincidence bug when the operator is called twice for a ridge roof: the
        # two slope solids share an exact ridge edge, and OCCT produces spurious extra
        # vertices.  Extending each solid slightly past the ridge (by margin) creates a
        # volumetric overlap instead of a kissing boundary — OCCT handles overlapping
        # DIFFERENCE operands correctly.
        margin = 1.0  # project units past the face edge — enough to ensure overlap at ridge
        operands = []
        for face in bm.faces:
            face.normal_update()
            normal = Vector(face.normal).normalized()

            # Orthonormal basis spanning the slope plane.
            ref = Vector((0, 0, 1)) if abs(normal.z) < 0.9 else Vector((1, 0, 0))
            tangent1 = normal.cross(ref).normalized()
            tangent2 = normal.cross(tangent1).normalized()

            centroid = sum((v.co for v in face.verts), Vector()) / len(face.verts)

            # Tight bounding rectangle in slope-plane coords, plus a small margin.
            t1_coords = [(v.co - centroid).dot(tangent1) for v in face.verts]
            t2_coords = [(v.co - centroid).dot(tangent2) for v in face.verts]
            half1 = max(abs(c) for c in t1_coords) + margin
            half2 = max(abs(c) for c in t2_coords) + margin

            # Rectangle on the slope plane, extruded upward in wall-local Z.
            clip_bm = bmesh.new()
            v0 = clip_bm.verts.new(centroid + half1 * tangent1 + half2 * tangent2)
            v1 = clip_bm.verts.new(centroid - half1 * tangent1 + half2 * tangent2)
            v2 = clip_bm.verts.new(centroid - half1 * tangent1 - half2 * tangent2)
            v3 = clip_bm.verts.new(centroid + half1 * tangent1 - half2 * tangent2)
            bottom_face = clip_bm.faces.new([v0, v1, v2, v3])
            result = bmesh.ops.extrude_face_region(clip_bm, geom=[bottom_face])
            top_verts = [e for e in result["geom"] if isinstance(e, bmesh.types.BMVert)]
            bmesh.ops.translate(clip_bm, verts=top_verts, vec=Vector((0, 0, max_z - min_z)))
            clip_bm.verts.ensure_lookup_table()

            clip_verts = [v.co for v in clip_bm.verts]
            clip_faces = [[v.index for v in f.verts] for f in clip_bm.faces]
            operand = builder.mesh(clip_verts, clip_faces)
            clip_bm.free()
            operands.append(operand)

        for extrusion in ifcopenshell.util.shape.get_base_extrusions(wall) or []:
            if extrusion.Position:
                position = ifcopenshell.util.placement.get_axis2placement(extrusion.Position)
            else:
                position = np.eye(4)

            direction = np.array(extrusion.ExtrudedDirection[0])
            direction /= np.linalg.norm(direction)
            direction = position @ np.append(direction, 0.0)

            if direction[2] <= 0 or position[2][3] > max_z:
                continue

            extrusion.Depth = max_z / direction[2]

            if operands:
                body_repr = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
                booleans = ifcopenshell.api.geometry.add_boolean(ifc_file, first_item=extrusion, second_items=operands)
                tool.Model.mark_manual_booleans(wall, booleans)

    @classmethod
    def connect_wall_to_slab(cls, wall: ifcopenshell.entity_instance, slab: ifcopenshell.entity_instance) -> None:
        ifcopenshell.api.geometry.connect_element(
            tool.Ifc.get(), relating_element=slab, related_element=wall, description="TOP"
        )

    @classmethod
    def get_epg_modifier(cls, obj: bpy.types.Object) -> Union[bpy.types.NodesModifier, None]:
        for m in obj.modifiers:
            if m.type == "NODES" and m.name.startswith("BBIM_EPG"):
                assert isinstance(m, bpy.types.NodesModifier)
                return m
        return None

    @classmethod
    def setup_external_nodes(
        cls, modifier: bpy.types.NodesModifier, external_nodes: bpy.types.GeometryNodeTree
    ) -> None:
        bbim_nodes = modifier.node_group

        if bbim_nodes is not None:
            # Just assign modifier to existing node group.
            assert isinstance(bbim_nodes, bpy.types.GeometryNodeTree)
            group_node = next(n for n in bbim_nodes.nodes if n.type == "GROUP")
            assert isinstance(group_node, bpy.types.GeometryNodeGroup)
            group_node.node_tree = external_nodes
            return

        # Create a new node group.
        bbim_nodes = bpy.data.node_groups.new(type="GeometryNodeTree", name="BBIM_EPG")
        modifier.node_group = bbim_nodes

        assert isinstance(bbim_nodes, bpy.types.GeometryNodeTree)
        bbim_nodes_interface = bbim_nodes.interface
        assert bbim_nodes_interface

        geometry_socket_2 = bbim_nodes_interface.new_socket(
            name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
        )
        geometry_socket_2.attribute_domain = "POINT"

        # Socket Geometry
        geometry_socket_3 = bbim_nodes_interface.new_socket(
            name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
        )
        geometry_socket_3.attribute_domain = "POINT"

        # Socket Socket
        socket_socket = bbim_nodes_interface.new_socket(name="Socket", in_out="INPUT", socket_type="NodeSocketGeometry")
        socket_socket.attribute_domain = "POINT"

        # Initialize bbim_epg nodes.
        # Node Group Input.
        group_input_1 = bbim_nodes.nodes.new("NodeGroupInput")
        assert isinstance(group_input_1, bpy.types.NodeGroupInput)
        group_input_1.name = "Group Input"
        # Node Group Output.
        group_output_1 = bbim_nodes.nodes.new("NodeGroupOutput")
        assert isinstance(group_output_1, bpy.types.NodeGroupOutput)
        group_output_1.name = "Group Output"
        group_output_1.is_active_output = True

        # Node Group.
        group = bbim_nodes.nodes.new("GeometryNodeGroup")
        assert isinstance(group, bpy.types.GeometryNodeGroup)
        group.name = "Group"
        group.node_tree = external_nodes

        # Set locations
        group_input_1.location = (-345.0525817871094, 65.80108642578125)
        group_output_1.location = (200.0, 0.0)
        group.location = (-83.36784362792969, 80.47976684570312)

        # Set dimensions
        group_input_1.width, group_input_1.height = 140.0, 100.0
        group_output_1.width, group_output_1.height = 140.0, 100.0
        group.width, group.height = 179.41021728515625, 100.0

        # Initialize bbim_epg links.
        # group.Geometry -> group_output_1.Geometry
        bbim_nodes.links.new(group.outputs[0], group_output_1.inputs[0])
        # group_input_1.Geometry -> group.Geometry
        bbim_nodes.links.new(group_input_1.outputs[0], group.inputs[0])

    @classmethod
    def setup_parametric_geometry(cls, obj: bpy.types.Object) -> None:
        props = cls.get_epg_props(obj)
        external_nodes = props.geo_nodes
        assert external_nodes

        if not (modifier := cls.get_epg_modifier(obj)):
            modifier = obj.modifiers.new(type="NODES", name="BBIM_EPG")
            assert isinstance(modifier, bpy.types.NodesModifier)
        modifier.show_viewport = True
        cls.setup_external_nodes(modifier, external_nodes)

    @classmethod
    def clean_up_parametric_geometry(cls, obj: bpy.types.Object) -> None:
        # Geo nodes are using modifier.
        modifier = tool.Model.get_epg_modifier(obj)
        if modifier is not None:
            node_tree = modifier.node_group
            assert node_tree
            bpy.data.node_groups.remove(node_tree)
            obj.modifiers.clear()

        # Sverchok are changing the mesh data to preview changes.
        # TODO: probably should use modifiers with nodes and temp mesh instead.
        active_representation = tool.Geometry.get_active_representation(obj)
        assert active_representation is not None
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=active_representation,
        )

    @classmethod
    def get_parametric_geometry_inputs(cls, modifier: bpy.types.NodesModifier) -> list[bpy.types.NodeSocket]:
        node_group = modifier.node_group
        assert isinstance(node_group, bpy.types.GeometryNodeTree)

        group_node = next(n for n in node_group.nodes if n.type == "GROUP")
        assert isinstance(group_node, bpy.types.GeometryNodeGroup)

        return [s for s in group_node.inputs if s.type != "GEOMETRY"]

    @classmethod
    def get_ifcsverchok_group_node(cls, node_tree: sverchok.node_tree.SverchCustomTree) -> SvGroupTreeNode:
        from sverchok.core.node_group import SvGroupTreeNode

        return next(n for n in node_tree.nodes if isinstance(n, SvGroupTreeNode) and n.label == "BBIM_EPG")

    @classmethod
    def get_ifcsverchok_shape_output(
        cls, node_tree: sverchok.node_tree.SverchCustomTree
    ) -> ifcsverchok.nodes.ifc.shape_builder.shape_output.SvSbShapeOutput:
        from ifcsverchok.nodes.ifc.shape_builder.shape_output import SvSbShapeOutput

        group_node = cls.get_ifcsverchok_group_node(node_tree)
        subtree = group_node.node_tree
        return next(n for n in subtree.nodes if isinstance(n, SvSbShapeOutput))

    @classmethod
    def update_mesh_from_sverchok(
        cls, obj: bpy.types.Object, node_tree: sverchok.node_tree.SverchCustomTree
    ) -> str | None:
        """
        :return: ``None`` if successful, otherwise error message.
        """
        import ifcsverchok.helper as helper

        output_node = cls.get_ifcsverchok_shape_output(node_tree)
        verts = helper.get_socket_value(output_node.outputs, "Vers", value_type="CONTAINER")
        edges = helper.get_socket_value(output_node.outputs, "Edgs", value_type="CONTAINER")
        faces = helper.get_socket_value(output_node.outputs, "Pols", value_type="CONTAINER")
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        mesh.clear_geometry()

        # `shade_flat=False`, because `from_pydata` is using method that doesn't support changing shading
        # during `Panel.draw` execution. We shade flat later ourselves.
        mesh.from_pydata(verts, edges, faces, shade_flat=False)

        def _name_convention_attribute_ensure(attributes, name, domain, data_type):
            try:
                attribute = attributes[name]
            except KeyError:
                return attributes.new(name, data_type, domain)
            if attribute.domain == domain and attribute.data_type == data_type:
                return attribute
            attributes.remove(attribute)
            return attributes.new(name, data_type, domain)

        sharp_faces = _name_convention_attribute_ensure(mesh.attributes, "sharp_face", "FACE", "BOOLEAN")
        assert isinstance(sharp_faces, bpy.types.BoolAttribute)
        data = sharp_faces.data
        ones = np.ones(len(data), dtype=bool)
        data.foreach_set("value", ones)

    @classmethod
    def align_objects(
        cls,
        reference_obj: bpy.types.Object,
        objs: Iterable[bpy.types.Object],
        align_type: Literal["CENTER", "POSITIVE", "NEGATIVE"],
    ) -> None:
        if align_type == "CENTER":
            point = reference_obj.matrix_world @ (Vector(reference_obj.bound_box[0]) + (reference_obj.dimensions / 2))
        elif align_type == "POSITIVE":
            point = reference_obj.matrix_world @ Vector(reference_obj.bound_box[6])
        elif align_type == "NEGATIVE":
            point = reference_obj.matrix_world @ Vector(reference_obj.bound_box[0])

        reference_x_axis = reference_obj.matrix_world.col[0].to_3d()
        reference_y_axis = reference_obj.matrix_world.col[1].to_3d()

        x_distances = cls.get_axis_distances(point, reference_x_axis, objs, align_type)
        y_distances = cls.get_axis_distances(point, reference_y_axis, objs, align_type)
        if abs(sum(x_distances)) < abs(sum(y_distances)):
            for i, obj in enumerate(objs):
                obj.matrix_world = Matrix.Translation(reference_x_axis * -x_distances[i]) @ obj.matrix_world
        else:
            for i, obj in enumerate(objs):
                obj.matrix_world = Matrix.Translation(reference_y_axis * -y_distances[i]) @ obj.matrix_world

    @classmethod
    def get_axis_distances(
        cls,
        point: Vector,
        axis: Vector,
        objs: Iterable[bpy.types.Object],
        align_type: Literal["CENTER", "POSITIVE", "NEGATIVE"],
    ) -> list[float]:
        results = []
        for obj in objs:
            if align_type == "CENTER":
                obj_point = obj.matrix_world @ (Vector(obj.bound_box[0]) + (obj.dimensions / 2))
            elif align_type == "POSITIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[6])
            elif align_type == "NEGATIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[0])
            results.append(mathutils.geometry.distance_point_to_plane(obj_point, point, axis))
        return results

    @classmethod
    def offset_wall(cls, wall: bpy.types.Object, baseline: Literal["EXTERIOR", "INTERIOR", "CENTER"]) -> None:
        element = tool.Ifc.get_entity(wall)
        usage = ifcopenshell.util.element.get_material(element)
        if usage is None or not usage.is_a("IfcMaterialLayerSetUsage"):
            return
        layer_set = usage.ForLayerSet
        if baseline == "CENTER":
            if usage.DirectionSense == "POSITIVE":
                usage.OffsetFromReferenceLine = -layer_set.TotalThickness / 2
            else:
                usage.OffsetFromReferenceLine = layer_set.TotalThickness / 2
        elif baseline == "INTERIOR":
            if usage.DirectionSense == "POSITIVE":
                usage.OffsetFromReferenceLine = -layer_set.TotalThickness
            else:
                usage.OffsetFromReferenceLine = 0.0
        elif baseline == "EXTERIOR":
            if usage.DirectionSense == "POSITIVE":
                usage.OffsetFromReferenceLine = 0.0
            else:
                usage.OffsetFromReferenceLine = layer_set.TotalThickness

    @classmethod
    def recreate_wall(cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
        # Curved fillet-corner walls own a hand-built banana body that
        # ``regenerate_wall_representation`` would flatten — it reads the axis
        # as a 2-point reference line and builds a straight extrusion. Rebuild
        # the curve in place instead: ``regenerate_fillet_corner_wall`` keeps
        # radius + placement from the pset / current ``ObjectPlacement`` while
        # picking up new thickness / height from the wall type, which is what
        # we want when a type-property edit triggered this call.
        if tool.Parametric.is_fillet_corner_wall(element):
            # Lazy import: ``tool.Model`` loads before ``bim/module/model`` at
            # addon enable; a module-level import would cycle.
            from bonsai.bim.module.model.wall import regenerate_fillet_corner_wall

            regenerate_fillet_corner_wall(element, obj)
            return
        rep = ifcopenshell.api.geometry.regenerate_wall_representation(tool.Ifc.get(), element)
        if rep is None:
            # Wall has no IfcMaterialLayerSet — layer-set rebuild not applicable.
            return
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=rep,
        )
        tool.Geometry.record_object_materials(obj)

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        matrix[:, 3] *= unit_scale
        obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(obj, matrix)
        tool.Geometry.record_object_position(obj)

    @classmethod
    def regenerate_wall(cls, obj: bpy.types.Object) -> None:
        """Rebuild a wall's body from current IFC state: extrusion + openings
        first, then re-clip to any surviving ``IfcRelConnectsElements(TOP)``
        slab. Safe on walls with no openings and no slab connection — both
        steps no-op against their preconditions."""
        element = tool.Ifc.get_entity(obj)
        if element is None:
            return
        cls.recreate_wall(element, obj)
        if cls.has_underside_connection(element):
            bonsai.core.model.regenerate_wall_to_underside(tool.Ifc, tool.Geometry, cls, [obj])

    @classmethod
    def recalculate_walls(cls, walls: list[bpy.types.Object]) -> None:
        queue: set[tuple[ifcopenshell.entity_instance, bpy.types.Object]] = set()
        for wall in walls:
            element = tool.Ifc.get_entity(wall)
            tool.Geometry.commit_placement_if_moved(wall)
            queue.add((element, wall))
            for rel in getattr(element, "ConnectedTo", []):
                obj = tool.Ifc.get_object(rel.RelatedElement)
                tool.Geometry.commit_placement_if_moved(obj)
                queue.add((rel.RelatedElement, obj))
            for rel in getattr(element, "ConnectedFrom", []):
                obj = tool.Ifc.get_object(rel.RelatingElement)
                tool.Geometry.commit_placement_if_moved(obj)
                queue.add((rel.RelatingElement, obj))

        # Sync filling and opening placements so subsequent wall recuts
        # operate on the up-to-date opening positions — a filling moved
        # along the wall's reference line otherwise stays cut at its old
        # spot.
        for element, wall in queue:
            if not wall:
                continue
            for rel in getattr(element, "HasOpenings", []) or []:
                opening = rel.RelatedOpeningElement
                for fill_rel in getattr(opening, "HasFillings", []) or []:
                    filling = fill_rel.RelatedBuildingElement
                    filling_obj = tool.Ifc.get_object(filling)
                    if filling_obj is None or not tool.Ifc.is_moved(filling_obj):
                        continue
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=filling_obj)
                    ifcopenshell.api.geometry.edit_object_placement(
                        tool.Ifc.get(), product=opening, matrix=filling_obj.matrix_world
                    )

        for element, wall in queue:
            if not wall:
                continue
            is_layer2_usage = tool.Model.get_usage_type(element) == "LAYER2"
            is_fillet_corner = tool.Parametric.is_fillet_corner_wall(element)
            if not (is_layer2_usage or is_fillet_corner):
                continue
            if is_layer2_usage:
                custom_offset = tool.Model.get_material_layer_custom_offset(element, wall)
                material = ifcopenshell.util.element.get_material(element)
                if material.is_a("IfcMaterialLayerSetUsage") and custom_offset is not None:
                    material.OffsetFromReferenceLine = custom_offset
            cls.recreate_wall(element, wall)

    @classmethod
    def regenerate_slab(cls, obj: bpy.types.Object) -> None:
        from bonsai.bim.module.model.slab import DumbSlabPlaner

        element = tool.Ifc.get_entity(obj)
        material_set = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        new_thickness = sum([l.LayerThickness for l in material_set.MaterialLayers])
        DumbSlabPlaner().change_thickness(element, new_thickness)

    @classmethod
    def regenerate_profile(cls, obj: bpy.types.Object) -> None:
        from bonsai.bim.module.model.profile import DumbProfileRecalculator

        DumbProfileRecalculator().recalculate([obj])

    @classmethod
    def run_ifcsverchok_graph_on_bonsai_file(cls, node_tree: sverchok.node_tree.SverchCustomTree) -> None:
        from ifcsverchok.ifcstore import SvIfcStore
        from sverchok.core.update_system import UpdateTree

        # We should be very careful and use bonsai file just for 1 graph update.
        # To avoid producing duplicated data in non-ephemeral file.
        SvIfcStore.use_bonsai_file = True
        try:
            # The ones below refresh asyncronously, so we're using different method to get results synchronously.
            # - bpy.ops.node.sverchok_update_context(force_mode=True)
            # - node_tree.force_update()
            # TODO: Ideally we should find shape output node and update only it's furtherest children.
            # Because user might have some nodes just floating around unused.
            # ` update_tree = UpdateTree.get(node_tree); update_tree.add_outdated(nodes)` can be used for this.
            UpdateTree.reset_tree(node_tree)
            nodes_to_update = UpdateTree.main_update(node_tree)
            # Consuming generator, which triggers the update.
            list(nodes_to_update)
        finally:
            SvIfcStore.use_bonsai_file = False

    @classmethod
    def create_bmesh_from_vertices(cls, vertices: list[Vector], is_closed: bool = False) -> bmesh.types.BMesh:
        bm = bmesh.new()

        new_verts = [bm.verts.new(v) for v in vertices]
        if is_closed:
            new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
            new_edges.append(
                bm.edges.new((new_verts[-1], new_verts[0]))
            )  # Add an edge between the last an first point to make it closed.
        else:
            new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]

        bm.verts.index_update()
        bm.edges.index_update()
        return bm
