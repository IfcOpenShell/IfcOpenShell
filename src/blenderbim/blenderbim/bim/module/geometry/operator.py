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
import logging
import numpy as np
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.api
import blenderbim.core.geometry as core
import blenderbim.core.style
import blenderbim.core.root
import blenderbim.tool as tool
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim import import_ifc
from ifcopenshell.api.geometry.data import Data
from ifcopenshell.api.context.data import Data as ContextData
from ifcopenshell.api.void.data import Data as VoidData
from mathutils import Vector


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class EditObjectPlacement(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_object_placement"
    bl_label = "Edit Object Placement"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            core.edit_object_placement(tool.Ifc, tool.Surveyor, obj=obj)


class AddRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.add_representation"
    bl_label = "Add Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()
    ifc_representation_class: bpy.props.StringProperty()
    profile_set_usage: bpy.props.IntProperty()

    def _execute(self, context):
        ifc_context = self.context_id or int(context.scene.BIMProperties.contexts or "0") or None
        if ifc_context:
            ifc_context = tool.Ifc.get().by_id(ifc_context)
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        core.add_representation(
            tool.Ifc,
            tool.Geometry,
            tool.Style,
            tool.Surveyor,
            obj=obj,
            context=ifc_context,
            ifc_representation_class=self.ifc_representation_class,
            profile_set_usage=tool.Ifc.get().by_id(self.profile_set_usage) if self.profile_set_usage else None,
        )
        Data.load(tool.Ifc.get(), obj.BIMObjectProperties.ifc_definition_id)
        element = tool.Ifc.get_entity(obj)
        if element.is_a("IfcTypeProduct"):
            if tool.Ifc.get_schema() == "IFC2X3":
                types = element.ObjectTypeOf
            else:
                types = element.Types
            if types:
                for element in types[0].RelatedObjects:
                    Data.load(tool.Ifc.get(), element.id())


class SwitchRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.switch_representation"
    bl_label = "Switch Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_definition_id: bpy.props.IntProperty()
    should_reload: bpy.props.BoolProperty()
    disable_opening_subtractions: bpy.props.BoolProperty()
    should_switch_all_meshes: bpy.props.BoolProperty()

    def _execute(self, context):
        core.switch_representation(
            tool.Geometry,
            obj=bpy.data.objects.get(self.obj) if self.obj else context.active_object,
            representation=tool.Ifc.get().by_id(self.ifc_definition_id),
            should_reload=self.should_reload,
            enable_dynamic_voids=self.disable_opening_subtractions,
            is_global=self.should_switch_all_meshes,
        )


class RemoveRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_representation"
    bl_label = "Remove Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    representation_id: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        representation = self.file.by_id(self.representation_id)
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        is_mapped_representation = representation.RepresentationType == "MappedRepresentation"
        if is_mapped_representation:
            mesh_name = "{}/{}".format(
                representation.ContextOfItems.id(), representation.Items[0].MappingSource.MappedRepresentation.id()
            )
        else:
            mesh_name = "{}/{}".format(representation.ContextOfItems.id(), representation.id())
        mesh = bpy.data.meshes.get(mesh_name)
        if mesh:
            if obj.data == mesh:
                # TODO we can do better than this
                void_mesh = bpy.data.meshes.get("Void")
                if not void_mesh:
                    void_mesh = bpy.data.meshes.new("Void")
                obj.data = void_mesh
            if not is_mapped_representation:
                bpy.data.meshes.remove(mesh)
        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        ifcopenshell.api.run(
            "geometry.unassign_representation", self.file, **{"product": product, "representation": representation}
        )
        ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        Data.load(self.file, product.id())
        return {"FINISHED"}


class UpdateRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_representation"
    bl_label = "Update Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_representation_class: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object.mode == "OBJECT"

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if not ContextData.is_loaded:
            ContextData.load(IfcStore.get_file())

        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        self.file = IfcStore.get_file()

        for obj in objs:
            self.update_obj_mesh_representation(context, obj)
            IfcStore.edited_objs.discard(obj)
        return {"FINISHED"}

    def update_obj_mesh_representation(self, context, obj):
        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)

        if product.is_a("IfcGridAxis"):
            ifcopenshell.api.run("grid.create_axis_curve", self.file, **{"axis_curve": obj, "grid_axis": product})
            return

        core.edit_object_placement(tool.Ifc, tool.Surveyor, obj=obj)

        old_representation = self.file.by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        context_of_items = old_representation.ContextOfItems

        gprop = context.scene.BIMGeoreferenceProperties
        coordinate_offset = None
        if gprop.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT":
            coordinate_offset = Vector(
                (
                    float(gprop.blender_eastings),
                    float(gprop.blender_northings),
                    float(gprop.blender_orthogonal_height),
                )
            )

        representation_data = {
            "context": context_of_items,
            "blender_object": obj,
            "geometry": obj.data,
            "coordinate_offset": coordinate_offset,
            "total_items": max(1, len(obj.material_slots)),
            "should_force_faceted_brep": context.scene.BIMGeometryProperties.should_force_faceted_brep,
            "should_force_triangulation": context.scene.BIMGeometryProperties.should_force_triangulation,
            "ifc_representation_class": self.ifc_representation_class,
        }

        new_representation = ifcopenshell.api.run("geometry.add_representation", self.file, **representation_data)

        [
            blenderbim.core.style.add_style(tool.Ifc, tool.Style, obj=s.material)
            for s in obj.material_slots
            if s.material and not s.material.BIMMaterialProperties.ifc_style_id
        ]

        if isinstance(obj.data, bpy.types.Mesh) and len(obj.data.polygons):
            ifcopenshell.api.run(
                "style.assign_representation_styles",
                self.file,
                **{
                    "shape_representation": new_representation,
                    "styles": [
                        self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                        for s in obj.material_slots
                        if s.material
                    ],
                    "should_use_presentation_style_assignment": context.scene.BIMGeometryProperties.should_use_presentation_style_assignment,
                },
            )

        # TODO: move this into a replace_representation usecase or something
        for inverse in self.file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        obj.data.BIMMeshProperties.ifc_definition_id = int(new_representation.id())
        obj.data.name = f"{old_representation.ContextOfItems.id()}/{new_representation.id()}"
        bpy.ops.bim.remove_representation(representation_id=old_representation.id(), obj=obj.name)
        Data.load(self.file, obj.BIMObjectProperties.ifc_definition_id)
        if obj.data.BIMMeshProperties.ifc_parameters:
            bpy.ops.bim.get_representation_ifc_parameters()


class UpdateParametricRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_parametric_representation"
    bl_label = "Update Parametric Representation"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object.mode == "OBJECT"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = context.active_object
        props = obj.data.BIMMeshProperties
        parameter = props.ifc_parameters[self.index]
        self.file.by_id(parameter.step_id)[parameter.index] = parameter.value
        show_representation_parameters = bool(props.ifc_parameters)
        core.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=tool.Ifc.get().by_id(props.ifc_definition_id),
            should_reload=True,
            enable_dynamic_voids=False,
            is_global=True,
        )
        if show_representation_parameters:
            bpy.ops.bim.get_representation_ifc_parameters()
        return {"FINISHED"}


class GetRepresentationIfcParameters(bpy.types.Operator):
    bl_idname = "bim.get_representation_ifc_parameters"
    bl_label = "Get Representation IFC Parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = context.active_object
        props = obj.data.BIMMeshProperties
        elements = self.file.traverse(self.file.by_id(props.ifc_definition_id))
        props.ifc_parameters.clear()
        for element in elements:
            if element.is_a("IfcRepresentationItem") or element.is_a("IfcParameterizedProfileDef"):
                for i in range(0, len(element)):
                    if element.attribute_type(i) == "DOUBLE":
                        new = props.ifc_parameters.add()
                        new.name = "{}/{}".format(element.is_a(), element.attribute_name(i))
                        new.step_id = element.id()
                        new.type = element.attribute_type(i)
                        new.index = i
                        if element[i]:
                            new.value = element[i]
        return {"FINISHED"}


class CopyRepresentation(bpy.types.Operator, Operator):
    bl_idname = "bim.copy_representation"
    bl_label = "Copy Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        if not context.active_object:
            return
        bm = bmesh.new()
        bm.from_mesh(context.active_object.data)
        for obj in context.selected_objects:
            if obj == context.active_object:
                continue
            if obj.data:
                bm.to_mesh(obj.data)
                core.add_representation(
                    tool.Ifc,
                    tool.Geometry,
                    tool.Style,
                    tool.Surveyor,
                    obj=obj,
                    context=tool.Ifc.get().by_id(int(context.scene.BIMProperties.contexts)),
                    ifc_representation_class=None,
                    profile_set_usage=None,
                )


class OverrideDelete(bpy.types.Operator):
    bl_idname = "object.delete"
    bl_label = "Delete"
    use_global: bpy.props.BoolProperty(default=False)
    confirm: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # Deep magick from the dawn of time
        if IfcStore.get_file():
            return IfcStore.execute_ifc_operator(self, context)
        for obj in context.selected_objects:
            bpy.data.objects.remove(obj)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        file = IfcStore.get_file()
        for obj in context.selected_objects:
            if obj.BIMObjectProperties.ifc_definition_id:
                element = file.by_id(obj.BIMObjectProperties.ifc_definition_id)
                if element.FillsVoids:
                    self.remove_filling(element)
                if element.is_a("IfcOpeningElement"):
                    for rel in element.HasFillings:
                        self.remove_filling(rel.RelatedBuildingElement)
                    if element.VoidsElements:
                        self.delete_opening_element(element)
                elif element.HasOpenings:
                    for rel in element.HasOpenings:
                        self.delete_opening_element(rel.RelatedOpeningElement)
            bpy.data.objects.remove(obj)
        return {"FINISHED"}

    def delete_opening_element(self, element):
        obj = IfcStore.get_element(element.VoidsElements[0].RelatingBuildingElement.id())
        bpy.ops.bim.remove_opening(opening_id=element.id(), obj=obj.name)

    def remove_filling(self, element):
        obj = IfcStore.get_element(element.id())
        bpy.ops.bim.remove_filling(obj=obj.name)


class OverrideDuplicateMove(bpy.types.Operator):
    bl_idname = "object.duplicate_move"
    bl_label = "Duplicate Objects"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # Deep magick from the dawn of time
        if IfcStore.get_file():
            IfcStore.execute_ifc_operator(self, context)
            if self.new_active_obj:
                context.view_layer.objects.active = self.new_active_obj
            return {"FINISHED"}

        new_active_obj = None
        for obj in context.selected_objects:
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()
            if obj == context.active_object:
                new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)
        if new_active_obj:
            context.view_layer.objects.active = new_active_obj
        bpy.ops.transform.translate("INVOKE_DEFAULT")
        return {"FINISHED"}

    def _execute(self, context):
        self.new_active_obj = None
        for obj in context.selected_objects:
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()
            if obj == context.active_object:
                self.new_active_obj = new_obj
            for collection in obj.users_collection:
                collection.objects.link(new_obj)
            obj.select_set(False)
            new_obj.select_set(True)
            # This is the only difference
            blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Root, obj=new_obj)
        bpy.ops.transform.translate("INVOKE_DEFAULT")
        blenderbim.bim.handler.purge_module_data()
        return {"FINISHED"}
