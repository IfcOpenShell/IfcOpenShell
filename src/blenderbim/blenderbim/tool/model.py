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
from mathutils import Matrix, Vector
from blenderbim.bim import import_ifc
from blenderbim.bim.module.geometry.helper import Helper


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
    def import_profile(cls, profile, obj=None, position=None):
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
        mesh.BIMMeshProperties.is_profile = True

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
        elif curve.is_a("IfcIndexedPolyCurve"):
            is_arc = False
            if curve.Segments:
                for segment in curve.Segments:
                    if len(segment[0]) == 3:  # IfcArcIndex
                        is_arc = True
                        local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment[0][0] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        cls.vertices.append(global_point)
                        local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment[0][1] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        cls.vertices.append(global_point)
                        cls.arcs.append([len(cls.vertices) - 2, len(cls.vertices) - 1])
                    else:
                        local_point = cls.convert_unit_to_si(curve.Points.CoordList[segment[0][0] - 1])
                        global_point = position @ Vector(local_point).to_3d()
                        cls.vertices.append(global_point)
                        if is_arc:
                            cls.arcs[-1].append(len(cls.vertices) - 1)
                            is_arc = False
            else:
                for local_point in curve.Points.CoordList:
                    global_point = position @ Vector(cls.convert_unit_to_si(local_point)).to_3d()
                    cls.vertices.append(global_point)
                # Curves without segments are cls closing
                del cls.vertices[-1]

            cls.edges.extend([(i, i + 1) for i in range(offset, len(cls.vertices))])
            cls.edges[-1] = (len(cls.vertices) - 1, offset)  # Close the loop
        elif curve.is_a("IfcCircle"):
            center = cls.convert_unit_to_si(
                Matrix(ifcopenshell.util.placement.get_axis2placement(curve.Position).tolist()).col[3].to_3d()
            )
            radius = cls.convert_unit_to_si(curve.Radius)
            cls.vertices.extend(
                [
                    position @ Vector((center[0], center[1] - curve.Radius, 0.0)),
                    position @ Vector((center[0], center[1] + curve.Radius, 0.0)),
                ]
            )
            cls.circles.append([offset, offset + 1])
            cls.edges.append((offset, offset + 1))

    @classmethod
    def import_rectangle(cls, obj, position, profile):
        if profile.Position:
            p_position = Matrix(ifcopenshell.util.placement.get_axis2placement(profile.Position).tolist())
            p_position[0][3] *= cls.unit_scale
            p_position[1][3] *= cls.unit_scale
            p_position[2][3] *= cls.unit_scale
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
    def regenerate_array(cls, parent, data):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj_stack = [parent]
        for array in data:
            child_i = 0
            existing_children = set(array["children"])
            total_existing_children = len(array["children"])
            children_elements = []
            children_objs = []
            for i in range(0, array["count"]):
                if i == 0:
                    continue
                offset = Vector((i * array["x"] * unit_scale, i * array["y"] * unit_scale, i * array["z"] * unit_scale))
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
                            product=child_element,
                            pset=tool.Ifc.get().by_id(child_pset["id"]),
                            properties={"Data": None},
                        )

                    new_matrix = obj.matrix_world.copy()
                    new_matrix.col[3] = (obj.matrix_world.col[3].to_3d() + offset).to_4d()
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
                    bpy.data.objects.remove(obj)
                # TODO: Not sufficient, refactor OverrideDeleteTrait

            bpy.context.view_layer.update()
