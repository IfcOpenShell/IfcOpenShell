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


class UnassignType(bpy.types.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        def exclude_callback(attribute):
            return attribute.is_a("IfcProfileDef") and attribute.ProfileName

        self.file = IfcStore.get_file()
        objs = [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element or element.is_a("IfcElementType"):
                continue
            ifcopenshell.api.run("type.unassign_type", self.file, related_object=element)

            active_representation = tool.Geometry.get_active_representation(obj)
            active_context = active_representation.ContextOfItems
            new_active_representation = None

            if element.Representation:
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
                blenderbim.core.geometry.switch_representation(
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
        element = tool.Ifc.get().by_id(self.relating_type)
        obj = tool.Ifc.get_object(element)
        if obj:
            if obj in context.selectable_objects:
                tool.Blender.select_and_activate_single_object(context, obj)
            else:
                self.report({"INFO"}, "Type object can't be selected : It may be hidden or in an excluded collection.")
        # IfcTypeProducts are only used for annotations and not part of the model interface.
        if element.is_a() != "IfcTypeProduct":
            context.scene.BIMModelProperties.ifc_class = element.is_a()
            context.scene.BIMModelProperties.relating_type_id = str(self.relating_type)
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else context.active_object
        relating_type = ifcopenshell.util.element.get_type(tool.Ifc.get_entity(related_object))
        if not relating_type:
            return {"FINISHED"}
        related_objects = ifcopenshell.util.element.get_types(relating_type)
        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if element and element in related_objects:
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
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            obj = bpy.data.objects.new(name, None)
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
            materials = ifc_file.by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = self.add_default_material()
            rel = ifcopenshell.api.run(
                "material.assign_material", ifc_file, product=element, type="IfcMaterialLayerSet"
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

        elif template == "PROFILESET":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            obj = bpy.data.objects.new(name, None)
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
            materials = ifc_file.by_type("IfcMaterial")
            if materials:
                material = materials[0]  # Arbitrarily pick a material
            else:
                material = self.add_default_material()
            named_profiles = [p for p in ifc_file.by_type("IfcProfileDef") if p.ProfileName]
            if named_profiles:
                profile = named_profiles[0]
            else:
                size = 0.5 / unit_scale
                profile = ifc_file.create_entity(
                    "IfcRectangleProfileDef", ProfileName="New Profile", ProfileType="AREA", XDim=size, YDim=size
                )
            rel = ifcopenshell.api.run(
                "material.assign_material", ifc_file, product=element, type="IfcMaterialProfileSet"
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

        elif template == "WINDOW":
            mesh = bpy.data.meshes.new("IfcWindow")
            obj = bpy.data.objects.new(name, mesh)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type if tool.Ifc.get_schema() != "IFC2X3" else None,
                ifc_class="IfcWindowType" if tool.Ifc.get_schema() != "IFC2X3" else "IfcWindowStyle",
                should_add_representation=False,
            )
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.bim.add_window()

        elif template == "DOOR":
            mesh = bpy.data.meshes.new("IfcDoor")
            obj = bpy.data.objects.new(name, mesh)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type if tool.Ifc.get_schema() != "IFC2X3" else None,
                ifc_class="IfcDoorType" if tool.Ifc.get_schema() != "IFC2X3" else "IfcDoorStyle",
                should_add_representation=False,
            )
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.bim.add_door()

        elif template == "STAIR":
            mesh = bpy.data.meshes.new("IfcStairFlight")
            obj = bpy.data.objects.new(name, mesh)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class="IfcStairFlightType",
                should_add_representation=True,
                context=body,
            )
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.bim.add_stair()

        elif template == "RAILING":
            mesh = bpy.data.meshes.new("IfcRailing")
            obj = bpy.data.objects.new(name, mesh)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class="IfcRailingType",
                should_add_representation=True,
                context=body,
            )
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.bim.add_railing()

        elif template == "ROOF":
            mesh = bpy.data.meshes.new("IfcRoof")
            obj = bpy.data.objects.new(name, mesh)
            element = blenderbim.core.root.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                predefined_type=predefined_type,
                ifc_class="IfcRoofType",
                should_add_representation=True,
                context=body,
            )
            bpy.ops.object.select_all(action="DESELECT")
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.bim.add_roof()

        bpy.ops.bim.load_type_thumbnails(ifc_class=ifc_class)
        props.type_class = props.type_class
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
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        element = tool.Ifc.get().by_id(self.element)
        obj = tool.Ifc.get_object(element)
        ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
        if obj:
            tool.Ifc.unlink(obj=obj)
            bpy.data.objects.remove(obj)


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
        new = blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=new_obj)
        new.Name += " Copy"
        bpy.ops.bim.load_type_thumbnails(ifc_class=new.is_a())
        if obj in context.selectable_objects:
            tool.Blender.select_and_activate_single_object(context, new_obj)
        else:
            self.report({"INFO"}, "Type object can't be selected : It may be hidden or in an excluded collection.")
        context.scene.BIMModelProperties.ifc_class = new.is_a()
        context.scene.BIMModelProperties.relating_type_id = str(new_obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class PurgeUnusedTypes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.purge_unused_types"
    bl_label = "Purge Unused Types"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.purge_unused_types(tool.Ifc, tool.Type)
