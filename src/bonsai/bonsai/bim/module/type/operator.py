# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import bmesh
import ifcopenshell.util.element
import ifcopenshell.util.schema
import ifcopenshell.util.representation
import ifcopenshell.util.type
import ifcopenshell.util.unit
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.geometry
import bonsai.core.type as core
import bonsai.core.root
from bonsai.bim.ifc import IfcStore


class AssignType(bpy.types.Operator, tool.Ifc.Operator):
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
        model_props = context.scene.BIMModelProperties
        for obj in related_objects:
            element = tool.Ifc.get_entity(obj)
            core.assign_type(tool.Ifc, tool.Type, element=element, type=type)
            if model_props.occurrence_name_style == "TYPE":
                obj.name = tool.Model.generate_occurrence_name(type, element.is_a())


class UnassignType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def _execute(self, context):
        def exclude_callback(attribute):
            return attribute.is_a("IfcProfileDef") and attribute.ProfileName

        self.file = IfcStore.get_file()
        objs = [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element or element.is_a("IfcElementType"):
                continue
            ifcopenshell.api.run("type.unassign_type", self.file, related_objects=[element])

            if element.Representation:
                new_active_representation = None
                active_representation = tool.Geometry.get_active_representation(obj)
                active_context = active_representation.ContextOfItems
                representations = []
                for representation in element.Representation.Representations:
                    resolved_representation = ifcopenshell.util.representation.resolve_representation(representation)
                    if representation == resolved_representation:
                        representations.append(representation)
                    else:
                        # We must unmap representations.
                        copied_representation = ifcopenshell.util.element.copy_deep(
                            tool.Ifc.get(),
                            resolved_representation,
                            exclude=["IfcGeometricRepresentationContext"],
                            exclude_callback=exclude_callback,
                        )
                        representations.append(copied_representation)
                        if representation.ContextOfItems == active_context:
                            new_active_representation = copied_representation
                element.Representation.Representations = representations

                if new_active_representation:
                    bonsai.core.geometry.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=obj,
                        representation=new_active_representation,
                        should_reload=False,
                        is_global=False,
                        should_sync_changes_first=False,
                    )
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMTypeProperties.is_editing_type = True
        context.active_object.BIMTypeProperties.relating_type_object = None
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

        if self.relating_type:  # if operator button sends a relating_type, the iterator only selects this one type
            element = tool.Ifc.get().by_id(self.relating_type)
            obj = tool.Ifc.get_object(element)
            selected_objs = [obj]
        else:  # else, the iterator selects all the types of all the selected objects
            selected_objs = context.selected_objects
            active_obj = context.active_object
            selected_objs.append(active_obj)  # update selected_objs so the active_obj is at the end of the list

        last_relating_type_obj = None
        for obj in selected_objs:
            element = tool.Ifc.get_entity(obj)
            relating_type = ifcopenshell.util.element.get_type(element)
            if relating_type:
                relating_type_obj = tool.Ifc.get_object(relating_type)
                if relating_type_obj:
                    if relating_type_obj.hide_get():
                        relating_type_obj.hide_set(False)
                    relating_type_obj.select_set(True)
                    last_relating_type_obj = relating_type_obj
            if not element.is_a("IfcTypeObject"):
                obj.select_set(False)

        context.view_layer.objects.active = last_relating_type_obj  # makes the active_obj's type the active object

        return {"FINISHED"}

    def find_collection_in_ifcproject(self, context, collection_name):

        ifc_project_collection = None
        for child in context.view_layer.layer_collection.children:
            if "IfcProject" in child.name:
                ifc_project_collection = child
                break

        if ifc_project_collection:
            collection_in_view_layer = ifc_project_collection.children.get(collection_name)
            return collection_in_view_layer


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        objects = bpy.context.selected_objects

        # store relating types to avoid selecting same elements multiple times
        relating_types = set()

        for related_object in objects:
            relating_type = ifcopenshell.util.element.get_type(tool.Ifc.get_entity(related_object))
            if not relating_type:
                related_object.select_set(False)
                continue
            relating_types.add(relating_type)

        for relating_type in relating_types:
            related_objects = ifcopenshell.util.element.get_types(relating_type)
            for element in related_objects:
                obj = tool.Ifc.get_object(element)
                if obj and obj in context.visible_objects:
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
        at_least_one_selectable_typed_object = False
        for element in ifcopenshell.util.element.get_types(tool.Ifc.get_entity(relating_type)):
            obj = tool.Ifc.get_object(element)
            if obj and obj in context.selectable_objects:
                obj.select_set(True)
                at_least_one_selectable_typed_object = True
        if at_least_one_selectable_typed_object:
            context.active_object.select_set(False)
            context.view_layer.objects.active = context.selected_objects[0]
        else:
            self.report({"INFO"}, "Typed objects can't be selected : They may be hidden or in an excluded collection.")
        return {"FINISHED"}


class AddType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_type"
    bl_label = "Add Type"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMModelProperties
        ifc_class = props.type_class
        predefined_type = props.type_predefined_type
        name = props.type_name
        template = props.type_template
        ifc_file = tool.Ifc.get()
        body = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        if not body:
            props.type_class = props.type_class
            self.report({"ERROR"}, "No Model/Body/MODEL_VIEW context found.")
            return {"FINISHED"}

        if template == "MESH":
            location = context.scene.cursor.location
            if context.active_object and context.selected_objects and context.active_object.data:
                obj = context.active_object
                element = tool.Ifc.get_entity(obj)
                if element:
                    mesh = obj.data.copy()
                    mesh.BIMMeshProperties.ifc_definition_id = 0
                    obj = bpy.data.objects.new(element.Name or name, mesh)
            else:
                mesh = bpy.data.meshes.new(name)
                bm = bmesh.new()
                bmesh.ops.create_cube(bm, size=1)
                bm.to_mesh(mesh)
                bm.free()
                obj = bpy.data.objects.new(name, mesh)
            obj.matrix_world.translation = location
            bonsai.core.root.assign_class(
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
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            obj = bpy.data.objects.new(name, None)
            element = bonsai.core.root.assign_class(
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
            materials = ifc_file.by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = ifcopenshell.api.run("material.add_material", tool.Ifc.get(), name="Unknown")
            rel = ifcopenshell.api.run(
                "material.assign_material", ifc_file, products=[element], type="IfcMaterialLayerSet"
            )
            layer_set = rel.RelatingMaterial
            layer = ifcopenshell.api.run("material.add_layer", ifc_file, layer_set=layer_set, material=material)
            thickness = 0.1  # Arbitrary metric thickness for now
            layer.LayerThickness = thickness / unit_scale

            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="EPset_Parametric")
            if template == "LAYERSET_AXIS2":
                axis = "AXIS2"
            elif template == "LAYERSET_AXIS3":
                axis = "AXIS3"
            ifcopenshell.api.run("pset.edit_pset", ifc_file, pset=pset, properties={"LayerSetDirection": axis})

        elif template == "PROFILESET" or template.startswith("FLOW_SEGMENT_"):
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            obj = bpy.data.objects.new(name, None)
            element = bonsai.core.root.assign_class(
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
            materials = ifc_file.by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = ifcopenshell.api.run("material.add_material", tool.Ifc.get(), name="Unknown")
            if template == "PROFILESET":
                named_profiles = [p for p in ifc_file.by_type("IfcProfileDef") if p.ProfileName]
                if named_profiles:
                    profile = named_profiles[0]
                else:
                    size = 0.5 / unit_scale
                    profile = ifc_file.create_entity(
                        "IfcRectangleProfileDef", ProfileName="New Profile", ProfileType="AREA", XDim=size, YDim=size
                    )
            else:
                # NOTE: defaults dims are in meters / mm
                # for now default names are hardcoded to mm
                if template == "FLOW_SEGMENT_RECTANGULAR":
                    default_x_dim = 0.4
                    default_y_dim = 0.2
                    profile_name = f"{ifc_class}-{default_x_dim*1000}x{default_y_dim*1000}"
                    profile = ifc_file.create_entity(
                        "IfcRectangleProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        XDim=default_x_dim / unit_scale,
                        YDim=default_y_dim / unit_scale,
                    )
                elif template == "FLOW_SEGMENT_CIRCULAR":
                    default_diameter = 0.1
                    profile_name = f"{ifc_class}-{default_diameter*1000}"
                    profile = ifc_file.create_entity(
                        "IfcCircleProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        Radius=(default_diameter / 2) / unit_scale,
                    )
                elif template == "FLOW_SEGMENT_CIRCULAR_HOLLOW":
                    default_diameter = 0.15
                    default_thickness = 0.005
                    profile_name = f"{ifc_class}-{default_diameter*1000}x{default_thickness*1000}"
                    profile = ifc_file.create_entity(
                        "IfcCircleHollowProfileDef",
                        ProfileName=profile_name,
                        ProfileType="AREA",
                        Radius=(default_diameter / 2) / unit_scale,
                        WallThickness=default_thickness,
                    )

            rel = ifcopenshell.api.run(
                "material.assign_material", ifc_file, products=[element], type="IfcMaterialProfileSet"
            )
            profile_set = rel.RelatingMaterial
            material_profile = ifcopenshell.api.run(
                "material.add_profile", ifc_file, profile_set=profile_set, material=material
            )
            ifcopenshell.api.run(
                "material.assign_profile", ifc_file, material_profile=material_profile, profile=profile
            )

        elif template == "EMPTY":
            obj = bpy.data.objects.new(name, None)
            bonsai.core.root.assign_class(
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

        elif template == "WINDOW":
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type if tool.Ifc.get_schema() != "IFC2X3" else None,
                ifc_class="IfcWindowType" if tool.Ifc.get_schema() != "IFC2X3" else "IfcWindowStyle",
                should_add_representation=False,
            )
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_window()

        elif template == "DOOR":
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type if tool.Ifc.get_schema() != "IFC2X3" else None,
                ifc_class="IfcDoorType" if tool.Ifc.get_schema() != "IFC2X3" else "IfcDoorStyle",
                should_add_representation=False,
            )
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_door()

        elif template == "STAIR":
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class=ifc_class,
                should_add_representation=False,
            )
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_stair()

        elif template == "RAILING":
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class="IfcRailingType",
                should_add_representation=True,
                context=body,
            )
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_railing()

        elif template == "ROOF":
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            element = bonsai.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class="IfcRoofType",
                should_add_representation=True,
                context=body,
            )
            with context.temp_override(active_object=obj):
                bpy.ops.bim.add_roof()

        bpy.ops.bim.load_type_thumbnails(ifc_class=ifc_class)
        props.type_class = props.type_class
        return {"FINISHED"}


class RemoveType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_type"
    bl_label = "Remove Type"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        tool.Geometry.delete_ifc_object(obj)


class RenameType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rename_type"
    bl_label = "Rename Type"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()
    name: bpy.props.StringProperty(name="Name")

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        element.Name = self.name
        if obj:
            tool.Root.set_object_name(obj, element)

    def invoke(self, context, event):
        element = tool.Ifc.get().by_id(self.element)
        self.name = element.Name or "Unnamed"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "name")


class AutoRenameOccurrences(bpy.types.Operator):
    bl_idname = "bim.auto_rename_occurrences"
    bl_label = "Auto Rename Occurrences"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        element_type = tool.Ifc.get_entity(obj)
        if element_type and element_type.is_a("IfcTypeObject"):
            for occurrence in ifcopenshell.util.element.get_types(element_type):
                obj = tool.Ifc.get_object(occurrence)
                occurrence.Name = tool.Model.generate_occurrence_name(element_type, occurrence.is_a())
                if obj:
                    tool.Root.set_object_name(obj, occurrence)
        return {"FINISHED"}


class DuplicateType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_type"
    bl_label = "Duplicate Type"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        if not obj:
            return {"FINISHED"}
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        new = bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)
        new.Name += " Copy"
        bpy.ops.bim.load_type_thumbnails(ifc_class=new.is_a())
        if obj in context.selectable_objects:
            tool.Blender.select_and_activate_single_object(context, new_obj)
        else:
            self.report({"INFO"}, "Type object can't be selected : It may be hidden or in an excluded collection.")
        context.scene.BIMModelProperties.ifc_class = new.is_a()
        context.scene.BIMModelProperties.relating_type_id = str(new_obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}
