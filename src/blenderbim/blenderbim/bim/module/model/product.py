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
import mathutils
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import blenderbim.tool as tool
import blenderbim.core.type
import blenderbim.core.geometry
from . import wall, slab, profile, mep
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.model.data import AuthoringData
from ifcopenshell.api.pset.data import Data as PsetData
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
from . import prop


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        context.scene.collection.objects.link(obj)
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = obj
        obj.select_set(True)
        return {"FINISHED"}


def add_empty_type_button(self, context):
    self.layout.operator(AddEmptyType.bl_idname, icon="FILE_3D")


class AddConstrTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_constr_type_instance"
    bl_label = "Add"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Type Instance to the model"
    ifc_class: bpy.props.StringProperty()
    relating_type_id: bpy.props.IntProperty()
    from_invoke: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        ifc_class = self.ifc_class or props.ifc_class
        relating_type_id = self.relating_type_id or props.relating_type_id

        if not ifc_class or not relating_type_id:
            return {"FINISHED"}

        if self.from_invoke:
            props.ifc_class = self.ifc_class
            props.relating_type_id = str(self.relating_type_id)

        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, self.file.schema)[0]
        relating_type = self.file.by_id(int(relating_type_id))
        material = ifcopenshell.util.element.get_material(relating_type)

        if material and material.is_a("IfcMaterialProfileSet"):
            if profile.DumbProfileGenerator(relating_type).generate():
                return {"FINISHED"}
        elif material and material.is_a("IfcMaterialLayerSet"):
            if self.generate_layered_element(ifc_class, relating_type):
                return {"FINISHED"}
        if relating_type.is_a("IfcFlowSegmentType") and not relating_type.RepresentationMaps:
            if mep.MepGenerator(relating_type).generate():
                return {"FINISHED"}

        building_obj = None
        if len(context.selected_objects) == 1 and context.active_object:
            building_obj = context.active_object

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
        collection = context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)
        collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        element = tool.Ifc.get_entity(obj)
        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

        if building_obj:
            if instance_class in ["IfcWindow", "IfcDoor"]:
                # TODO For now we are hardcoding windows and doors as a prototype
                bpy.ops.bim.add_element_opening(
                    voided_building_element=building_obj.name, filling_building_element=obj.name
                )
            if instance_class == "IfcDoor":
                obj.location[2] = building_obj.location[2] - min([v[2] for v in obj.bound_box])
        else:
            if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
                obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        for port in ifcopenshell.util.system.get_ports(relating_type):
            mat = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
            mat[0][3] *= unit_scale
            mat[1][3] *= unit_scale
            mat[2][3] *= unit_scale
            mat = obj.matrix_world @ mathutils.Matrix(mat)
            new_port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            tool.Ifc.run("system.assign_port", element=element, port=new_port)
            tool.Ifc.run("geometry.edit_object_placement", product=new_port, matrix=mat, is_si=True)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {"FINISHED"}

    @staticmethod
    def generate_layered_element(ifc_class, relating_type):
        layer_set_direction = None

        parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
        if parametric:
            layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)
        if layer_set_direction is None:
            if ifc_class in ["IfcSlabType", "IfcRoofType", "IfcRampType", "IfcPlateType"]:
                layer_set_direction = "AXIS3"
            else:
                layer_set_direction = "AXIS2"

        if layer_set_direction == "AXIS3":
            if slab.DumbSlabGenerator(relating_type).generate():
                return True
        elif layer_set_direction == "AXIS2":
            if wall.DumbWallGenerator(relating_type).generate():
                return True
        else:
            pass  # Dumb block generator? Eh? :)


class DisplayConstrTypes(bpy.types.Operator):
    bl_idname = "bim.display_constr_types"
    bl_label = "Browse Construction Types"
    bl_options = {"REGISTER"}
    bl_description = "Display all available Construction Types to add new instances"

    def invoke(self, context, event):
        if not AuthoringData.is_loaded:
            AuthoringData.load()
        props = context.scene.BIMModelProperties
        ifc_class = props.ifc_class
        relating_type_info = AuthoringData.relating_type_info(ifc_class)
        if relating_type_info is None or not relating_type_info.fully_loaded:
            AuthoringData.assetize_constr_class(ifc_class)
        bpy.ops.bim.display_constr_types_ui("INVOKE_DEFAULT")
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


class DynamicallyVoidProduct(bpy.types.Operator):
    bl_idname = "bim.dynamically_void_product"
    bl_label = "Dynamically Void Product"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj)
        if obj is None:
            return {"FINISHED"}
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        if not product.HasOpenings:
            return {"FINISHED"}
        if [m for m in obj.modifiers if m.type == "BOOLEAN"]:
            return {"FINISHED"}
        representation = ifcopenshell.util.representation.get_representation(product, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return {"FINISHED"}
        was_edit_mode = obj.mode == "EDIT"
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")
        blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            enable_dynamic_voids=True,
            is_global=True,
            should_sync_changes_first=False,
        )
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


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
            blenderbim.core.geometry.remove_representation(tool.Ifc, tool.Geometry, obj=obj, representation=old_box)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
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
            blenderbim.core.geometry.switch_representation(
                tool.Geometry,
                obj=obj,
                representation=representation,
                should_reload=True,
                enable_dynamic_voids=True,
                is_global=True,
                should_sync_changes_first=False,
            )


def ensure_material_assigned(usecase_path, ifc_file, settings):
    if usecase_path == "material.assign_material":
        if not settings.get("material", None):
            return
        elements = [settings["product"]]
    else:
        elements = []
        for rel in ifc_file.by_type("IfcRelAssociatesMaterial"):
            if rel.RelatingMaterial == settings["material"] or [
                e for e in ifc_file.traverse(rel.RelatingMaterial) if e == settings["material"]
            ]:
                elements.extend(rel.RelatedObjects)

    for element in elements:
        obj = IfcStore.get_element(element.GlobalId)
        if not obj or not obj.data:
            continue

        element_material = ifcopenshell.util.element.get_material(element)
        material = [m for m in ifc_file.traverse(element_material) if m.is_a("IfcMaterial")]

        object_material_ids = [
            om.BIMObjectProperties.ifc_definition_id
            for om in obj.data.materials
            if om is not None and om.BIMObjectProperties.ifc_definition_id
        ]

        if material and material[0].id() in object_material_ids:
            continue

        if len(obj.data.materials) == 1:
            obj.data.materials.clear()

        if not material:
            continue

        obj.data.materials.append(IfcStore.get_element(material[0].id()))
