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
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.util.element
import bonsai.bim.schema
import bonsai.tool as tool
import bonsai.core.pset as core
import bonsai.bim.module.pset.data
from bonsai.bim.ifc import IfcStore
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.pset.prop import RenamePropertyEntry, AddEditPropertyEntry


class TogglePsetExpansion(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_pset_expansion"
    bl_label = "Toggle Pset Expansion"
    pset_id: bpy.props.IntProperty()

    def _execute(self, context):
        bonsai.bim.module.pset.data.is_expanded[self.pset_id] = not bonsai.bim.module.pset.data.is_expanded.setdefault(
            self.pset_id, True
        )


class EnablePsetEditing(bpy.types.Operator):
    bl_idname = "bim.enable_pset_editing"
    bl_label = "Enable Pset Editing"
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()
    pset_name: bpy.props.StringProperty()
    pset_type: bpy.props.StringProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        if self.pset_id:
            pset = tool.Ifc.get().by_id(self.pset_id)
            self.pset_name = pset.Name
        else:
            pset = None

        core.enable_pset_editing(tool.Pset, pset, self.pset_name, self.pset_type, self.obj, self.obj_type)
        return {"FINISHED"}


class DisablePsetEditing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_pset_editing"
    bl_label = "Disable Pset Editing"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        props = tool.Pset.get_pset_props(self.obj, self.obj_type)
        if props.active_pset_id:
            pset = tool.Ifc.get().by_id(props.active_pset_id)
            ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(self.obj, self.obj_type, context)
            if tool.Pset.is_pset_empty(pset):
                ifcopenshell.api.pset.remove_pset(
                    tool.Ifc.get(), product=tool.Ifc.get().by_id(ifc_definition_id), pset=pset
                )
        props.active_pset_id = 0
        props.active_pset_name = ""
        props.active_pset_type = "-"


class EditPset(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_pset"
    bl_label = "Edit Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()
    pset_id: bpy.props.IntProperty()
    properties: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Pset.get_pset_props(self.obj, self.obj_type)
        ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(self.obj, self.obj_type, context)
        element = tool.Ifc.get().by_id(ifc_definition_id)
        properties = {}

        pset_id = self.pset_id or props.active_pset_id
        if pset_id:
            pset = self.file.by_id(pset_id)
        elif props.active_pset_type == "PSET":
            pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name=props.active_pset_name)
            props.active_pset_id = pset.id()
        elif props.active_pset_type == "QTO":
            pset = ifcopenshell.api.pset.add_qto(self.file, product=element, name=props.active_pset_name)
            props.active_pset_id = pset.id()

        if self.properties:
            properties = json.loads(self.properties)
        else:
            for prop in props.properties:
                if prop.value_type == "IfcPropertySingleValue":
                    properties[prop.metadata.name] = prop.metadata.get_value()
                elif prop.value_type == "IfcPropertyEnumeratedValue":
                    value_name = prop.metadata.get_value_name()
                    properties[prop.metadata.name] = [
                        e[value_name] for e in prop.enumerated_value.enumerated_values if e.is_selected
                    ]

        if pset.is_a() in ("IfcPropertySet", "IfcMaterialProperties", "IfcProfileProperties"):
            ifcopenshell.api.pset.edit_pset(
                self.file,
                pset=pset,
                name=props.active_pset_name,
                properties=properties,
                pset_template=bonsai.bim.schema.ifc.psetqto.get_by_name(props.active_pset_name),
            )
        else:
            for key, value in properties.items():
                if value is None:
                    continue
                if isinstance(value, float):
                    properties[key] = round(value, 4)
                elif not isinstance(value, int):
                    properties[key] = 0
            ifcopenshell.api.pset.edit_qto(
                self.file,
                qto=pset,
                name=props.active_pset_name,
                properties=properties,
            )
            if tool.Cost.has_schedules():
                tool.Cost.update_cost_items(pset=pset)
        bpy.ops.bim.disable_pset_editing(obj=self.obj, obj_type=self.obj_type)
        tool.Blender.update_viewport()


class RemovePset(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_pset"
    bl_label = "Remove Pset"
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in tool.Blender.get_selected_objects()]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]
        pset_name = tool.Ifc.get().by_id(self.pset_id).Name
        for obj in objects:
            props = tool.Pset.get_pset_props(obj, self.obj_type)
            ifc_definition_id = tool.Blender.get_obj_ifc_definition_id(obj, self.obj_type, context)
            element = tool.Ifc.get().by_id(ifc_definition_id)
            pset = ifcopenshell.util.element.get_psets(element, should_inherit=False).get(pset_name, None)
            if pset:
                ifcopenshell.api.pset.remove_pset(
                    tool.Ifc.get(), product=element, pset=tool.Ifc.get().by_id(pset["id"])
                )


class AddPset(bpy.types.Operator):
    bl_idname = "bim.add_pset"
    bl_label = "Add Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        core.add_pset(tool.Ifc, tool.Pset, tool.Blender, obj_name=self.obj, obj_type=self.obj_type)
        return {"FINISHED"}


class UnsharePset(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unshare_pset"
    bl_label = "Unshare Pset"
    bl_description = (
        "Click to copy a pset as linked only to the selected objects. "
        "If multiple objects are selected, each will get a separate pset copy.\n\n"
        "Otherwise changing a pset shared by multiple elements "
        "will change it's properties for all the elements it's linked to, not just for the active object"
    )
    bl_options = {"REGISTER", "UNDO"}
    description_: bpy.props.StringProperty(name="Custom Tooltip Description")
    pset_id: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        if not properties.description_:
            return cls.bl_description
        return f"{properties.description_}{cls.bl_description}"

    def _execute(self, context):
        core.unshare_pset(tool.Ifc, tool.Pset, self.obj_type, self.obj, self.pset_id)


class AddQto(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_qto"
    bl_label = "Add Qto"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Quantity Take Off"
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        qto_name = tool.Pset.get_pset_name(self.obj, self.obj_type, pset_type="QTO")
        bpy.ops.bim.enable_pset_editing(
            pset_id=0, pset_name=qto_name, pset_type="QTO", obj=self.obj, obj_type=self.obj_type
        )


class CopyPropertyToSelection(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_property_to_selection"
    bl_label = "Copy Property To Selection"
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        name: str

    def _execute(self, context):
        assert (obj := context.active_object)
        props = tool.Pset.get_pset_props(obj.name, "Object")
        pset_id = props.active_pset_id
        if pset_id:
            is_pset = tool.Ifc.get().by_id(pset_id).is_a("IfcPropertySet")
        else:
            is_pset = props.active_pset_type == "PSET"
        pset_name = props.active_pset_name
        prop = props.properties[self.name]
        if prop.value_type == "IfcPropertySingleValue":
            prop_value = prop.metadata.get_value()
        elif prop.value_type == "IfcPropertyEnumeratedValue":
            value_name = prop.metadata.get_value_name()
            prop_value = [e[value_name] for e in prop.enumerated_value.enumerated_values if e.is_selected]
        else:
            self.report({"ERROR"}, f"Unsupport value type: '{prop.value_type}'.")
            return {"CANCELLED"}

        for obj in tool.Blender.get_selected_objects():
            core.copy_property_to_selection(
                tool.Ifc,
                tool.Pset,
                obj=obj,
                is_pset=is_pset,
                pset_name=pset_name,
                prop_name=self.name,
                prop_value=prop_value,
            )


class BIM_OT_add_property_to_edit(bpy.types.Operator):
    bl_label = "Add Property to Edit"
    bl_idname = "bim.add_property_to_edit"
    bl_options = {"REGISTER", "UNDO"}
    option: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=[(t, t, "") for t in tool.Pset.BULK_OPERATION_TYPES],
    )
    index: bpy.props.IntProperty(default=-1)  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        option: tool.Pset.BulkOperationType
        index: int

    @classmethod
    def description(cls, context: bpy.types.Context, properties: bpy.types.OperatorProperties) -> str:
        return f"Add property entry to for bulk operation '{properties.option}'."

    def execute(self, context):
        if self.index == -1:
            tool.Pset.get_bulk_operation_collection(self.option).add()
        else:
            assert self.option == "ADD_EDIT"
            props = tool.Pset.get_global_pset_props()
            props.psets_to_add_edit[self.index].enum_values.add()
        return {"FINISHED"}


class BIM_OT_remove_property_to_edit(bpy.types.Operator):
    bl_label = "Remove Property from Editing"
    bl_idname = "bim.remove_property_to_edit"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]
    index2: bpy.props.IntProperty(default=-1)  # pyright: ignore[reportRedeclaration]
    option: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=[(t, t, "") for t in tool.Pset.BULK_OPERATION_TYPES],
    )

    if TYPE_CHECKING:
        index: int
        index2: int
        option: tool.Pset.BulkOperationType

    @classmethod
    def description(cls, context: bpy.types.Context, properties: bpy.types.OperatorProperties) -> str:
        return f"Remove property entry from bulk operation '{properties.option}'."

    def execute(self, context):
        if self.index2 == -1:
            tool.Pset.get_bulk_operation_collection(self.option).remove(self.index)
        else:
            assert self.option == "ADD_EDIT"
            props = tool.Pset.get_global_pset_props()
            props.psets_to_add_edit[self.index].enum_values.remove(self.index2)
        return {"FINISHED"}


class BIM_OT_bulk_edit_clear_list(bpy.types.Operator):
    bl_label = "Clear List of Properties"
    bl_idname = "bim.pset_bulk_edit_clear_list"
    bl_options = {"REGISTER", "UNDO"}
    option: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=[(t, t, "") for t in tool.Pset.BULK_OPERATION_TYPES],
    )

    if TYPE_CHECKING:
        option: tool.Pset.BulkOperationType

    def execute(self, context):
        tool.Pset.get_bulk_operation_collection(self.option).clear()
        return {"FINISHED"}


class BIM_OT_pset_bulk_rename_parameters(bpy.types.Operator, tool.Ifc.Operator):
    bl_label = "Rename Parameters"
    bl_idname = "bim.pset_bulk_rename_parameters"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Rename pset properties for all IfcElements"

    def _execute(self, context):
        props_to_map = tool.Pset.get_global_pset_props().psets_to_rename
        ifc_file = tool.Ifc.get()
        all_ifc_elements = ifc_file.by_type("IfcElement")

        properties_map: defaultdict[str, dict[str, str]] = defaultdict(dict)
        """pset_name -> {old_name -> new_name}"""
        for p in props_to_map:
            properties_map[p.name][p.existing_property_name] = p.new_property_name

        props_renamed = 0
        for ifc_element in all_ifc_elements:
            for definition in ifc_element.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    prop_set = definition.RelatingPropertyDefinition
                    props_renamed += self.rename_property(prop_set, properties_map)

        self.report({"INFO"}, f"Finished applying changes, {props_renamed} properties renamed.")
        return {"FINISHED"}

    def rename_property(
        self,
        property_set: ifcopenshell.entity_instance,
        pset_remap: dict[str, dict[str, str]],
    ) -> int:
        props_renamed = 0
        pset_name = property_set.Name
        if pset_name not in pset_remap:
            return props_renamed

        properties_remap = pset_remap[pset_name]
        property_container: tuple[ifcopenshell.entity_instance, ...]
        if property_set.is_a() == "IfcPropertySet":
            property_container = property_set.HasProperties
        elif property_set.is_a() == "IfcElementQuantity":
            property_container = property_set.Quantities
        else:
            assert False

        for obj_prop in property_container:
            prop_name = obj_prop.Name
            if prop_name not in properties_remap:
                continue
            obj_prop.Name = properties_remap[prop_name]
            props_renamed += 1
        return props_renamed


class BIM_OT_add_edit_custom_property(bpy.types.Operator, tool.Ifc.Operator):
    bl_label = "Add or Edit a Custom Property"
    bl_idname = "bim.add_edit_custom_property"
    bl_description = "Edit pset properties for selected objects."
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        entries = tool.Pset.get_global_pset_props().psets_to_add_edit

        elements_changed = 0
        for obj in tool.Blender.get_selected_objects():
            ifc_element = tool.Ifc.get_entity(obj)
            if not ifc_element:
                continue

            for prop in entries:
                value = getattr(prop, prop.get_value_name())
                primary_measure_type = prop.primary_measure_type

                if prop.template_type == "IfcPropertyEnumeratedValue":
                    value_ifc_entity = self.generate_enum_entity(prop)
                elif prop.template_type == "IfcPropertySingleValue":
                    value_ifc_entity = self.file.create_entity(primary_measure_type, value)
                else:
                    assert False

                new_pset = ifcopenshell.api.pset.add_pset(self.file, product=ifc_element, name=prop.pset_name)
                ifcopenshell.api.pset.edit_pset(self.file, pset=new_pset, properties={prop.name: value_ifc_entity})

            if entries:
                elements_changed += 1
        self.report({"INFO"}, f"Finished applying changes, {elements_changed} elements changed.")
        return {"FINISHED"}

    def generate_enum_entity(self, prop: "AddEditPropertyEntry") -> ifcopenshell.entity_instance:
        prop_type = prop.get_value_name()
        prop_enum = self.file.create_entity(
            "IFCPROPERTYENUMERATION",
            Name=prop.name,
            EnumerationValues=tuple(
                self.file.create_entity(prop.primary_measure_type, ev[prop_type]) for ev in prop.enum_values
            ),
        )
        prop_enum_value = self.file.create_entity(
            "IFCPROPERTYENUMERATEDVALUE",
            Name=prop.name,
            EnumerationValues=tuple(
                self.file.create_entity(prop.primary_measure_type, ev[prop_type])
                for ev in prop.enum_values
                if ev.is_selected == True
            ),
            EnumerationReference=prop_enum,
        )
        return prop_enum_value


class BIM_OT_bulk_remove_psets(bpy.types.Operator, tool.Ifc.Operator):
    bl_label = "Bulk Remove Psets from Selected Objects"
    bl_idname = "bim.bulk_remove_psets"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Bulk remove psets from selected objects"
    index: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Pset.get_global_pset_props()

        pset_names_to_delete = {p.name for p in props.psets_to_delete}
        psets_removed = 0

        for obj in tool.Blender.get_selected_objects():
            ifc_element = tool.Ifc.get_entity(obj)
            if not ifc_element:
                continue
            psets = ifcopenshell.util.element.get_psets(ifc_element)

            for pset_name, pset_data in psets.items():
                if pset_name not in pset_names_to_delete:
                    continue

                ifcopenshell.api.pset.remove_pset(
                    self.file,
                    product=ifc_element,
                    pset=self.file.by_id(pset_data["id"]),
                )
                psets_removed += 1

        self.report({"INFO"}, f"Finished applying changes, {psets_removed} psets removed.")
        return {"FINISHED"}


class AddProposedProp(bpy.types.Operator):
    bl_idname = "bim.add_proposed_prop"
    bl_label = "Add Proposed Prop"
    bl_description = (
        "Add proposed property to the custom property set.\n\n"
        "Property type will be deduced from the provided value. Possible types:\n"
        "- provide an integer or a float to create integer/real property\n"
        "- 'true', 'false' to add a boolean property\n"
        "- 'null' or '' (empty value) to add a null property\n"
        "- any other value will be added as a string property"
    )
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    prop_value: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        description = "Add proposed property to the custom property set.\n\n"
        props = tool.Pset.get_pset_props(properties.obj, properties.obj_type)
        if props.active_pset_type == "PSET":
            description += (
                "Property type will be deduced from the provided value. Possible types:\n"
                "- provide an integer or a float to create integer/real property\n"
                "- 'true', 'false' to add a boolean property\n"
                "- 'null' or '' (empty value) to add a null property\n"
                "- any other value will be added as a string property"
            )
        else:
            from ifcopenshell.api.pset.edit_qto import FLOAT_TYPE_KEYWORDS

            description += (
                "Property type will be deduced from the provided value and property name. Possible types:\n"
                "- Integer values - Count type\n"
                "- Float values - will try to match one of the keywords below in prop name, "
                "otherwise will default to Length type\n\n"
                "Types and their keywords:\n"
            )
            for prop_type, keywords in FLOAT_TYPE_KEYWORDS:
                description += f"- {prop_type} - {', '.join(keywords)}\n"
            description = description.rstrip()  # Strip last newline.
        return description

    def execute(self, context):
        res = core.add_proposed_prop(tool.Pset, self.obj, self.obj_type, self.prop_name, self.prop_value)
        if res:
            self.report({"ERROR"}, res)
            return {"CANCELLED"}
        return {"FINISHED"}


class SavePsetAsTemplate(bpy.types.Operator, tool.PsetTemplate.PsetTemplateOperator):
    bl_idname = "bim.save_pset_as_template"
    bl_label = "Save Pset As Template"
    bl_description = "Save the provided pset as a pset template"
    bl_options = {"REGISTER", "UNDO"}
    pset_id: bpy.props.IntProperty()

    def invoke(self, context, event):
        props = tool.PsetTemplate.get_pset_template_props()
        if tool.Blender.get_enum_safe(props, "pset_template_files") is None:
            self.report({"ERROR"}, "No template files found. You can create one in Property Set Templates UI.")
            return {"CANCELLED"}
        return context.window_manager.invoke_props_dialog(self, width=250)

    def draw(self, context):
        props = tool.PsetTemplate.get_pset_template_props()
        self.layout.prop(props, "pset_template_files", text="Template File")

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        pset = ifc_file.by_id(self.pset_id)
        template_file = IfcStore.pset_template_file
        assert template_file

        tool.PsetTemplate.add_pset_as_template(pset, template_file)

        template_file.write(IfcStore.pset_template_path)
        bonsai.bim.handler.refresh_ui_data()
        bonsai.bim.schema.reload(ifc_file.schema)
