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

import bpy
import json
import bmesh
import collections
import collections.abc
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import bonsai.core.geometry
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.core.geometry as geometry
from math import atan, degrees
from mathutils import Matrix, Vector
from copy import deepcopy
from functools import partial
from bonsai.bim import import_ifc
from bonsai.bim.module.geometry.helper import Helper
from bonsai.bim.module.model.data import AuthoringData, RailingData, RoofData, WindowData, DoorData
from bonsai.bim.module.model.opening import FilledOpeningGenerator
from ifcopenshell.util.shape_builder import V, ShapeBuilder
from typing import Optional, Union, TypeVar, Any, Iterable, Literal

T = TypeVar("T")


class Model(bonsai.core.tool.Model):
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
    def convert_data_to_project_units(cls, data: dict[str, Any], non_si_props: list[str] = []) -> dict[str, Any]:
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
    def convert_data_to_si_units(cls, data: dict[str, Any], non_si_props: list[str] = []) -> dict[str, Any]:
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for prop_name in data:
            if prop_name in non_si_props:
                continue
            prop_value = data[prop_name]
            if isinstance(prop_value, collections.abc.Iterable):
                data[prop_name] = [v * si_conversion for v in prop_value]
            else:
                data[prop_name] = prop_value * si_conversion
        return data

    @classmethod
    def export_curve(cls, position: Matrix, edge_indices: list[tuple[int, int]]) -> ifcopenshell.entity_instance:
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
    def export_profile(
        cls, obj: bpy.types.Object, position: Optional[Matrix] = None
    ) -> Union[ifcopenshell.entity_instance, None]:
        """Returns `None` in case if profile was invalid."""
        if position is None:
            position = Matrix()

        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        helper = Helper(tool.Ifc.get())
        indices = helper.auto_detect_arbitrary_profile_with_voids(obj, obj.data)

        if isinstance(indices, tuple) and indices[0] is False:  # Ugly
            return

        cls.bm = bmesh.new()
        cls.bm.from_mesh(obj.data)
        cls.bm.verts.ensure_lookup_table()
        cls.bm.edges.ensure_lookup_table()

        if indices["inner_curves"]:
            profile = tool.Ifc.get().createIfcArbitraryProfileDefWithVoids("AREA")
        else:
            profile = tool.Ifc.get().createIfcArbitraryClosedProfileDef("AREA")

        if tool.Ifc.get().schema != "IFC2X3":
            cls.points = cls.export_points(position, indices["points"])

        profile.OuterCurve = cls.export_curve(position, indices["profile"])
        if indices["inner_curves"]:
            results = []
            for inner_curve in indices["inner_curves"]:
                results.append(cls.export_curve(position, inner_curve))
            profile.InnerCurves = results

        cls.bm.free()
        return profile

    @classmethod
    def export_surface(cls, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
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

        helper = Helper(tool.Ifc.get())
        indices = helper.auto_detect_arbitrary_profile_with_voids(obj, obj.data)

        if isinstance(indices, tuple) and indices[0] is False:  # Ugly
            return

        cls.bm = bmesh.new()
        cls.bm.from_mesh(obj.data)
        cls.bm.verts.ensure_lookup_table()
        cls.bm.edges.ensure_lookup_table()

        surface = tool.Ifc.get().createIfcCurveBoundedPlane()
        surface.BasisSurface = tool.Ifc.get().createIfcPlane(
            tool.Ifc.get().createIfcAxis2Placement3D(
                tool.Ifc.get().createIfcCartesianPoint([o / cls.unit_scale for o in p1]),
                tool.Ifc.get().createIfcDirection([float(o) for o in z_axis]),
                tool.Ifc.get().createIfcDirection([float(o) for o in x_axis]),
            )
        )

        if tool.Ifc.get().schema != "IFC2X3":
            cls.points = cls.export_points(position, indices["points"])

        surface.OuterBoundary = cls.export_curve(position, indices["profile"])
        results = []
        for inner_curve in indices["inner_curves"]:
            results.append(cls.export_curve(position, inner_curve))
        surface.InnerBoundaries = results

        cls.bm.free()
        return surface

    @classmethod
    def generate_occurrence_name(cls, element_type: ifcopenshell.entity_instance, ifc_class: str) -> str:
        props = bpy.context.scene.BIMModelProperties
        if props.occurrence_name_style == "CLASS":
            return ifc_class[3:]
        elif props.occurrence_name_style == "TYPE":
            return element_type.Name or "Unnamed"
        elif props.occurrence_name_style == "CUSTOM":
            try:
                # Power users gonna power
                return eval(props.occurrence_name_function) or "Instance"
            except:
                return "Instance"

    @classmethod
    def get_extrusion(cls, representation: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """return first found IfcExtrudedAreaSolid"""
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanResult"):
                item = item.FirstOperand
            else:
                break

    @classmethod
    def import_axis(cls, axis, obj=None, position=None):
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        if position is None:
            position = Matrix()

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        if isinstance(axis, list):
            cls.vertices.extend(
                [
                    position @ Vector(cls.convert_unit_to_si(axis[0])).to_3d(),
                    position @ Vector(cls.convert_unit_to_si(axis[1])).to_3d(),
                ]
            )
            cls.edges.append([0, 1])
        else:
            cls.import_curve(obj, position, axis)

        mesh = bpy.data.meshes.new("Axis")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        mesh.BIMMeshProperties.subshape_type = "AXIS"

        if obj is None:
            obj = bpy.data.objects.new("Axis", mesh)
        else:
            obj.data = mesh

        return obj

    @classmethod
    def import_profile(cls, profile, obj=None, position=None):
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

        if profile.is_a("IfcArbitraryClosedProfileDef"):
            cls.import_curve(obj, position, profile.OuterCurve)
            if profile.is_a("IfcArbitraryProfileDefWithVoids"):
                for inner_curve in profile.InnerCurves:
                    cls.import_curve(obj, position, inner_curve)
        elif profile.is_a() == "IfcRectangleProfileDef":
            cls.import_rectangle(obj, position, profile)

        mesh = bpy.data.meshes.new("Profile")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        mesh.BIMMeshProperties.subshape_type = "PROFILE"

        if obj is None:
            obj = bpy.data.objects.new("Profile", mesh)
        else:
            obj.data = mesh

        for arc in cls.arcs:
            group = obj.vertex_groups.new(name="IFCARCINDEX")
            group.add(arc, 1, "REPLACE")

        for circle in cls.circles:
            group = obj.vertex_groups.new(name="IFCCIRCLE")
            group.add(circle, 1, "REPLACE")

        return obj

    @classmethod
    def import_surface(cls, surface, obj=None):
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        cls.vertices = []
        cls.edges = []
        cls.arcs = []
        cls.circles = []

        if surface.is_a("IfcCurveBoundedPlane"):
            position = Matrix(ifcopenshell.util.placement.get_axis2placement(surface.BasisSurface.Position).tolist())
            position.translation *= cls.unit_scale

            cls.import_curve(obj, position, surface.OuterBoundary)
            for inner_boundary in surface.InnerBoundaries:
                cls.import_curve(obj, position, inner_boundary)

        mesh = bpy.data.meshes.new("Surface")
        mesh.from_pydata(cls.vertices, cls.edges, [])
        mesh.BIMMeshProperties.subshape_type = "PROFILE"

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

    @classmethod
    def import_curve(cls, obj, position, curve):
        offset = len(cls.vertices)

        if curve.is_a("IfcPolyline"):
            total_points = len(curve.Points)
            last_index = len(curve.Points) - 1
            for i, point in enumerate(curve.Points):
                if i == last_index:
                    continue
                global_point = position @ Vector(cls.convert_unit_to_si(point.Coordinates)).to_3d()
                cls.vertices.append(global_point)
            cls.edges.extend([(i, i + 1) for i in range(offset, len(cls.vertices))])
            cls.edges[-1] = (len(cls.vertices) - 1, offset)  # Close the loop
        elif curve.is_a("IfcCompositeCurve"):
            # This is a first pass incomplete implementation only for simple polylines, and misses many details.
            for segment in curve.Segments:
                cls.import_curve(obj, position, segment.ParentCurve)
        elif curve.is_a("IfcIndexedPolyCurve"):
            is_arc = False
            is_closed = False
            if curve.Segments:
                for segment in curve.Segments:
                    if segment.is_a("IfcArcIndex"):
                        is_arc = True
                        local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment[0][0] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        cls.vertices.append(global_point)
                        local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment[0][1] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        cls.vertices.append(global_point)
                        cls.arcs.append([len(cls.vertices) - 2, len(cls.vertices) - 1])
                    else:
                        for segment_index in segment[0][0:-1]:
                            local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment_index - 1])
                            global_point = position @ Vector(local_point).to_3d()
                            cls.vertices.append(global_point)
                            if is_arc:
                                cls.arcs[-1].append(len(cls.vertices) - 1)
                                is_arc = False

                if curve.Segments[0][0][0] == curve.Segments[-1][0][-1]:
                    is_closed = True
            else:
                for local_point in curve.Points.CoordList:
                    global_point = position @ Vector(cls.convert_unit_to_si(local_point)).to_3d()
                    cls.vertices.append(global_point)

                if cls.vertices[offset] == cls.vertices[-1]:
                    is_closed = True
                    del cls.vertices[-1]

            cls.edges.extend([(i, i + 1) for i in range(offset, len(cls.vertices) - 1)])
            if is_closed:
                cls.edges.append([len(cls.vertices) - 1, offset])  # Close the loop
        elif curve.is_a("IfcCircle"):
            center = cls.convert_unit_to_si(
                Matrix(ifcopenshell.util.placement.get_axis2placement(curve.Position).tolist()).translation
            )
            radius = cls.convert_unit_to_si(curve.Radius)
            cls.vertices.extend(
                [
                    position @ Vector((center[0], center[1] - radius, 0.0)),
                    position @ Vector((center[0], center[1] + radius, 0.0)),
                ]
            )
            cls.circles.append([offset, offset + 1])
            cls.edges.append((offset, offset + 1))

    @classmethod
    def import_rectangle(cls, obj, position, profile):
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
    def load_openings(cls, openings):
        if not openings:
            return []
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        ifc_importer.create_generic_elements(set(openings))
        for opening_obj in ifc_importer.added_data.values():
            tool.Collector.assign(opening_obj, should_clean_users_collection=False)
        return ifc_importer.added_data.values()

    @classmethod
    def clear_scene_openings(cls) -> None:
        props = bpy.context.scene.BIMModelProperties
        has_deleted_opening = True
        while has_deleted_opening:
            has_deleted_opening = False
            for i, opening in enumerate(props.openings):
                if not opening.obj:
                    props.openings.remove(i)
                    has_deleted_opening = True

    @classmethod
    def get_material_layer_parameters(cls, element: ifcopenshell.entity_instance) -> dict[str, Any]:
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
        if direction_sense == "NEGATIVE":
            thickness *= -1
            offset *= -1
        return {
            "layer_set_direction": layer_set_direction,
            "thickness": thickness,
            "offset": offset,
            "direction_sense": direction_sense,
        }

    @classmethod
    def get_booleans(cls, element=None, representation=None) -> list[ifcopenshell.entity_instance]:
        if representation is None:
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
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
    def get_manual_booleans(cls, element, representation=None) -> list[ifcopenshell.entity_instance]:
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        if not pset:
            return []
        boolean_ids = json.loads(pset["Data"])
        if representation is None:
            representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if not representation:
                return []
        booleans = [b for b in cls.get_booleans(element, representation) if b.id() in boolean_ids]
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
            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Boolean")
            data = boolean_ids
        data = tool.Ifc.get().createIfcText(json.dumps(data))
        ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})

    @classmethod
    def unmark_manual_booleans(cls, element, boolean_ids):
        # NOTE: we use use boolean_ids instead of boolean entities
        # so it will be possible to unmark manual booleans after they already was deleted
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        if not pset:
            return
        data = set(json.loads(pset["Data"]))
        data -= set(boolean_ids)
        data = list(data)
        pset = tool.Ifc.get().by_id(pset["id"])
        if data:
            data = tool.Ifc.get().createIfcText(json.dumps(data))
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": data})
        else:
            ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)

    @classmethod
    def get_flow_segment_axis(cls, obj):
        z_values = [v[2] for v in obj.bound_box]
        return (obj.matrix_world @ Vector((0, 0, min(z_values))), obj.matrix_world @ Vector((0, 0, max(z_values))))

    @classmethod
    def get_flow_segment_profile(cls, element):
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
            elif material.is_a("IfcMaterialProfileSetUsage"):
                return "PROFILE"

    @classmethod
    def get_wall_axis(cls, obj, layers=None):
        x_values = [v[0] for v in obj.bound_box]
        min_x = min(x_values)
        max_x = max(x_values)
        axes = {}
        if layers:
            axes = {
                "base": [
                    (obj.matrix_world @ Vector((min_x, layers["offset"], 0.0))).to_2d(),
                    (obj.matrix_world @ Vector((max_x, layers["offset"], 0.0))).to_2d(),
                ],
                "side": [
                    (obj.matrix_world @ Vector((min_x, layers["offset"] + layers["thickness"], 0.0))).to_2d(),
                    (obj.matrix_world @ Vector((max_x, layers["offset"] + layers["thickness"], 0.0))).to_2d(),
                ],
            }
        axes["reference"] = [
            (obj.matrix_world @ Vector((min_x, 0.0, 0.0))).to_2d(),
            (obj.matrix_world @ Vector((max_x, 0.0, 0.0))).to_2d(),
        ]
        return axes

    @classmethod
    def handle_array_on_copied_element(cls, element, array_data=None):
        """if no `array_data` is provided then an array will be removed from the element"""

        if array_data is None:
            array_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not array_pset:
                return

            array_pset_data = array_pset["Data"]
            array_pset = tool.Ifc.get().by_id(array_pset["id"])
            ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=array_pset)

            # remove constraints
            obj = tool.Ifc.get_object(element)
            if not array_pset_data:  # skip array parents
                constraint = next((c for c in obj.constraints if c.type == "CHILD_OF"), None)
                if constraint:
                    matrix = obj.matrix_world.copy()
                    obj.constraints.remove(constraint)
                    # keep the matrix before the constraint
                    # otherwise object will jump to some previous position
                    obj.matrix_world = matrix
                tool.Blender.lock_transform(obj, False)

        else:
            obj = tool.Ifc.get_object(element)
            array_pset = tool.Pset.get_element_pset(element, "BBIM_Array")
            default_data = tool.Ifc.get().createIfcText('[{"children": []}]')
            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=array_pset,
                properties={"Parent": element.GlobalId, "Data": default_data},
            )

            tool.Model.regenerate_array(obj, array_data)

            json_data = tool.Ifc.get().createIfcText(json.dumps(array_data))
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=array_pset, properties={"Data": json_data})

            for i in range(len(array_data)):
                tool.Blender.Modifier.Array.set_children_lock_state(element, i, True)
            tool.Blender.Modifier.Array.constrain_children_to_parent(element)

    @classmethod
    def regenerate_array(cls, parent_obj, data, array_layers_to_apply=tuple()):
        """`array_layers_to_apply` - list of array layer indices to apply"""
        tool.Blender.Modifier.Array.remove_constraints(tool.Ifc.get_entity(parent_obj))

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj_stack = [parent_obj]

        for array_i, array in enumerate(data):
            # for `sync_children` we remove all previously generated children to regenerate them again
            # to assure they are in complete sync (psets, etc) with the array parent
            if array["sync_children"]:
                removed_children = set(array["children"])
                for removed_child in removed_children:
                    element = tool.Ifc.get().by_guid(removed_child)
                    obj = tool.Ifc.get_object(element)
                    if obj:
                        tool.Geometry.delete_ifc_object(obj)
                array["children"].clear()

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

            for i in range(array["count"]):
                if i == 0:
                    continue
                offset = base_offset * i

                for obj in obj_stack:
                    # get currently proccesed array element and it's object
                    if child_i >= total_existing_children:
                        child_obj = tool.Spatial.duplicate_object_and_data(obj)
                        child_element = tool.Spatial.run_root_copy_class(obj=child_obj)
                    else:
                        global_id = array["children"][child_i]
                        try:
                            child_element = tool.Ifc.get().by_guid(global_id)
                            child_obj = tool.Ifc.get_object(child_element)
                            assert child_obj
                        except:
                            child_obj = tool.Spatial.duplicate_object_and_data(obj)
                            child_element = tool.Spatial.run_root_copy_class(obj=child_obj)

                    # add child pset
                    child_pset = tool.Pset.get_element_pset(child_element, "BBIM_Array")
                    if child_pset:
                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            tool.Ifc.get(),
                            pset=child_pset,
                            properties={"Data": None},
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
                element = tool.Ifc.get().by_guid(removed_child)
                obj = tool.Ifc.get_object(element)
                if obj:
                    tool.Geometry.delete_ifc_object(obj)

            if array_i in array_layers_to_apply:
                for child_element in children_elements:
                    pset = tool.Pset.get_element_pset(child_element, "BBIM_Array")
                    ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=child_element, pset=pset)

                array["children"] = []
                array["count"] = 1

            bpy.context.view_layer.update()

    @classmethod
    def replace_object_ifc_representation(cls, ifc_context, obj, new_representation):
        ifc_file = tool.Ifc.get()
        ifc_element = tool.Ifc.get_entity(obj)
        old_representation = ifcopenshell.util.representation.get_representation(
            ifc_element, ifc_context.ContextType, ifc_context.ContextIdentifier, ifc_context.TargetView
        )

        if old_representation:
            old_representation = tool.Geometry.resolve_mapped_representation(old_representation)
            for inverse in ifc_file.get_inverse(old_representation):
                ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)
            ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=old_representation)
        else:
            ifcopenshell.api.run(
                "geometry.assign_representation", ifc_file, product=ifc_element, representation=new_representation
            )
        geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=new_representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

    @classmethod
    def update_thumbnail_for_element(cls, element, refresh=False):
        if bpy.app.background:
            return

        from PIL import Image, ImageDraw

        obj = tool.Ifc.get_object(element)
        if not obj:
            return  # Nothing to process

        if not refresh and element.id() in AuthoringData.type_thumbnails:
            return  # Already processed

        obj.asset_generate_preview()
        while not obj.preview:
            pass

        # if object has .data we can use default blender .asset_generate_preview()
        if not obj.data:
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

                is_horizontal = False
                if element.is_a("IfcSlabType"):
                    is_horizontal = True

                parametric = ifcopenshell.util.element.get_psets(element).get("EPset_Parametric")
                if parametric:
                    layer_set_direction = parametric.get("LayerSetDirection", None)
                    if layer_set_direction == "AXIS2":
                        is_horizontal = False
                    elif layer_set_direction == "AXIS3":
                        is_horizontal = True

                if is_horizontal:
                    width, height = height, width

                x_offset = (size / 2) - (width / 2)
                y_offset = (size / 2) - (height / 2)
                draw.rectangle([x_offset, y_offset, width + x_offset, height + y_offset], outline="white", width=5)
                current_thickness = 0
                del thicknesses[-1]
                for thickness in thicknesses:
                    current_thickness += thickness
                    if element.is_a("IfcSlabType"):
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
    def get_modeling_bbim_pset_data(cls, object, pset_name):
        """get modelling BBIM pset data (eg, BBIM_Roof) and loads it's `Data` as json to `data_dict`"""
        element = tool.Ifc.get_entity(object)
        if not element:
            return
        psets = ifcopenshell.util.element.get_psets(element)
        pset_data = psets.get(pset_name, None)
        if not pset_data:
            return
        pset_data["data_dict"] = json.loads(pset_data.get("Data", "[]") or "[]")
        return pset_data

    @classmethod
    def edit_element_placement(cls, element, matrix):
        """Useful for moving objects like ports or openings -
        the method will ensure it will be moved in blender scene too if it exists"""
        obj = tool.Ifc.get_object(element)
        if obj:
            obj.matrix_world = matrix
            return
        tool.Ifc.run("geometry.edit_object_placement", product=element, matrix=matrix, is_si=True)

    @classmethod
    def sync_object_ifc_position(cls, obj):
        """make sure IFC position will be in sync with the Blender object position, if object was moved in Blender"""
        if tool.Ifc.is_moved(obj):
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

    @classmethod
    def get_element_matrix(cls, element, keep_local=False):
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
            body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=body,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )

    @classmethod
    def is_parametric_roof_active(cls):
        return (RoofData.is_loaded or not RoofData.load()) and RoofData.data["pset_data"]

    @classmethod
    def is_parametric_railing_active(cls):
        return (RailingData.is_loaded or not RailingData.load()) and RailingData.data["pset_data"]

    @classmethod
    def is_parametric_window_active(cls):
        return (WindowData.is_loaded or not WindowData.load()) and WindowData.data["pset_data"]

    @classmethod
    def is_parametric_door_active(cls):
        return (DoorData.is_loaded or not DoorData.load()) and DoorData.data["pset_data"]

    @classmethod
    def get_active_stair_calculated_params(cls, pset_data=None):
        props = bpy.context.active_object.BIMStairProperties

        if props.is_editing:
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            number_of_treads = props.number_of_treads
            height = props.height / si_conversion
            tread_run = props.tread_run / si_conversion
            first_tread_run = props.custom_first_last_tread_run[0] / si_conversion
            last_tread_run = props.custom_first_last_tread_run[1] / si_conversion
            nosing_length = props.nosing_length / si_conversion
        else:
            number_of_treads = pset_data["number_of_treads"]
            height = pset_data["height"]
            tread_run = pset_data["tread_run"]
            # use .get to not break the old .ifc models
            custom_first_last_tread_run = pset_data.get("custom_first_last_tread_run", (0, 0))
            first_tread_run, last_tread_run = custom_first_last_tread_run
            nosing_length = pset_data.get("nosing_length", 0)

        calculated_params = {}
        number_of_rises = number_of_treads + 1
        calculated_params["Number of Risers"] = number_of_rises
        calculated_params["Tread Rise"] = round(height / number_of_rises, 5)

        # calculate stair length
        n_default_tread_runs = number_of_rises
        length = 0
        if first_tread_run != 0:
            n_default_tread_runs -= 1
            length += first_tread_run
        if last_tread_run != 0:
            n_default_tread_runs -= 1
            if n_default_tread_runs >= 0:
                length += last_tread_run
        length += tread_run * max(n_default_tread_runs, 0)
        # nosing overlaps
        # are not part of the tread run
        # so they don't affect the stair length
        # except the first tread's nosing
        if nosing_length > 0:  # nosing overlaps
            length += nosing_length
        if nosing_length < 0:  # tread gaps
            length += abs(nosing_length) * number_of_treads
        calculated_params["Length"] = round(length, 5)
        pitch = height / length
        pitch_formatted = str(round(pitch * 100, 1)) + " % / " + str(round(degrees(atan(pitch)), 1)) + " deg"
        calculated_params["Pitch"] = str(pitch_formatted)

        return calculated_params

    @classmethod
    def generate_stair_2d_profile(
        cls,
        number_of_treads,
        height,
        width,
        tread_run,
        stair_type,
        # WOOD/STEEL CONCRETE STAIR ARGUMENTS
        tread_depth=None,
        # CONCRETE STAIR ARGUMENTS
        has_top_nib=None,
        top_slab_depth=None,
        base_slab_depth=None,
        custom_first_last_tread_run=(0, 0),
        nosing_length=0,
        # CONCRETE GENERIC STAIR ARGUMENTS
        nosing_depth=0,
    ):
        """returns a tuple of stair profile data: (vertices, edges, faces)"""
        vertices = []
        edges = []
        faces = []

        number_of_risers = number_of_treads + 1
        tread_rise = height / number_of_risers
        custom_tread_run = any(run != 0 for run in custom_first_last_tread_run)
        nosing_overlap = max(nosing_length, 0)
        nosing_tread_gap = -min(nosing_length, 0)
        nosing_overlap_offset = -V(nosing_overlap, 0)

        def define_generic_stair_treads():
            vertices.append(Vector([0, 0]))
            nonlocal nosing_depth, nosing_overlap
            # avoid weird geometry
            nosing_depth = min(nosing_depth, tread_rise)
            nosing_overlap = min(nosing_overlap, tread_run)

            default_tread_edges = np.array(((0, 1), (1, 2)))
            # horizontal tread line
            if nosing_overlap == 0:
                default_tread_verts = (V(0, tread_rise), V(tread_run, tread_rise))
            elif nosing_depth == 0:
                default_tread_verts = (V(-nosing_overlap, tread_rise), V(tread_run, tread_rise))
            else:  # nosing_overlap > 0 nosing_depth > 0
                # kind of L shape
                default_tread_verts = (
                    V(0, tread_rise - nosing_depth),
                    V(-nosing_overlap, tread_rise - nosing_depth),
                    V(-nosing_overlap, tread_rise),
                    V(tread_run, tread_rise),
                )
                add_edges = ((2, 3), (3, 4))
                default_tread_edges = np.concatenate((default_tread_edges, add_edges))
            default_tread_offset = Vector([tread_run, tread_rise])

            def get_tread_data(i):
                if custom_tread_run:
                    current_tread_run = None
                    if i == 0:
                        current_tread_run = custom_first_last_tread_run[0]
                    elif i == number_of_risers - 1:
                        current_tread_run = custom_first_last_tread_run[1]

                    if current_tread_run:
                        tread_offset = default_tread_offset.copy()
                        tread_offset.x = current_tread_run
                        tread_verts = deepcopy(default_tread_verts)
                        tread_verts[-1].x = current_tread_run
                        return tread_offset, tread_verts
                return default_tread_offset, default_tread_verts

            # treads
            current_offset = V(0, 0)
            for i in range(number_of_risers):
                last_vert_i = len(vertices) - 1
                tread_offset, tread_verts = get_tread_data(i)
                current_tread_verts = [v + current_offset for v in tread_verts]
                edges.extend(default_tread_edges + last_vert_i)
                vertices.extend(current_tread_verts)
                current_offset += tread_offset

        if stair_type == "WOOD/STEEL":
            builder = ShapeBuilder(None)
            # full tread rectangle
            get_tread_verts = partial(builder.get_rectangle_coords, position=V(0, -(tread_depth - tread_rise)))
            default_tread_verts = get_tread_verts(size=V(tread_run + nosing_overlap, tread_depth))
            default_tread_offset = V(tread_run + nosing_tread_gap, tread_rise)

            def get_tread_data(i):
                if custom_tread_run:
                    current_tread_run = None
                    if i == 0 and custom_first_last_tread_run[0] != 0:
                        current_tread_run = custom_first_last_tread_run[0]
                    elif i == number_of_risers - 1 and custom_first_last_tread_run[1] != 0:
                        current_tread_run = custom_first_last_tread_run[1]

                    if current_tread_run:
                        tread_offset = default_tread_offset.copy()
                        tread_offset.x = current_tread_run + nosing_tread_gap
                        tread_verts = get_tread_verts(size=V(current_tread_run + nosing_overlap, tread_depth))
                        return tread_offset, tread_verts
                return default_tread_offset, default_tread_verts

            # each tread is a separate shape
            cur_offset = V(0, 0)
            for i in range(number_of_risers):
                tread_offset, tread_verts = get_tread_data(i)
                cur_trade_shape = [v + cur_offset + nosing_overlap_offset for v in tread_verts]
                vertices.extend(cur_trade_shape)

                cur_vertex = i * 4
                verts_to_add = (
                    (cur_vertex, cur_vertex + 1),
                    (cur_vertex + 1, cur_vertex + 2),
                    (cur_vertex + 2, cur_vertex + 3),
                    (cur_vertex + 3, cur_vertex),
                )
                edges.extend(verts_to_add)
                cur_offset += tread_offset

        elif stair_type == "GENERIC":
            define_generic_stair_treads()

            # close the shape
            last_vert_i = len(vertices)
            vertices.append(vertices[-1] * V(1, 0))
            edges.extend([(last_vert_i - 1, last_vert_i), (last_vert_i, 0)])

            # flip edges direction for ccw polygon winding order
            edges = [e[::-1] for e in edges]

        elif stair_type == "CONCRETE":
            define_generic_stair_treads()

            # add the nibs
            # basically we define stair bottom line as a line at `tread_depth` distance
            # from the tread diagonal line
            # we're going it define that line, sample it and abrupt it in case it meets a slab
            # graph: https://www.desmos.com/calculator/bilmnti3cp
            tread_diagonal_dir = V(tread_run, tread_rise).normalized()
            # td_vector is clockwise orthogonal vector
            td_vector = tread_diagonal_dir.yx * V(1, -1) * tread_depth

            stair_tan = tread_rise / tread_run
            # s0 is just a sampled point from the bottom line
            # we stick to the third point as the first point
            # is affected by customized tread run
            s0 = V(custom_first_last_tread_run[0] or tread_run, tread_rise) + td_vector
            # comes from y = stair_tan * x + b
            b = s0.y - stair_tan * s0.x

            def get_point_on_2d_line(x=None, y=None):
                if y is None:
                    y = stair_tan * x + b
                elif x is None:
                    x = (y - b) / stair_tan
                return V(x, y)

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

        vertices = (v.to_3d().xzy for v in vertices)
        return (vertices, edges, faces)

    @classmethod
    def update_simple_openings(cls, element: ifcopenshell.entity_instance) -> None:
        ifc_file = tool.Ifc.get()
        fillings = {e: tool.Ifc.get_object(e) for e in tool.Ifc.get_all_element_occurrences(element)}

        voided_objs = set()
        has_replaced_opening_representation = False
        for filling in fillings:
            if not filling.FillsVoids:
                continue

            opening = filling.FillsVoids[0].RelatingOpeningElement
            voided_obj = tool.Ifc.get_object(opening.VoidsElements[0].RelatingBuildingElement)
            voided_objs.add(voided_obj)

            # We assume all occurrences of the same element type (e.g. a window)
            # will use openings of the same thickness.
            # Generator we use by default will create a really thick opening representation
            # to make sure it will fit for walls with different thickness.
            if has_replaced_opening_representation:
                continue

            old_representation = ifcopenshell.util.representation.get_representation(
                opening, "Model", "Body", "MODEL_VIEW"
            )
            old_representation = tool.Geometry.resolve_mapped_representation(old_representation)
            ifcopenshell.api.run(
                "geometry.unassign_representation", ifc_file, product=opening, representation=old_representation
            )

            new_representation = FilledOpeningGenerator().generate_opening_from_filling(
                filling, fillings[filling], voided_obj.dimensions[1]
            )

            for inverse in ifc_file.get_inverse(old_representation):
                ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

            ifcopenshell.api.run("geometry.remove_representation", ifc_file, representation=old_representation)

            has_replaced_opening_representation = True

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

        if assigned_material:
            # NOTE: currently only IfcMaterials are supported
            # for anyone else we just switch representation.
            if not assigned_material.is_a("IfcMaterial"):
                tool.Geometry.reload_representation([tool.Ifc.get_object(e) for e in elements])
                return

        # Since different elements can share meshes (e.g. occurrences without openings)
        # we need to make sure not to process them multiple times.
        meshes_users: dict[bpy.types.Mesh, set[bpy.types.Object]] = dict()
        for obj in bpy.data.objects:
            if not obj.data:
                continue
            meshes_users.setdefault(obj.data, set()).add(obj)

        objects: set[bpy.types.Object] = set()
        for element in elements:
            obj: bpy.types.Object = tool.Ifc.get_object(element)
            if not obj or not obj.data:
                continue
            objects.add(obj)

        meshes: set[bpy.types.Mesh] = {obj.data for obj in objects}

        for mesh in meshes:
            mesh_users = meshes_users[mesh]

            if not mesh_users.issubset(objects):
                # It's unsafe to make changes to the mesh
                # as it's used by objects unrelated to the current change.
                # E.g. material with a style was assigned to a particular occurrence
                # and this change shouldn't be applied to other occurrences and type.
                objs_to_reload = mesh_users.intersection(objects)
                for obj in objs_to_reload:
                    tool.Geometry._reload_representation(obj)
                continue

            obj = next(iter(mesh_users))
            element = tool.Ifc.get_entity(obj)
            assert element  # Type checker.
            own_material = next(iter(ifcopenshell.util.element.get_materials(element, should_inherit=False)), None)
            inherited_mstyle = tool.Geometry.get_inherited_material_style(element)

            if assigned_material:
                if own_material:
                    ms2 = tool.Material.get_style(own_material)
                    ms1 = inherited_mstyle
                else:
                    ms1 = None
                    ms2 = inherited_mstyle

                cls.replace_material_style(mesh, obj, ms1, ms2)
                tool.Geometry.record_object_materials(obj)

            else:  # Material unnassignment.
                if not tool.Geometry.has_geometry_without_styles(mesh):
                    tool.Geometry._reload_representation(obj)
                    continue

                if not inherited_mstyle:
                    continue

                cls.replace_material_style(mesh, obj, None, inherited_mstyle)
                tool.Geometry.record_object_materials(obj)

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
    def replace_material_style(
        cls,
        mesh: bpy.types.Mesh,
        obj: bpy.types.Object,
        mstyle1: Union[ifcopenshell.entity_instance, None],
        mstyle2: Union[ifcopenshell.entity_instance, None],
    ) -> None:
        if mstyle1 == mstyle2:
            return

        # Get Blender materials.
        mbstyle1, mbstyle2 = None, None
        if mstyle1:
            mbstyle1 = tool.Ifc.get_object(mstyle1)
            assert isinstance(mbstyle1, bpy.types.Material)
        if mstyle2:
            mbstyle2 = tool.Ifc.get_object(mstyle2)
            assert isinstance(mbstyle2, bpy.types.Material)

        # Copy data to the list as mesh.materials doesn't allow to search for None.
        materials: list[Union[bpy.types.Material, None]] = mesh.materials[:]
        # Material style is overridden by representation item, nothing to change.
        if mesh.materials and mbstyle1 not in materials:
            return

        i1 = None
        if mbstyle1 is None:
            if not materials:
                mesh.materials.append(None)
                i1 = 0
            else:
                i1 = materials.index(None)
        else:
            rep = tool.Geometry.get_active_representation(obj)
            assert rep  # Type checker.
            rep_styles = tool.Geometry.get_representation_styles(rep)
            if mbstyle1 in rep_styles:
                tool.Geometry._reload_representation(obj)
                return
            else:
                i1 = materials.index(mbstyle1)

        if mbstyle2 in materials:
            i2 = materials.index(mbstyle2)
            # Reassign faces.
            buffer = np.empty(len(mesh.polygons), dtype=np.int32)
            mesh.polygons.foreach_get("material_index", buffer)
            buffer[buffer == i1] = i2
            mesh.polygons.foreach_set("material_index", buffer)

            mesh.materials.pop(index=i1)
        else:
            mesh.materials[i1] = mbstyle2
