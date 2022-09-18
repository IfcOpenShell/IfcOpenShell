# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import copy
import math
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import mathutils.geometry
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.root
import blenderbim.core.geometry
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
from ifcopenshell.api.material.data import Data as MaterialData
from math import pi, degrees
from mathutils import Vector, Matrix


def element_listener(element, obj):
    blenderbim.bim.handler.subscribe_to(obj, "mode", mode_callback)


def mode_callback(obj, data):
    for obj in set(bpy.context.selected_objects + [bpy.context.active_object]):
        if (
            not obj.data
            or not isinstance(obj.data, (bpy.types.Mesh, bpy.types.Curve, bpy.types.TextCurve))
            or not obj.BIMObjectProperties.ifc_definition_id
            or not bpy.context.scene.BIMProjectProperties.is_authoring
        ):
            return
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
        if not parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
            return
        if obj.mode == "EDIT":
            bpy.ops.bim.dynamically_void_product(obj=obj.name)
            IfcStore.edited_objs.add(obj)
            bm = bmesh.from_edit_mesh(obj.data)
            bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
            bmesh.update_edit_mesh(obj.data)
            bm.free()
        else:
            new_origin = obj.matrix_world @ Vector(obj.bound_box[0])
            obj.data.transform(
                Matrix.Translation(
                    (obj.matrix_world.inverted().to_quaternion() @ (obj.matrix_world.translation - new_origin))
                )
            )
            obj.matrix_world.translation = new_origin


class JoinWall(bpy.types.Operator):
    bl_idname = "bim.join_wall"
    bl_label = "Join Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Trim/Extend the selected walls to the last selected wall:
    'T' mode: Trim/Extend to a selected wall or 3D target
    'L' mode: Join two selected wall ends
    '' (empty) mode: Unjoin selected walls
    """
    join_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.BIMObjectProperties.ifc_definition_id]
        #for obj in selected_objs:
        #    bpy.ops.bim.dynamically_void_product(obj=obj.name)
        if not self.join_type:
            for obj in selected_objs:
                DumbWallJoiner().unjoin(obj)
            return {"FINISHED"}
        if not context.active_object:
            return {"FINISHED"}
        if len(selected_objs) == 1:
            DumbWallJoiner().join_E(context.active_object, context.scene.cursor.location)
            #IfcStore.edited_objs.add(context.active_object)
            return {"FINISHED"}
        if len(selected_objs) < 2:
            return {"FINISHED"}
        joiner = DumbWallJoiner()
        for obj in selected_objs:
            if obj == context.active_object:
                continue
            if self.join_type == "T":
                joiner.join_T(obj, context.active_object)
            elif self.join_type == "L":
                joiner.join_L(obj, context.active_object)
            IfcStore.edited_objs.add(obj)
        #if self.join_type != "T":
        #    IfcStore.edited_objs.add(context.active_object)
        return {"FINISHED"}


class AlignWall(bpy.types.Operator):
    bl_idname = "bim.align_wall"
    bl_label = "Align Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """ Align the selected walls to the last selected wall:
    'Ext.': align to the EXTERIOR face
    'C/L': align to wall CENTERLINE
    'Int.': align to the INTERIOR face"""
    align_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        selected_valid_objects = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        return context.active_object and len(selected_valid_objects) > 1

    def execute(self, context):
        selected_objects = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objects:
            if obj == context.active_object:
                continue
            aligner = DumbWallAligner(obj, context.active_object)
            if self.align_type == "CENTERLINE":
                aligner.align_centerline()
            elif self.align_type == "EXTERIOR":
                aligner.align_first_layer()
            elif self.align_type == "INTERIOR":
                aligner.align_last_layer()
            IfcStore.edited_objs.add(obj)
        return {"FINISHED"}


class FlipWall(bpy.types.Operator):
    bl_idname = "bim.flip_wall"
    bl_label = "Flip Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Switch the origin from the min XY corner to the max XY corner, and rotates the origin by 180"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objs:
            DumbWallFlipper(obj).flip()
            IfcStore.edited_objs.add(obj)
        return {"FINISHED"}


class SplitWall(bpy.types.Operator):
    bl_idname = "bim.split_wall"
    bl_label = "Split Wall"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Split selected wall into two walls in correspondence of Blender cursor. The cursor must be in the wall volume"
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.data and hasattr(o.data, "transform")]
        for obj in selected_objs:
            DumbWallJoiner().split(obj, context.scene.cursor.location)
        return {"FINISHED"}


class RecalculateWall(bpy.types.Operator):
    bl_idname = "bim.recalculate_wall"
    bl_label = "Recalculate Wall"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        DumbWallRecalculator().recalculate(context.selected_objects)
        return {"FINISHED"}


def recalculate_dumb_wall_origin(wall, new_origin=None):
    if new_origin is None:
        new_origin = wall.matrix_world @ Vector(wall.bound_box[0])
    if (wall.matrix_world.translation - new_origin).length < 0.001:
        return
    wall.data.transform(
        Matrix.Translation(
            (wall.matrix_world.inverted().to_quaternion() @ (wall.matrix_world.translation - new_origin))
        )
    )
    wall.matrix_world.translation = new_origin
    for child in wall.children:
        child.matrix_parent_inverse = wall.matrix_world.inverted()


class DumbWallFlipper:
    # A flip switches the origin from the min XY corner to the max XY corner, and rotates the origin by 180.
    def __init__(self, wall):
        self.wall = wall

    def flip(self):
        if (
            self.wall.matrix_world.translation - self.wall.matrix_world @ Vector(self.wall.bound_box[0])
        ).length < 0.001:
            recalculate_dumb_wall_origin(self.wall, self.wall.matrix_world @ Vector(self.wall.bound_box[7]))
            self.rotate_wall_180()
            bpy.context.view_layer.update()
            for child in self.wall.children:
                child.matrix_parent_inverse = self.wall.matrix_world.inverted()
        else:
            recalculate_dumb_wall_origin(self.wall)

    def rotate_wall_180(self):
        flip_matrix = Matrix.Rotation(pi, 4, "Z")
        self.wall.data.transform(flip_matrix)
        self.wall.rotation_euler.rotate(flip_matrix)


class DumbWallAligner:
    # An alignment shifts the origin of all walls to the closest point on the
    # local X axis of the reference wall. In addition, the Z rotation is copied.
    # Z translations are ignored for alignment.
    def __init__(self, wall, reference_wall):
        self.wall = wall
        self.reference_wall = reference_wall

    def align_centerline(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y
        reference_width = (Vector(self.reference_wall.bound_box[3]) - Vector(self.reference_wall.bound_box[0])).y

        if self.is_rotation_flipped():
            offset = self.wall.matrix_world.to_quaternion() @ Vector((0, -(reference_width / 2) - (width / 2), 0))
        else:
            offset = self.wall.matrix_world.to_quaternion() @ Vector((0, (reference_width / 2) - (width / 2), 0))

        self.align(
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0]),
            self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4]),
            offset,
        )

    def align_last_layer(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        if self.is_rotation_flipped():
            DumbWallFlipper(self.wall).flip()
            bpy.context.view_layer.update()
        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[3])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[7])

        wall_width = (Vector(self.wall.bound_box[3]) - Vector(self.wall.bound_box[0])).y

        offset = self.wall.matrix_world.to_quaternion() @ Vector((0, -wall_width, 0))
        self.align(start, end, offset)

    def align_first_layer(self):
        recalculate_dumb_wall_origin(self.wall)
        recalculate_dumb_wall_origin(self.reference_wall)
        self.align_rotation()

        if self.is_rotation_flipped():
            DumbWallFlipper(self.wall).flip()
            bpy.context.view_layer.update()

        start = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[0])
        end = self.reference_wall.matrix_world @ Vector(self.reference_wall.bound_box[4])

        self.align(start, end)

    def align(self, start, end, offset=None):
        if offset is None:
            offset = Vector((0, 0, 0))
        point, distance = mathutils.geometry.intersect_point_line(self.wall.matrix_world.translation, start, end)
        new_origin = point + offset
        self.wall.matrix_world.translation[0] = new_origin[0]
        self.wall.matrix_world.translation[1] = new_origin[1]

    def align_rotation(self):
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        if round(degrees(angle) % 360) in (0, 180):
            return
        elif angle > (pi / 2):
            self.wall.rotation_euler[2] -= pi - angle
        else:
            self.wall.rotation_euler[2] += angle
        bpy.context.view_layer.update()

    def is_rotation_flipped(self):
        reference = (self.reference_wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        wall = (self.wall.matrix_world.to_quaternion() @ Vector((1, 0, 0))).to_2d()
        angle = reference.angle_signed(wall)
        return round(degrees(angle) % 360) == 180


class DumbWallRecalculator:
    def recalculate(self, walls):
        queue = set()
        for wall in walls:
            element = tool.Ifc.get_entity(wall)
            queue.add((element, wall))
            for rel in getattr(element, "ConnectedTo", []):
                queue.add((rel.RelatedElement, tool.Ifc.get_object(rel.RelatedElement)))
            for rel in getattr(element, "ConnectedFrom", []):
                queue.add((rel.RelatingElement, tool.Ifc.get_object(rel.RelatingElement)))
        joiner = DumbWallJoiner()
        for element, wall in queue:
            if element.is_a("IfcWall") and wall:
                joiner.recreate_wall(element, wall)


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        self.file = IfcStore.get_file()
        self.layers = get_material_layer_parameters(self.relating_type)
        if not self.layers["thickness"]:
            return

        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.width = self.layers["thickness"]
        self.height = 3.0
        self.length = 1.0
        self.rotation = 0.0
        self.location = Vector((0, 0, 0))

        if self.has_sketch():
            return self.derive_from_sketch()
        return self.derive_from_cursor()

    def has_sketch(self):
        return (
            bpy.context.scene.grease_pencil
            and len(bpy.context.scene.grease_pencil.layers) == 1
            and bpy.context.scene.grease_pencil.layers[0].active_frame.strokes
        )

    def derive_from_sketch(self):
        objs = []
        strokes = []
        layer = bpy.context.scene.grease_pencil.layers[0]

        for stroke in layer.active_frame.strokes:
            if len(stroke.points) == 1:
                continue
            data = self.create_wall_from_2_points((stroke.points[0].co, stroke.points[-1].co))
            if data:
                strokes.append(data)
                objs.append(data["obj"])

        if len(objs) < 2:
            return objs

        l_joins = set()
        for stroke in strokes:
            if not stroke["obj"]:
                continue
            for stroke2 in strokes:
                if stroke2 == stroke or not stroke2["obj"]:
                    continue
                if self.has_nearby_ends(stroke, stroke2):
                    wall_join = "-JOIN-".join(sorted([stroke["obj"].name, stroke2["obj"].name]))
                    if wall_join not in l_joins:
                        l_joins.add(wall_join)
                        DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_L()
                elif self.has_end_near_stroke(stroke, stroke2):
                    DumbWallJoiner(stroke["obj"], stroke2["obj"]).join_T()
        bpy.context.scene.grease_pencil.layers.remove(layer)
        return objs

    def create_wall_from_2_points(self, coords):
        direction = coords[1] - coords[0]
        length = direction.length
        if length < 0.1:
            return
        data = {"coords": coords}

        # Round to nearest 50mm (yes, metric for now)
        self.length = 0.05 * round(length / 0.05)
        self.rotation = math.atan2(direction[1], direction[0])
        # Round to nearest 5 degrees
        nearest_degree = (math.pi / 180) * 5
        self.rotation = nearest_degree * round(self.rotation / nearest_degree)
        self.location = coords[0]
        data["obj"] = self.create_wall()
        return data

    def has_end_near_stroke(self, stroke, stroke2):
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][0], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][0]):
            return True
        point, distance = mathutils.geometry.intersect_point_line(stroke["coords"][1], *stroke2["coords"])
        if distance > 0 and distance < 1 and self.is_near(point, stroke["coords"][1]):
            return True

    def has_nearby_ends(self, stroke, stroke2):
        return (
            self.is_near(stroke["coords"][0], stroke2["coords"][0])
            or self.is_near(stroke["coords"][0], stroke2["coords"][1])
            or self.is_near(stroke["coords"][1], stroke2["coords"][0])
            or self.is_near(stroke["coords"][1], stroke2["coords"][1])
        )

    def is_near(self, point1, point2):
        return (point1 - point2).length < 0.1

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                local_location = sibling_obj.matrix_world.inverted() @ self.location
                try:
                    raycast = sibling_obj.closest_point_on_mesh(local_location, distance=0.01)
                except:
                    # If the mesh has no faces
                    raycast = [None]
                if not raycast[0]:
                    continue
                for face in sibling_obj.data.polygons:
                    if (
                        abs(face.normal.y) >= 0.75
                        and abs(mathutils.geometry.distance_point_to_plane(local_location, face.center, face.normal))
                        < 0.01
                    ):
                        # Rotate the wall in the direction of the face normal
                        normal = (sibling_obj.matrix_world.to_quaternion() @ face.normal).normalized()
                        self.rotation = math.atan2(normal[1], normal[0])
                        break
        return self.create_wall()

    def create_wall(self):
        ifc_class = self.get_relating_type_class(self.relating_type)
        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)
        obj.location = self.location
        obj.rotation_euler[2] = self.rotation
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)

        element = blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
            context=self.body_context,
        )
        if self.axis_context:
            representation = ifcopenshell.api.run(
                "geometry.add_axis_representation",
                tool.Ifc.get(),
                context=self.axis_context,
                axis=[
                    (
                        0.0,
                        0.0,
                    ),
                    (self.length, 0.0),
                ],
            )
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
            )
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            tool.Ifc.get(),
            context=self.body_context,
            thickness=self.layers["thickness"],
            offset=self.layers["offset"],
            length=self.length,
            height=self.height,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", tool.Ifc.get(), product=element, representation=representation
        )
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )
        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=self.relating_type)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.DumbLayer2"})
        MaterialData.load(self.file)
        obj.select_set(True)
        return obj

    def get_relating_type_class(self, relating_type):
        classes = ifcopenshell.util.type.get_applicable_entities(relating_type.is_a(), tool.Ifc.get().schema)
        return [c for c in classes if "StandardCase" not in c][0]


def calculate_quantities(usecase_path, ifc_file, settings):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    obj = settings["blender_object"]
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    parametric = ifcopenshell.util.element.get_psets(product).get("EPset_Parametric")
    if not parametric or "Engine" not in parametric or parametric["Engine"] != "BlenderBIM.DumbLayer2":
        return
    qto = ifcopenshell.api.run(
        "pset.add_qto", ifc_file, should_run_listeners=False, product=product, name="Qto_WallBaseQuantities"
    )
    length = obj.dimensions[0] / unit_scale
    width = obj.dimensions[1] / unit_scale
    height = obj.dimensions[2] / unit_scale

    bm_gross = bmesh.new()
    bm_gross.from_mesh(obj.data)
    bm_gross.faces.ensure_lookup_table()

    bm_net = bmesh.new()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_mesh = obj.evaluated_get(depsgraph).data
    bm_net.from_mesh(evaluated_mesh)
    bm_net.faces.ensure_lookup_table()

    gross_footprint_area = sum([f.calc_area() for f in bm_gross.faces if f.normal.z < -0.9])
    net_footprint_area = sum([f.calc_area() for f in bm_net.faces if f.normal.z < -0.9])
    gross_side_area = sum([f.calc_area() for f in bm_gross.faces if f.normal.y > 0.9])
    net_side_area = sum([f.calc_area() for f in bm_net.faces if f.normal.y > 0.9])
    gross_volume = bm_gross.calc_volume()
    net_volume = bm_net.calc_volume()
    bm_gross.free()
    bm_net.free()

    ifcopenshell.api.run(
        "pset.edit_qto",
        ifc_file,
        should_run_listeners=False,
        qto=qto,
        properties={
            "Length": round(length, 2),
            "Width": round(width, 2),
            "Height": round(height, 2),
            "GrossFootprintArea": round(gross_footprint_area, 2),
            "NetFootprintArea": round(net_footprint_area, 2),
            "GrossSideArea": round(gross_side_area, 2),
            "NetSideArea": round(net_side_area, 2),
            "GrossVolume": round(gross_volume, 2),
            "NetVolume": round(net_volume, 2),
        },
    )
    PsetData.load(ifc_file, obj.BIMObjectProperties.ifc_definition_id)


class DumbWallPlaner:
    def regenerate_from_layer(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        layer = settings["layer"]
        thickness = settings["attributes"].get("LayerThickness")
        if thickness is None:
            return
        for layer_set in layer.ToMaterialLayerSet:
            total_thickness = sum([l.LayerThickness for l in layer_set.MaterialLayers])
            if not total_thickness:
                continue
            for inverse in ifc_file.get_inverse(layer_set):
                if not inverse.is_a("IfcMaterialLayerSetUsage") or inverse.LayerSetDirection != "AXIS2":
                    continue
                if ifc_file.schema == "IFC2X3":
                    for rel in ifc_file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_thickness(element, thickness)

    def regenerate_from_type(self, usecase_path, ifc_file, settings):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        new_material = ifcopenshell.util.element.get_material(settings["relating_type"])
        if not new_material or not new_material.is_a("IfcMaterialLayerSet"):
            return
        new_thickness = sum([l.LayerThickness for l in new_material.MaterialLayers])
        material = ifcopenshell.util.element.get_material(settings["related_object"])

        relating_type = settings["relating_type"]
        if hasattr(relating_type, "HasPropertySets"):
            psets = relating_type.HasPropertySets
            if psets is not None:
                for pset in psets:
                    if hasattr(pset, "HasProperties"):
                        pset_props = pset.HasProperties
                        if pset_props is not None:
                            for prop in pset_props:
                                if prop.Name == "LayerSetDirection":
                                    if hasattr(prop, "NominalValue"):
                                        nominal_value = prop.NominalValue
                                        if hasattr(nominal_value, "wrappedValue"):
                                            if nominal_value.wrappedValue == "AXIS3":
                                                return

        if material and material.is_a("IfcMaterialLayerSetUsage") and material.LayerSetDirection == "AXIS2":
            self.change_thickness(settings["related_object"], new_thickness)

    def change_thickness(self, element, thickness):
        obj = IfcStore.get_element(element.id())
        if not obj:
            return

        delta_thickness = (thickness * self.unit_scale) - obj.dimensions.y
        if round(delta_thickness, 2) == 0:
            return

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)

        min_face, max_face = self.get_wall_end_faces(obj, bm)

        verts_to_move = []
        verts_to_move.extend(self.thicken_face(min_face, delta_thickness))
        verts_to_move.extend(self.thicken_face(max_face, delta_thickness))
        for vert_to_move in verts_to_move:
            vert_to_move["vert"].co += vert_to_move["vector"]

        bm.to_mesh(obj.data)
        obj.data.update()
        bm.free()
        IfcStore.edited_objs.add(obj)

    def thicken_face(self, face, delta_thickness):
        slide_magnitude = abs(delta_thickness)
        results = []
        for vert in face.verts:
            slide_vector = None
            for edge in vert.link_edges:
                other_vert = edge.verts[1] if edge.verts[0] == vert else edge.verts[0]
                if delta_thickness > 0:
                    potential_slide_vector = (vert.co - other_vert.co).normalized()
                    if potential_slide_vector.y < 0:
                        continue
                else:
                    potential_slide_vector = (other_vert.co - vert.co).normalized()
                    if potential_slide_vector.y > 0:
                        continue
                if abs(potential_slide_vector.x) > 0.9 or abs(potential_slide_vector.z) > 0.9:
                    continue
                slide_vector = potential_slide_vector
                break
            if not slide_vector:
                continue
            slide_vector *= slide_magnitude / abs(slide_vector.y)
            results.append({"vert": vert, "vector": slide_vector})
        return results

    # An end face is a quad that is on one end of the wall or the other. It must
    # have at least one vertex on either extreme X-axis, and a non-insignificant
    # X component of its face normal
    def get_wall_end_faces(self, wall, bm):
        min_face = None
        max_face = None
        min_x = min([v[0] for v in wall.bound_box])
        max_x = max([v[0] for v in wall.bound_box])
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            for v in f.verts:
                if v.co.x == min_x and abs(f.normal.x) > 0.1:
                    min_face = f
                elif v.co.x == max_x and abs(f.normal.x) > 0.1:
                    max_face = f
            if min_face and max_face:
                break
        return min_face, max_face


class DumbWallJoiner:
    def __init__(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "AXIS", "GRAPH_VIEW")
        self.body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        self.axis_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Axis", "GRAPH_VIEW")

    def unjoin(self, wall1):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATSTART")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")

        axis1 = self.get_wall_axis(wall1)
        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        self.recreate_wall(element1, wall1, axis, body)

    def split(self, wall1, target):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return
        axis1 = self.get_wall_axis(wall1)
        axis2 = copy.deepcopy(axis1)
        intersect, connection = mathutils.geometry.intersect_point_line(target.to_2d(), *axis1["reference"])
        if connection < 0 or connection > 1 or tool.Cad.is_x(connection, (0, 1)):
            return
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        wall2 = self.duplicate_wall(wall1)
        MaterialData.load(tool.Ifc.get())
        element2 = tool.Ifc.get_entity(wall2)

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type="ATEND")
        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element2, connection_type="ATSTART")

        axis1["reference"][1] = intersect
        axis2["reference"][0] = intersect
        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        self.recreate_wall(element2, wall2, axis2["reference"], axis2["reference"])

    def duplicate_wall(self, wall1):
        wall2 = wall1.copy()
        wall2.data = wall2.data.copy()
        wall1.users_collection[0].objects.link(wall2)
        blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=wall2)
        return wall2

    def join_L(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = self.get_wall_axis(wall1)
        axis2 = self.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        wall1_end = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"
        wall2_end = "ATEND" if tool.Cad.edge_percent(intersect, axis2["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            relating_element=element1,
            related_element=element2,
            relating_connection=wall1_end,
            related_connection=wall2_end,
        )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])
        self.recreate_wall(element2, wall2, axis2["reference"], axis2["reference"])

    def join_E(self, wall1, target):
        element1 = tool.Ifc.get_entity(wall1)
        if not element1:
            return

        axis1 = self.get_wall_axis(wall1)
        intersect, connection = mathutils.geometry.intersect_point_line(target.to_2d(), *axis1["reference"])
        connection = "ATEND" if connection > 0.5 else "ATSTART"

        ifcopenshell.api.run("geometry.disconnect_path", tool.Ifc.get(), element=element1, connection_type=connection)

        axis = copy.deepcopy(axis1["reference"])
        body = copy.deepcopy(axis1["reference"])
        axis[1 if connection == "ATEND" else 0] = intersect
        body[1 if connection == "ATEND" else 0] = intersect
        self.recreate_wall(element1, wall1, axis, body)

    def join_T(self, wall1, wall2):
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        axis1 = self.get_wall_axis(wall1)
        axis2 = self.get_wall_axis(wall2)
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        connection = "ATEND" if tool.Cad.edge_percent(intersect, axis1["reference"]) > 0.5 else "ATSTART"

        ifcopenshell.api.run(
            "geometry.connect_path",
            tool.Ifc.get(),
            related_element=element1,
            relating_element=element2,
            relating_connection="ATPATH",
            related_connection=connection,
        )

        self.recreate_wall(element1, wall1, axis1["reference"], axis1["reference"])

    def recreate_wall(self, element, obj, axis=None, body=None):
        if axis is None or body is None:
            axis = body = self.get_wall_axis(obj)["reference"]
        self.axis = copy.deepcopy(axis)
        self.body = copy.deepcopy(body)
        self.original_body = copy.deepcopy(body)
        height = self.get_height(tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id))
        self.clippings = []
        layers = get_material_layer_parameters(element)

        for rel in element.ConnectedTo:
            connection = rel.RelatingConnectionType
            other = tool.Ifc.get_object(rel.RelatedElement)
            if connection not in ["ATPATH", "NOTDEFINED"]:
                self.join(obj, other, connection, is_relating=True)
        for rel in element.ConnectedFrom:
            connection = rel.RelatedConnectionType
            other = tool.Ifc.get_object(rel.RelatingElement)
            if connection not in ["ATPATH", "NOTDEFINED"]:
                self.join(obj, other, connection, is_relating=False)

        new_matrix = copy.deepcopy(obj.matrix_world)
        new_matrix.col[3] = self.body[0].to_4d()
        new_matrix.invert()
        self.clippings = [new_matrix @ c for c in self.clippings]

        length = (self.body[1] - self.body[0]).length

        if self.axis_context:
            axis = [(new_matrix @ a.to_3d()).to_2d() for a in self.axis]
            new_axis = ifcopenshell.api.run(
                "geometry.add_axis_representation", tool.Ifc.get(), context=self.axis_context, axis=axis
            )
            old_axis = ifcopenshell.util.representation.get_representation(element, "Plan", "Axis", "GRAPH_VIEW")
            if old_axis:
                for inverse in tool.Ifc.get().get_inverse(old_axis):
                    ifcopenshell.util.element.replace_attribute(inverse, old_axis, new_axis)
                blenderbim.core.geometry.remove_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=old_axis
                )
            else:
                ifcopenshell.api.run(
                    "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_axis
                )

        new_body = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            tool.Ifc.get(),
            context=self.body_context,
            length=length,
            height=height,
            offset=layers["offset"],
            thickness=layers["thickness"],
            clippings=self.clippings,
        )

        old_body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if old_body:
            for inverse in tool.Ifc.get().get_inverse(old_body):
                ifcopenshell.util.element.replace_attribute(inverse, old_body, new_body)
            obj.data.BIMMeshProperties.ifc_definition_id = int(new_body.id())
            obj.data.name = f"{self.body_context.id()}/{new_body.id()}"
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_body)
        else:
            ifcopenshell.api.run(
                "geometry.assign_representation", tool.Ifc.get(), product=element, representation=new_body
            )

        obj.location[0], obj.location[1] = self.body[0]
        bpy.context.view_layer.update()
        if tool.Ifc.is_moved(obj):
            blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=new_body,
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
            should_sync_changes_first=False,
        )

    def create_matrix(self, p, x, y, z):
        return Matrix(
            (
                (x[0], y[0], z[0], p[0]),
                (x[1], y[1], z[1], p[1]),
                (x[2], y[2], z[2], p[2]),
                (0.0, 0.0, 0.0, 1.0),
            )
        )

    def get_wall_axis(self, obj, layers=None):
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

    def get_height(self, representation):
        height = 3.0
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                height = item.Depth / self.unit_scale
                break
            elif item.is_a("IfcBooleanClippingResult"):
                item = item.FirstOperand
            else:
                break
        return height

    def join(self, wall1, wall2, connection, is_relating=True):
        print('going to join', wall1, wall2, connection, is_relating)
        element1 = tool.Ifc.get_entity(wall1)
        element2 = tool.Ifc.get_entity(wall2)
        layers1 = get_material_layer_parameters(element1)
        layers2 = get_material_layer_parameters(element2)
        axis1 = self.get_wall_axis(wall1, layers1)
        axis2 = self.get_wall_axis(wall2, layers2)

        angle = tool.Cad.angle_edges(axis1["reference"], axis2["reference"], signed=False, degrees=True)
        if tool.Cad.is_x(angle, (0, 180)):
            return

        # Work out axis line
        intersect = tool.Cad.intersect_edges(axis1["reference"], axis2["reference"])
        if intersect:
            intersect, _ = intersect
        else:
            return
        self.axis[1 if connection == "ATEND" else 0] = intersect

        # Work out body extents
        intersect1, _ = tool.Cad.intersect_edges(axis1["base"], axis2["base"])
        intersect2, _ = tool.Cad.intersect_edges(axis1["base"], axis2["side"])
        intersect3, _ = tool.Cad.intersect_edges(axis1["side"], axis2["base"])
        intersect4, _ = tool.Cad.intersect_edges(axis1["side"], axis2["side"])

        intersect12 = intersect1.lerp(intersect2, 0.5)
        intersect34 = intersect3.lerp(intersect4, 0.5)

        if connection == "ATEND":
            if is_relating:
                base_target = tool.Cad.furthest_vector(axis1["base"][0], (intersect1, intersect2))
            else:
                base_target = tool.Cad.closest_vector(axis1["base"][0], (intersect1, intersect2))
            if tool.Cad.is_x(angle, (90, 270)):
                self.body[1] = tool.Cad.point_on_edge(base_target, axis1["reference"])
            else:
                if is_relating:
                    side_target = tool.Cad.furthest_vector(axis1["side"][0], (intersect3, intersect4))
                else:
                    side_target = tool.Cad.closest_vector(axis1["side"][0], (intersect3, intersect4))
                base_percent = tool.Cad.edge_percent(base_target, axis1["base"])
                side_percent = tool.Cad.edge_percent(side_target, axis1["side"])
                if base_percent > side_percent:
                    self.body[1] = tool.Cad.point_on_edge(base_target, axis1["reference"])
                    clip = side_target.to_3d()
                    x_axis = (side_target - base_target).normalized().to_3d()
                    y_axis = Vector((0, 0, 1))
                    z_axis = x_axis.cross(y_axis)
                    self.clippings.append(self.create_matrix(clip, x_axis, y_axis, z_axis))
                else:
                    self.body[1] = tool.Cad.point_on_edge(side_target, axis1["reference"])
                    clip = base_target.to_3d()
                    x_axis = (side_target - base_target).normalized().to_3d()
                    y_axis = Vector((0, 0, 1))
                    z_axis = x_axis.cross(y_axis)
                    self.clippings.append(self.create_matrix(clip, x_axis, y_axis, z_axis))
        else:
            if is_relating:
                base_target = tool.Cad.furthest_vector(axis1["base"][1], (intersect1, intersect2))
            else:
                base_target = tool.Cad.closest_vector(axis1["base"][1], (intersect1, intersect2))
            if tool.Cad.is_x(angle, (90, 270)):
                self.body[0] = tool.Cad.point_on_edge(base_target, axis1["reference"])
            else:
                if is_relating:
                    side_target = tool.Cad.furthest_vector(axis1["side"][1], (intersect3, intersect4))
                else:
                    side_target = tool.Cad.closest_vector(axis1["side"][1], (intersect3, intersect4))
                base_percent = tool.Cad.edge_percent(base_target, axis1["base"])
                side_percent = tool.Cad.edge_percent(side_target, axis1["side"])
                if base_percent < side_percent:
                    self.body[0] = tool.Cad.point_on_edge(base_target, axis1["reference"])
                    clip = side_target.to_3d()
                    x_axis = (side_target - base_target).normalized().to_3d()
                    y_axis = Vector((0, 0, 1))
                    z_axis = y_axis.cross(x_axis)
                    self.clippings.append(self.create_matrix(clip, x_axis, y_axis, z_axis))
                else:
                    self.body[0] = tool.Cad.point_on_edge(side_target, axis1["reference"])
                    clip = base_target.to_3d()
                    x_axis = (side_target - base_target).normalized().to_3d()
                    y_axis = Vector((0, 0, 1))
                    z_axis = y_axis.cross(x_axis)
                    self.clippings.append(self.create_matrix(clip, x_axis, y_axis, z_axis))


def get_material_layer_parameters(element):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    offset = 0.0
    thickness = 0.0
    material = ifcopenshell.util.element.get_material(element)
    if material:
        if material.is_a("IfcMaterialLayerSetUsage"):
            offset = material.OffsetFromReferenceLine / unit_scale
            material = material.ForLayerSet
        if material.is_a("IfcMaterialLayerSet"):
            thickness = sum([l.LayerThickness for l in material.MaterialLayers]) / unit_scale
    return {"thickness": thickness, "offset": offset}
