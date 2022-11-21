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
import bmesh
import ifcopenshell.util.schema
import ifcopenshell.util.type
import ifcopenshell.api
import blenderbim.tool as tool
import blenderbim.core.geometry
import blenderbim.core.type as core
import blenderbim.core.root
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.type.data import Data
from ifcopenshell.api.geometry.data import Data as GeometryData
from ifcopenshell.api.material.data import Data as MaterialData


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AssignType(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_type"
    bl_label = "Assign Type"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def _execute(self, context):
        type = tool.Ifc.get().by_id(self.relating_type or int(context.active_object.BIMTypeProperties.relating_type))
        related_objects = (
            [bpy.data.objects.get(self.related_object)]
            if self.related_object
            else context.selected_objects or [context.active_object]
        )
        for obj in related_objects:
            core.assign_type(tool.Ifc, tool.Type, element=tool.Ifc.get_entity(obj), type=type)
            oprops = obj.BIMObjectProperties
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
            GeometryData.load(IfcStore.get_file(), oprops.ifc_definition_id)
            MaterialData.load(IfcStore.get_file(), oprops.ifc_definition_id)
        MaterialData.load(IfcStore.get_file())


class UnassignType(bpy.types.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            ifcopenshell.api.run(
                "type.unassign_type",
                self.file,
                **{
                    "related_object": self.file.by_id(oprops.ifc_definition_id),
                },
            )
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMTypeProperties.is_editing_type = True
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        obj.BIMTypeProperties.is_editing_type = False
        return {"FINISHED"}


class SelectType(bpy.types.Operator):
    bl_idname = "bim.select_type"
    bl_label = "Select Type"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.IntProperty()

    def execute(self, context):
        element = tool.Ifc.get().by_id(self.relating_type)
        obj = tool.Ifc.get_object(element)
        if obj:
            context.view_layer.objects.active = obj
            obj.select_set(True)
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else context.active_object
        oprops = related_object.BIMObjectProperties
        product = self.file.by_id(oprops.ifc_definition_id)
        declaration = IfcStore.get_schema().declaration_by_name(product.is_a())
        if ifcopenshell.util.schema.is_a(declaration, "IfcElementType"):
            related_objects = ifcopenshell.api.run(
                "type.get_related_objects", self.file, **{"relating_type": self.file.by_id(oprops.ifc_definition_id)}
            )
        else:
            related_objects = ifcopenshell.api.run(
                "type.get_related_objects", self.file, **{"related_object": self.file.by_id(oprops.ifc_definition_id)}
            )
        for obj in context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}


class SelectTypeObjects(bpy.types.Operator):
    bl_idname = "bim.select_type_objects"
    bl_label = "Select Type Objects"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        relating_type = bpy.data.objects.get(self.relating_type) if self.relating_type else context.active_object
        for element in ifcopenshell.util.element.get_types(tool.Ifc.get_entity(relating_type)):
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


class AddType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_type"
    bl_label = "Add Type"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        ifc_class = props.type_class
        predefined_type = props.type_predefined_type
        template = props.type_template
        body = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        if not body:
            return {"FINISHED"}
        if template == "MESH":
            location = context.scene.cursor.location
            if context.active_object and context.selected_objects and context.active_object.data:
                obj = context.active_object
                element = tool.Ifc.get_entity(obj)
                if element:
                    mesh = obj.data.copy()
                    mesh.BIMMeshProperties.ifc_definition_id = 0
                    obj = bpy.data.objects.new(element.Name or "TYPEX", mesh)
            else:
                mesh = bpy.data.meshes.new("TYPEX")
                bm = bmesh.new()
                bmesh.ops.create_cube(bm, size=1)
                bm.to_mesh(mesh)
                bm.free()
                obj = bpy.data.objects.new("TYPEX", mesh)
            obj.matrix_world.col[3] = location.to_4d()
            blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=True,
                context=body,
                ifc_representation_class=None,
            )
        elif template in ("LAYERSET_AXIS2", "LAYERSET_AXIS3"):
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            obj = bpy.data.objects.new("TYPEX", None)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=True,
                context=body,
                ifc_representation_class=None,
            )
            materials = tool.Ifc.get().by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = self.add_default_material()
            rel = ifcopenshell.api.run(
                "material.assign_material", tool.Ifc.get(), product=element, type="IfcMaterialLayerSet"
            )
            layer_set = rel.RelatingMaterial
            layer = ifcopenshell.api.run("material.add_layer", tool.Ifc.get(), layer_set=layer_set, material=material)
            thickness = 0.1  # Arbitrary metric thickness for now
            layer.LayerThickness = thickness / unit_scale

            pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="EPset_Parametric")
            if template == "LAYERSET_AXIS2":
                axis = "AXIS2"
            elif template == "LAYERSET_AXIS3":
                axis = "AXIS3"
            ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"LayerSetDirection": axis})
        elif template == "PROFILESET":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            obj = bpy.data.objects.new("TYPEX", None)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=True,
                context=body,
                ifc_representation_class=None,
            )
            materials = tool.Ifc.get().by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = self.add_default_material()
            size = 0.5 / unit_scale
            profile = tool.Ifc.get().create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=size, YDim=size)
            rel = ifcopenshell.api.run(
                "material.assign_material", tool.Ifc.get(), product=element, type="IfcMaterialProfileSet"
            )
            profile_set = rel.RelatingMaterial
            material_profile = ifcopenshell.api.run(
                "material.add_profile", tool.Ifc.get(), profile_set=profile_set, material=material
            )
            ifcopenshell.api.run(
                "material.assign_profile", tool.Ifc.get(), material_profile=material_profile, profile=profile
            )
        elif template == "EMPTY":
            obj = bpy.data.objects.new("TYPEX", None)
            blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=True,
                context=body,
                ifc_representation_class=None,
            )
        bpy.ops.bim.load_type_thumbnails(ifc_class=ifc_class)
        return {"FINISHED"}

    def add_default_material(self):
        material = ifcopenshell.api.run("material.add_material", tool.Ifc.get(), name="Unknown")
        blender_material = bpy.data.materials.new(material.Name)
        tool.Ifc.link(material, blender_material)
        blender_material.use_fake_user = True
        return material


class RemoveType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_type"
    bl_label = "Remove Type"
    bl_options = {"REGISTER"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
        if obj:
            tool.Ifc.unlink(obj=obj)
            bpy.data.objects.remove(obj)
        return {"FINISHED"}


class DuplicateType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_type"
    bl_label = "Duplicate Type"
    bl_options = {"REGISTER"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        if not obj:
            return {"FINISHED"}
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        new = blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)
        new.Name += " Copy"
        bpy.ops.bim.load_type_thumbnails(ifc_class=new.is_a())
        return {"FINISHED"}
