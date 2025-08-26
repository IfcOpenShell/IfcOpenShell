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
import json
import ifcopenshell
import ifcopenshell.api.attribute
import ifcopenshell.guid
import ifcopenshell.util.element
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.core.attribute as core
import bonsai.core.spatial
from typing import TYPE_CHECKING, Any, Union, Literal

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute
    import bpy.stub_internal.rna_enums as rna_enums


def get_objs_for_operation(
    operator_properties: "AttributesOperator", context: bpy.types.Context
) -> list[bpy.types.Object]:
    if operator_properties.obj:
        return [bpy.data.objects[operator_properties.obj]]
    if operator_properties.mass_operation:
        return context.selected_objects[:]
    obj = context.active_object
    assert obj
    return [obj]


class AttributesOperator:
    obj: bpy.props.StringProperty(options={"SKIP_SAVE"})
    mass_operation: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        obj: str
        mass_operation: bool

    def invoke(self, context, event):
        self.mass_operation = event.alt
        return self.execute(context)


class EnableEditingAttributes(bpy.types.Operator, AttributesOperator):
    bl_idname = "bim.enable_editing_attributes"
    bl_label = "Enable Editing Attributes"
    bl_description = "ALT + Left Click to enable editing attributes on all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def enable_editing_attribute_on_obj(self, obj: bpy.types.Object) -> None:
        props = tool.Blender.get_object_attribute_props(obj)
        props.attributes.clear()

        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        has_inherited_predefined_type = False
        if not element.is_a("IfcTypeObject") and (element_type := ifcopenshell.util.element.get_type(element)):
            # Allow for None due to https://github.com/buildingSMART/IFC4.3.x-development/issues/818
            has_inherited_predefined_type = ifcopenshell.util.element.get_predefined_type(element_type) not in (
                "NOTDEFINED",
                None,
            )

        lookup_attrs = tool.Attribute.does_ifc_class_support_explorer_lookup(element.is_a())

        def callback(name: str, prop: Union["Attribute", None], data: dict[str, Any]) -> None | Literal[True]:
            if name in ("RefLatitude", "RefLongitude"):
                new = props.attributes.add()
                new.name = name
                new.is_null = data[name] is None
                new.is_optional = True
                new.data_type = "string"
                new.ifc_class = data["type"]
                new.string_value = "" if new.is_null else json.dumps(data[name])
                bonsai.bim.helper.add_attribute_description(new)
                new.description += " The degrees, minutes and seconds should follow this format : [12,34,56]"
            if name in ("PredefinedType", "ObjectType") and has_inherited_predefined_type:
                props.attributes.remove(len(props.attributes) - 1)
                return True
            if lookup_attrs and (name in lookup_attrs):
                new = props.attributes.add()
                new.name = name
                new.ifc_class = data["type"]
                new.data_type = "enum"
                new.is_optional = True
                new.enum_items_dynamic = lookup_attrs[name]
                new.use_explorer_ui = True
                value: Union[ifcopenshell.entity_instance, None] = data[name]
                if value is not None:
                    new.enum_value = str(value.id())

        bonsai.bim.helper.import_attributes(element, props.attributes, callback=callback)
        props.is_editing_attributes = True

    def execute(self, context):
        for obj in get_objs_for_operation(self, context):
            self.enable_editing_attribute_on_obj(obj)
        return {"FINISHED"}


class DisableEditingAttributes(bpy.types.Operator, AttributesOperator):
    bl_idname = "bim.disable_editing_attributes"
    bl_label = "Disable Editing Attributes"
    bl_description = "ALT + Left Click to disable editing attributes on all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def disable_editing_attributes_on_obj(self, obj: bpy.types.Object) -> None:
        props = tool.Blender.get_object_attribute_props(obj)
        props.attributes.clear()
        props.property_unset("is_editing_attributes")

    def execute(self, context):
        for obj in get_objs_for_operation(self, context):
            self.disable_editing_attributes_on_obj(obj)
        return {"FINISHED"}


class EditAttributes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_attributes"
    bl_label = "Edit Attributes"
    bl_description = "Edit the attributes of the active object"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.file = tool.Ifc.get()
        obj = tool.Blender.get_active_object(is_selected=False)
        if not obj or not (element := tool.Ifc.get_entity(obj)):
            return

        def callback(attributes: dict[str, Any], prop: "Attribute") -> None | Literal[True]:
            if prop.name in ("RefLatitude", "RefLongitude"):
                if not prop.is_null:
                    try:
                        attributes[prop.name] = json.loads(prop.string_value)
                    except:
                        attributes[prop.name] = None
                    return True

        props = tool.Blender.get_object_attribute_props(obj)
        attributes = bonsai.bim.helper.export_attributes(props.attributes, callback=callback)
        lookup_attrs = tool.Attribute.does_ifc_class_support_explorer_lookup(element.is_a())
        if lookup_attrs:
            bonsai.bim.helper.process_exported_entity_attribute(attributes, list(lookup_attrs))
        ifcopenshell.api.attribute.edit_attributes(self.file, product=element, attributes=attributes)

        tool.Root.set_object_name(obj, element)
        bpy.ops.bim.disable_editing_attributes(obj=obj.name)

        if tool.Root.is_spatial_element(element):
            bonsai.core.spatial.import_spatial_decomposition(tool.Spatial)


class GenerateGlobalId(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_global_id"
    bl_label = "Regenerate GlobalId"
    bl_description = "Regenerate GlobalId\n\nSHIFT+CLICK to regenerate GlobalIds for all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    use_selected: bpy.props.BoolProperty(name="Use All Selected Objects", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        # using all selected objects on shift+click
        # make sure to use SKIP_SAVE on property, otherwise it might get stuck
        if event.type == "LEFTMOUSE" and event.shift:
            self.use_selected = True
        return self.execute(context)

    def _execute(self, context):
        if self.use_selected:
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if not element or not element.is_a("IfcRoot"):
                    continue
                element.GlobalId = ifcopenshell.guid.new()

        obj = context.active_object
        if not obj or not (props := tool.Blender.get_object_attribute_props(obj)).is_editing_attributes:
            return {"FINISHED"}

        element = tool.Ifc.get_entity(obj)

        if not element or not element.is_a("IfcRoot"):
            return {"FINISHED"}

        if self.use_selected and obj in context.selected_objects:
            # guid value was already regenerated, just update the ui prop
            guid_value = element.GlobalId
        else:
            guid_value = ifcopenshell.guid.new()

        props.attributes["GlobalId"].string_value = guid_value
        return {"FINISHED"}


class CopyAttributeToSelection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_attribute_to_selection"
    bl_label = "Copy Attribute To Selection"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        obj = tool.Blender.get_active_object()
        assert obj
        props = tool.Blender.get_object_attribute_props(obj)
        value = props.attributes[self.name].get_value()
        total = core.copy_attribute_to_selection(
            tool.Ifc, tool.Blender, tool.Root, tool.Spatial, name=self.name, value=value
        )
        self.report({"INFO"}, f"Attribute was successfully copied to {total} elements.")


class ExplorerAddEntity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.explorer_add_entity"
    bl_label = "Add Entity"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context) -> None:
        props = tool.Attribute.get_explorer_props()
        ifc_file = tool.Ifc.get()

        entity = ifc_file.create_entity(props.ifc_class)
        tool.Attribute.refresh_uilist_entities()
        tool.Attribute.enable_editing_entity(entity)
        tool.Attribute.import_entity_attributes(entity)


class ExplorerEnableEditingEntity(bpy.types.Operator):
    bl_idname = "bim.explorer_enable_editing_entity"
    bl_label = "Enable Editing Entity"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        props = tool.Attribute.get_explorer_props()
        ifc_file = tool.Ifc.get()
        assert (active_entity := props.active_entity)
        entity = ifc_file.by_id(active_entity.ifc_definition_id)

        tool.Attribute.disable_editing_entity()
        tool.Attribute.enable_editing_entity(entity)
        tool.Attribute.import_entity_attributes(entity)
        return {"FINISHED"}


class ExplorerDisableEditingEntity(bpy.types.Operator):
    bl_idname = "bim.explorer_disable_editing_entity"
    bl_label = "Disable Editing Entity"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        tool.Attribute.disable_editing_entity()
        return {"FINISHED"}


class ExplorerEditEntity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.explorer_edit_entity"
    bl_label = "Edit Entity"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context) -> None:
        ifc_file = tool.Ifc.get()
        props = tool.Attribute.get_explorer_props()
        entity = ifc_file.by_id(props.editing_entity_id)

        attrs = tool.Attribute.export_entity_attributes()
        for attr, value in attrs.items():
            setattr(entity, attr, value)
        tool.Attribute.refresh_uilist_entities()
        tool.Attribute.disable_editing_entity()


class ExplorerShowUIPopup(bpy.types.Operator):
    bl_idname = "bim.explorer_show_ui_popup"
    bl_label = "Show Explorer UI"
    bl_description = "Show Explorer UI to select element as attribute value or edit it."
    bl_options = {"REGISTER", "UNDO"}

    ifc_class: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]
    """Element IFC class."""
    attribute_name: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]
    """IFC class attribute name."""
    data_path: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]
    """Full data path"""
    preselect_ifc_id: bpy.props.IntProperty(options={"SKIP_SAVE"})  # pyright: ignore[reportRedeclaration]
    """IFC id to preselect in the popup."""

    if TYPE_CHECKING:
        ifc_class: str
        attribute_name: str
        data_path: str
        preselect_ifc_id: int

    def invoke(self, context, event) -> "set[rna_enums.OperatorReturnItems]":
        assert context.window_manager
        assert self.ifc_class and self.attribute_name and self.data_path

        props = tool.Attribute.get_explorer_props()
        props.is_loaded = True
        props.ifc_class = self.get_attribute_type()

        if self.preselect_ifc_id:
            props.active_entity_index = next(
                i for i, e in enumerate(props.entities) if e.ifc_definition_id == self.preselect_ifc_id
            )

        return context.window_manager.invoke_props_dialog(self, width=400)

    def get_attribute_type(self) -> str:
        schema = tool.Ifc.schema()
        entity = schema.declaration_by_name(self.ifc_class).as_entity()
        assert entity
        i = entity.attribute_index(self.attribute_name)
        attr = entity.all_attributes()[i]
        named_type = attr.type_of_attribute().as_named_type()
        assert named_type
        declared = named_type.declared_type()
        return declared.name()

    def draw(self, context) -> None:
        from bonsai.bim.module.attribute.ui import BIM_PT_explorer

        BIM_PT_explorer.draw(self, context, is_popup=True)

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        props = tool.Attribute.get_explorer_props()
        active_entity = props.active_entity
        if active_entity is None:
            self.report({"WARNING"}, "No entity selected.")
            return {"FINISHED"}

        # Apply pending changes for convenience.
        if props.editing_entity_id:
            if props.editing_entity_id == active_entity.ifc_definition_id:
                bpy.ops.bim.explorer_edit_entity()
            else:
                bpy.ops.bim.explorer_disable_editing_entity()

        # Very important to do it after changes applied, otherwise enum might update
        # and index will be pointing to a different element.
        exec(f"{self.data_path} = '{active_entity.ifc_definition_id}'")
        return {"FINISHED"}

    def cancel(self, context: bpy.types.Context) -> None:
        props = tool.Attribute.get_explorer_props()
        if props.editing_entity_id:
            bpy.ops.bim.explorer_disable_editing_entity()
