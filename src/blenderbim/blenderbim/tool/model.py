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

import bpy
import bmesh
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.core.geometry as geometry
from mathutils import Matrix, Vector
from blenderbim.bim import import_ifc
from blenderbim.bim.module.geometry.helper import Helper
from blenderbim.bim.module.model.data import AuthoringData, RailingData, RoofData, WindowData, DoorData
import collections
import json
import numpy as np


class Model(blenderbim.core.tool.Model):
    @classmethod
    def convert_si_to_unit(cls, value):
        if isinstance(value, (tuple, list)):
            return [v / cls.unit_scale for v in value]
        return value / cls.unit_scale

    @classmethod
    def convert_unit_to_si(cls, value):
        if isinstance(value, (tuple, list)):
            return [v * cls.unit_scale for v in value]
        return value * cls.unit_scale

    @classmethod
    def convert_data_to_project_units(cls, data, non_si_props=[]):
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
    def convert_data_to_si_units(cls, data, non_si_props=[]):
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
    def export_curve(cls, position, edge_indices, points=None):
        position_i = position.inverted()
        if len(edge_indices) == 2:
            diameter = edge_indices[0]
            p1 = cls.bm.verts[diameter[0]].co
            p2 = cls.bm.verts[diameter[1]].co
            center = cls.convert_si_to_unit(list(position_i @ p1.lerp(p2, 0.5)))
            radius = cls.convert_si_to_unit((p1 - p2).length / 2)
            return tool.Ifc.get().createIfcCircle(
                tool.Ifc.get().createIfcAxis2Placement2D(tool.Ifc.get().createIfcCartesianPoint(center[0:2])), radius
            )
        if tool.Ifc.get().schema == "IFC2X3":
            points = []
            for edge in edge_indices:
                local_point = (position_i @ Vector(cls.bm.verts[edge[0]].co)).to_2d()
                points.append(tool.Ifc.get().createIfcCartesianPoint(cls.convert_si_to_unit(local_point)))
            points.append(points[0])
            return tool.Ifc.get().createIfcPolyline(points)
        segments = []
        for segment in edge_indices:
            if len(segment) == 2:
                segments.append(tool.Ifc.get().createIfcLineIndex([i + 1 for i in segment]))
            elif len(segment) == 3:
                segments.append(tool.Ifc.get().createIfcArcIndex([i + 1 for i in segment]))
        return tool.Ifc.get().createIfcIndexedPolyCurve(cls.points, segments, False)

    @classmethod
    def export_points(cls, position, indices):
        position_i = position.inverted()
        points = []
        for point in indices:
            local_point = (position_i @ point).to_2d()
            points.append(cls.convert_si_to_unit(list(local_point)))
        return tool.Ifc.get().createIfcCartesianPointList2D(points)

    @classmethod
    def export_profile(cls, obj, position=None):
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
    def export_surface(cls, obj):
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
    def generate_occurrence_name(cls, element_type, ifc_class):
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
    def get_extrusion(cls, representation):
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
    def load_openings(cls, element, openings):
        if not openings:
            return []
        obj = tool.Ifc.get_object(element)
        ifc_import_settings = import_ifc.IfcImportSettings.factory()
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        openings = set(openings)
        openings -= ifc_importer.create_products(openings)
        for opening in openings or []:
            if tool.Ifc.get_object(opening):
                continue
            opening_obj = ifc_importer.create_product(opening)
            if obj:
                opening_obj.parent = obj
                opening_obj.matrix_parent_inverse = obj.matrix_world.inverted()
        for obj in ifc_importer.added_data.values():
            bpy.context.scene.collection.objects.link(obj)
        return ifc_importer.added_data.values()

    @classmethod
    def clear_scene_openings(cls):
        props = bpy.context.scene.BIMModelProperties
        has_deleted_opening = True
        while has_deleted_opening:
            has_deleted_opening = False
            for i, opening in enumerate(props.openings):
                if not opening.obj:
                    props.openings.remove(i)
                    has_deleted_opening = True

    @classmethod
    def get_material_layer_parameters(cls, element):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        offset = 0.0
        thickness = 0.0
        direction_sense = "POSITIVE"
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialLayerSetUsage"):
                offset = material.OffsetFromReferenceLine * unit_scale
                direction_sense = material.DirectionSense
                material = material.ForLayerSet
            if material.is_a("IfcMaterialLayerSet"):
                thickness = sum([l.LayerThickness for l in material.MaterialLayers]) * unit_scale
        if direction_sense == "NEGATIVE":
            thickness *= -1
            offset *= -1
        return {"thickness": thickness, "offset": offset, "direction_sense": direction_sense}

    @classmethod
    def get_manual_booleans(cls, element):
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not body:
            return []
        booleans = []
        items = list(body.Items)
        while items:
            item = items.pop()
            if item.is_a() == "IfcBooleanResult":
                booleans.append(item)
                items.append(item.FirstOperand)
            elif item.is_a("IfcBooleanClippingResult"):
                items.append(item.FirstOperand)
        return booleans

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
    def get_usage_type(cls, element):
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
            default_data = '[{"children": []}]'
            ifcopenshell.api.run(
                "pset.edit_pset",
                tool.Ifc.get(),
                pset=array_pset,
                properties={"Parent": element.GlobalId, "Data": default_data},
            )

            tool.Model.regenerate_array(obj, array_data)

            json_data = json.dumps(array_data)
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=array_pset, properties={"Data": json_data})

            for i in range(len(array_data)):
                tool.Blender.Modifier.Array.set_children_lock_state(element, i, True)
            tool.Blender.Modifier.Array.constrain_children_to_parent(element)

    @classmethod
    def regenerate_array(cls, parent_obj, data, keep_objs=False):
        tool.Blender.Modifier.Array.remove_constraints(tool.Ifc.get_entity(parent_obj))

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj_stack = [parent_obj]

        for array in data:
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
            if array["method"] == "DISTRIBUTE":
                divider = 1 if ((array["count"] - 1) == 0) else (array["count"] - 1)
                base_offset = Vector([array["x"] / divider, array["y"] / divider, array["z"] / divider]) * unit_scale
            else:
                base_offset = Vector([array["x"], array["y"], array["z"]]) * unit_scale
            for i in range(array["count"]):
                if i == 0:
                    continue
                offset = base_offset * i
                for obj in obj_stack:
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

                    child_psets = ifcopenshell.util.element.get_psets(child_element)
                    child_pset = child_psets.get("BBIM_Array")
                    if child_pset:
                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            tool.Ifc.get(),
                            pset=tool.Ifc.get().by_id(child_pset["id"]),
                            properties={"Data": None},
                        )

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

            removed_children = set(existing_children) - set(array["children"])
            for removed_child in removed_children:
                element = tool.Ifc.get().by_guid(removed_child)
                obj = tool.Ifc.get_object(element)
                if obj:
                    if keep_objs:
                        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
                        pset = tool.Ifc.get().by_id(pset["id"])
                        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)
                    else:
                        tool.Geometry.delete_ifc_object(obj)

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
    def get_element_matrix(cls, element, keep_local=False):
        placement = element.ObjectPlacement
        if keep_local:
            placement = ifcopenshell.util.placement.get_axis2placement(placement.RelativePlacement)
        else:
            placement = ifcopenshell.util.placement.get_local_placement(placement)
        return Matrix(placement)

    @classmethod
    def reload_body_representation(cls, obj_or_objects):
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
            blenderbim.core.geometry.switch_representation(
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
