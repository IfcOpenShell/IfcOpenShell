# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import mathutils
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.type
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.aggregate
import bonsai.core.type
import bonsai.core.geometry
import bonsai.core.spatial
from . import wall, slab, profile, mep
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model.data import AuthoringData
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
import json
from typing import Any, Union, Optional


class EnableAddType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_add_type"
    bl_label = "Enable Add Type"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        bpy.context.scene.BIMModelProperties.is_adding_type = True


class DisableAddType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_add_type"
    bl_label = "Disable Add Type"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        bpy.context.scene.BIMModelProperties.is_adding_type = False


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}


class AddDefaultType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_default_type"
    bl_label = "Add Default Type"
    bl_options = {"REGISTER", "UNDO"}
    ifc_element_type: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        ifc_file = tool.Ifc.get()
        props.type_class = self.ifc_element_type
        if self.ifc_element_type == "IfcWallType":
            if ifc_file.schema == "IFC2X3":
                props.type_predefined_type = "STANDARD"
            else:
                props.type_predefined_type = "SOLIDWALL"
            props.type_template = "LAYERSET_AXIS2"
        elif self.ifc_element_type == "IfcSlabType":
            props.type_predefined_type = "FLOOR"
            props.type_template = "LAYERSET_AXIS3"
        elif self.ifc_element_type == "IfcDoorType":
            props.type_predefined_type = "DOOR"
            props.type_template = "DOOR"
        elif self.ifc_element_type == "IfcWindowType":
            props.type_predefined_type = "WINDOW"
            props.type_template = "WINDOW"
        elif self.ifc_element_type == "IfcColumnType":
            props.type_predefined_type = "COLUMN"
            props.type_template = "PROFILESET"
        elif self.ifc_element_type == "IfcBeamType":
            props.type_predefined_type = "BEAM"
            props.type_template = "PROFILESET"
        elif self.ifc_element_type == "IfcDuctSegmentType":
            props.type_predefined_type = "RIGIDSEGMENT"
            props.type_template = "FLOW_SEGMENT_RECTANGULAR"
        elif self.ifc_element_type == "IfcPipeSegmentType":
            props.type_predefined_type = "RIGIDSEGMENT"
            props.type_template = "FLOW_SEGMENT_CIRCULAR"
        bpy.ops.bim.add_type()


class AddConstrTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_constr_type_instance"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Type Instance to the model"
    relating_type_id: bpy.props.IntProperty()
    from_invoke: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        relating_type_id = self.relating_type_id or props.relating_type_id

        if not relating_type_id:
            return {"FINISHED"}

        # Check relating_type_id enum_items since it's possible
        # that we're adding e.g. IfcRoofType being in a Slab Tool
        # and roof type id won't be present in the relating_type_id enum.
        if self.from_invoke and str(self.relating_type_id) in AuthoringData.data["relating_type_id"]:
            props.relating_type_id = str(self.relating_type_id)

        self.container = None
        self.container_obj = None
        if container := tool.Root.get_default_container():
            self.container = container
            self.container_obj = tool.Ifc.get_object(container)

        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        ifc_class = relating_type.is_a()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, tool.Ifc.get().schema)[0]
        material = ifcopenshell.util.element.get_material(relating_type)

        if material and material.is_a("IfcMaterialProfileSet"):
            if obj := profile.DumbProfileGenerator(relating_type).generate():
                tool.Blender.select_and_activate_single_object(context, obj)
                if relating_type.is_a("IfcFlowSegmentType"):
                    self.set_flow_segment_rl(obj)
                    mep.MEPGenerator(relating_type).setup_ports(obj)
                return {"FINISHED"}
        elif material and material.is_a("IfcMaterialLayerSet"):
            if self.generate_layered_element(ifc_class, relating_type):
                tool.Blender.select_and_activate_single_object(context, context.selected_objects[-1])
                return {"FINISHED"}

        building_obj = None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object
            building_element = tool.Ifc.get_entity(building_obj)

        # A cube
        verts = [
            Vector((-1, -1, -1)),
            Vector((-1, -1, 1)),
            Vector((-1, 1, -1)),
            Vector((-1, 1, 1)),
            Vector((1, -1, -1)),
            Vector((1, -1, 1)),
            Vector((1, 1, -1)),
            Vector((1, 1, 1)),
        ]
        edges = []
        faces = [
            [0, 1, 3, 2],
            [2, 3, 7, 6],
            [6, 7, 5, 4],
            [4, 5, 1, 0],
            [2, 6, 4, 0],
            [7, 3, 1, 5],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(relating_type, instance_class), mesh)

        obj.location = context.scene.cursor.location

        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        tool.Blender.remove_data_block(mesh)  # Remove "Instance" mesh

        mesh_data = obj.data
        element = tool.Ifc.get_entity(obj)
        bonsai.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)
        if obj.data != mesh_data:  # remove orphaned mesh from "bim.assign_class"
            tool.Blender.remove_data_block(mesh_data)

        # Update required as core.type.assign_type may change obj.data
        # TODO: This is inefficient. It literally creates a mesh, then potentially removes it.
        context.view_layer.update()

        if (
            building_obj
            and building_element
            and building_element.is_a() in ["IfcWall", "IfcWallStandardCase", "IfcCovering", "IfcElementAssembly"]
            and instance_class in ["IfcWindow", "IfcDoor"]
        ):
            # Fills should be a sibling to the building element
            parent = ifcopenshell.util.element.get_aggregate(building_element)
            if parent:
                parent_obj = tool.Ifc.get_object(parent)
                bonsai.core.aggregate.assign_object(
                    tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=parent_obj, related_obj=obj
                )
            else:
                parent = ifcopenshell.util.element.get_container(building_element)
                if parent:
                    bonsai.core.spatial.assign_container(
                        tool.Ifc, tool.Collector, tool.Spatial, container=parent, element_obj=obj
                    )

        # set occurrences properties for the types defined with modifiers
        if instance_class in ["IfcWindow", "IfcDoor"]:
            pset_name = f"BBIM_{instance_class[3:]}"
            bbim_pset = ifcopenshell.util.element.get_psets(element).get(pset_name, None)
            if bbim_pset:
                bbim_prop_data = json.loads(bbim_pset["Data"])
                element.OverallWidth = bbim_prop_data["overall_width"]
                element.OverallHeight = bbim_prop_data["overall_height"]

        if (
            building_obj
            and building_element
            and building_element.is_a() in ["IfcWall", "IfcWallStandardCase", "IfcCovering", "IfcElementAssembly"]
        ):
            if instance_class in ["IfcWindow", "IfcDoor"]:
                # TODO For now we are hardcoding windows and doors as a prototype
                bpy.ops.bim.add_filled_opening(voided_obj=building_obj.name, filling_obj=obj.name)
        else:
            if self.container_obj:
                if props.rl_mode == "BOTTOM":
                    obj.location.z = self.container_obj.location.z - tool.Blender.get_object_bounding_box(obj)["min_z"]
                elif props.rl_mode == "CONTAINER":
                    obj.location.z = self.container_obj.location.z
                elif props.rl_mode == "CURSOR":
                    pass

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(relating_type):
            mat = Matrix(ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement))
            mat.translation *= unit_scale
            mat = obj.matrix_world @ mat
            new_port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            new_port.PredefinedType = port.PredefinedType
            new_port.SystemType = port.SystemType
            tool.Ifc.run("system.assign_port", element=element, port=new_port)
            tool.Ifc.run("geometry.edit_object_placement", product=new_port, matrix=mat, is_si=True)

        if ifc_class == "IfcDoorType" and len(context.selected_objects) >= 1:
            pass
        else:
            tool.Blender.select_and_activate_single_object(context, obj)
        return {"FINISHED"}

    def set_flow_segment_rl(self, obj):
        if self.container_obj:
            obj.location[2] = self.container_obj.location[2] + bpy.context.scene.BIMModelProperties.rl2

    @staticmethod
    def generate_layered_element(ifc_class: str, relating_type: ifcopenshell.entity_instance) -> bool:
        layer_set_direction = None

        parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
        if parametric:
            layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)
        if layer_set_direction is None:
            if ifc_class in ["IfcSlabType", "IfcRoofType", "IfcRampType", "IfcPlateType"]:
                layer_set_direction = "AXIS3"
            else:
                layer_set_direction = "AXIS2"

        obj = None
        if layer_set_direction == "AXIS3":
            obj = slab.DumbSlabGenerator(relating_type).generate()
        elif layer_set_direction == "AXIS2":
            obj = wall.DumbWallGenerator(relating_type).generate()
        else:
            pass  # Dumb block generator? Eh? :)

        if obj:
            material = ifcopenshell.util.element.get_material(tool.Ifc.get_entity(obj))
            material.LayerSetDirection = layer_set_direction
            return True
        return False


class ChangeTypePage(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_type_page"
    bl_label = "Change Type Page"
    bl_options = {"REGISTER"}
    page: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        bpy.ops.bim.load_type_thumbnails(ifc_class=props.type_class, offset=9 * (self.page - 1), limit=9)
        props.type_page = self.page
        return {"FINISHED"}


class AlignProduct(bpy.types.Operator):
    bl_idname = "bim.align_product"
    bl_label = "Align Product"
    bl_options = {"REGISTER", "UNDO"}
    align_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) < 2 or not context.active_object:
            return {"FINISHED"}
        if self.align_type == "CENTERLINE":
            point = context.active_object.matrix_world @ (
                Vector(context.active_object.bound_box[0]) + (context.active_object.dimensions / 2)
            )
        elif self.align_type == "POSITIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[6])
        elif self.align_type == "NEGATIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[0])

        active_x_axis = context.active_object.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        active_y_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        active_z_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, 1))

        x_distances = self.get_axis_distances(point, active_x_axis, context)
        y_distances = self.get_axis_distances(point, active_y_axis, context)
        if abs(sum(x_distances)) < abs(sum(y_distances)):
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_x_axis * -x_distances[i]) @ obj.matrix_world
        else:
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_y_axis * -y_distances[i]) @ obj.matrix_world
        return {"FINISHED"}

    def get_axis_distances(self, point, axis, context):
        results = []
        for obj in context.selected_objects:
            if self.align_type == "CENTERLINE":
                obj_point = obj.matrix_world @ (Vector(obj.bound_box[0]) + (obj.dimensions / 2))
            elif self.align_type == "POSITIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[6])
            elif self.align_type == "NEGATIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[0])
            results.append(mathutils.geometry.distance_point_to_plane(obj_point, point, axis))
        return results


class LoadTypeThumbnails(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_type_thumbnails"
    bl_label = "Load Type Thumbnails"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    limit: bpy.props.IntProperty()
    offset: bpy.props.IntProperty()

    def _execute(self, context):
        if bpy.app.background:
            return

        props = bpy.context.scene.BIMModelProperties
        processing = set()
        # Only process at most one paginated class at a time.
        # Large projects have hundreds of types which can lead to unnecessary lag.
        queue = sorted(tool.Ifc.get().by_type(self.ifc_class), key=lambda e: e.Name or "Unnamed")
        if self.limit:
            queue = queue[self.offset : self.offset + self.limit]
        else:
            offset = 9 * (props.type_page - 1)
            if offset < 0:
                offset = 0
            queue = queue[offset : offset + 9]

        while queue:
            # if bpy.app.is_job_running("RENDER_PREVIEW") does not seem to reflect asset preview generation
            element = queue.pop()
            if tool.Model.update_thumbnail_for_element(element):
                queue.append(element)
        return {"FINISHED"}


class MirrorElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.mirror_elements"
    bl_label = "Mirror Elements"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Faux-mirrors the selected objects by an active empty along a mirror plane"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def _execute(self, context):
        # This is not a true mirror operation. In BIM, objects that are
        # mirrored are not the same type. (i.e. a mirrored asymmetric desk is a
        # completely different product). To preserve types, we calculate
        # bounding box centroids, and mirror the position of the object.  The
        # mirrored object performs the necessary rotation to preserve the
        # mirrored intention, but never actually truly mirror anything (i.e.
        # scale = -1).

        # Objects are mirrored along the YZ plane of the mirror object.
        # Mirrored objects have their relative local Y and Z axes preserved,
        # and the new X axis is calculated.

        # In theory, untyped objects may be truly mirrored, but this is not yet
        # implemented.
        mirror = context.active_object
        reflection = Matrix()
        reflection[0][0] = -1

        mirror.select_set(False)

        if not context.selected_objects:
            self.report(
                {"INFO"},
                "At least two objects must be selected: an object to be mirrored, and a mirror axis as the active object.",
            )
            return {"FINISHED"}

        bpy.ops.bim.override_object_duplicate_move(is_interactive=False)

        for obj in context.selected_objects:
            if obj == mirror:
                continue

            objmat = mirror.matrix_world.inverted() @ obj.matrix_world.copy()
            x, y, z = objmat.to_3x3().col
            centroid = Vector(obj.bound_box[0]).lerp(Vector(obj.bound_box[6]), 0.5)
            c = mirror.matrix_world.inverted() @ obj.matrix_world @ centroid
            newy = mirror.matrix_world.to_quaternion() @ (y @ reflection)
            newz = mirror.matrix_world.to_quaternion() @ (z @ reflection)
            newx = newy.cross(newz)
            newc = mirror.matrix_world @ (c @ reflection)

            newmat = Matrix((newx.to_4d(), newy.to_4d(), newz.to_4d(), newc.to_4d())).transposed()
            newmat.translation = Vector(newmat.translation) - (newmat.to_quaternion() @ centroid)

            obj.matrix_world = newmat


def generate_box(usecase_path, ifc_file, settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    if 0 in list(obj.dimensions):
        return
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bonsai.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_box)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box},
        )


def regenerate_profile_usage(usecase_path, ifc_file, settings):
    elements = []
    if ifc_file.schema == "IFC2X3":
        for rel in ifc_file.get_inverse(settings["usage"]):
            if not rel.is_a("IfcRelAssociatesMaterial"):
                continue
            for element in rel.RelatedObjects:
                elements.append(element)
    else:
        for rel in settings["usage"].AssociatedTo:
            for element in rel.RelatedObjects:
                elements.append(element)

    for element in elements:
        obj = IfcStore.get_element(element.id())
        if not obj:
            continue
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bonsai.core.geometry.switch_representation(
                tool.Ifc,
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                is_global=True,
                should_sync_changes_first=False,
            )
