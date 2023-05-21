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
import json
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.pset
import ifcopenshell.util.attribute
import blenderbim.bim.schema
import blenderbim.bim.helper
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.pset as core
import blenderbim.core.qto as QtoCore
import blenderbim.bim.module.pset.data
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator
from blenderbim.bim.module.pset.calc_quantity_function_mapper import mapper


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


def get_pset_props(context, obj, obj_type):
    if obj_type == "Object":
        return bpy.data.objects.get(obj).PsetProperties
    elif obj_type == "Material":
        return bpy.data.materials.get(obj).PsetProperties
    elif obj_type == "MaterialSet":
        return bpy.data.objects.get(obj).MaterialSetPsetProperties
    elif obj_type == "MaterialSetItem":
        return bpy.data.objects.get(obj).MaterialSetItemPsetProperties
    elif obj_type == "Task":
        return context.scene.TaskPsetProperties
    elif obj_type == "Resource":
        return context.scene.ResourcePsetProperties
    elif obj_type == "Profile":
        return context.scene.ProfilePsetProperties
    elif obj_type == "WorkSchedule":
        return context.scene.WorkSchedulePsetProperties


class TogglePsetExpansion(bpy.types.Operator, Operator):
    bl_idname = "bim.toggle_pset_expansion"
    bl_label = "Toggle Pset Expansion"
    pset_id: bpy.props.IntProperty()

    def _execute(self, context):
        blenderbim.bim.module.pset.data.is_expanded[
            self.pset_id
        ] = not blenderbim.bim.module.pset.data.is_expanded.setdefault(self.pset_id, True)


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
        self.props = get_pset_props(context, self.obj, self.obj_type)
        self.props.properties.clear()
        ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, self.obj, self.obj_type)

        if self.pset_id:
            pset = tool.Ifc.get().by_id(self.pset_id)
            self.props.active_pset_name = pset.Name
            self.props.active_pset_type = ""
            pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(pset.Name)
        else:
            pset = None
            self.props.active_pset_name = self.pset_name
            self.props.active_pset_type = self.pset_type
            pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(self.pset_name)

        if pset_template:
            self.load_from_pset_template(pset_template, pset)
        else:
            self.load_from_pset_data(pset)

        self.props.active_pset_id = self.pset_id
        return {"FINISHED"}

    def load_from_pset_template(self, pset_template, pset):
        if pset:
            data = ifcopenshell.util.element.get_property_definition(pset)
            del data["id"]
        else:
            data = {}
        for prop_template in pset_template.HasPropertyTemplates:
            if not prop_template.is_a("IfcSimplePropertyTemplate"):
                continue  # Other types not yet supported
            if prop_template.TemplateType == "P_SINGLEVALUE":
                self.load_single_value(pset_template, prop_template, data)
            elif prop_template.TemplateType.startswith("Q_"):
                self.load_single_value(pset_template, prop_template, data)
            elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                self.load_enumerated_value(prop_template, data)

    def load_single_value(self, pset_template, prop_template, data):
        prop = self.props.properties.add()
        prop.name = prop_template.Name
        prop.value_type = "IfcPropertySingleValue"
        metadata = prop.metadata
        metadata.name = prop_template.Name
        metadata.is_null = data.get(prop_template.Name, None) is None
        metadata.is_optional = True
        metadata.is_uri = prop_template.PrimaryMeasureType == "IfcURIReference"
        metadata.has_calculator = bool(mapper.get(pset_template.Name, {}).get(prop_template.Name, None))
        metadata.data_type = self.get_data_type(prop_template)

        if metadata.data_type == "string":
            metadata.string_value = "" if metadata.is_null else str(data[prop_template.Name])
        elif metadata.data_type == "integer":
            metadata.int_value = 0 if metadata.is_null else int(data[prop_template.Name])
        elif metadata.data_type == "float":
            metadata.float_value = 0.0 if metadata.is_null else float(data[prop_template.Name])
        elif metadata.data_type == "boolean":
            metadata.bool_value = False if metadata.is_null else bool(data[prop_template.Name])

        metadata.ifc_class = pset_template.Name
        blenderbim.bim.helper.add_attribute_description(metadata, prop_template)

    def get_data_type(self, prop_template):
        if prop_template.TemplateType in ["Q_LENGTH", "Q_AREA", "Q_VOLUME", "Q_WEIGHT", "Q_TIME"]:
            return "float"
        elif prop_template.TemplateType == "Q_COUNT":
            return "integer"
        return ifcopenshell.util.attribute.get_primitive_type(
            IfcStore.get_schema().declaration_by_name(prop_template.PrimaryMeasureType or "IfcLabel")
        )

    def load_enumerated_value(self, prop_template, data):
        enum_items = [v.wrappedValue for v in prop_template.Enumerators.EnumerationValues]
        selected_enum_items = data.get(prop_template.Name, []) or []

        prop = self.props.properties.add()
        prop.name = prop_template.Name
        prop.value_type = "IfcPropertyEnumeratedValue"
        metadata = prop.metadata
        metadata.name = prop_template.Name
        metadata.is_null = data.get(prop_template.Name, None) is None
        metadata.is_optional = True
        metadata.is_uri = prop_template.PrimaryMeasureType == "IfcURIReference"

        # Cute hack to abuse the metadata to find the Blender data_type
        metadata.set_value(enum_items[0])
        data_type = metadata.get_value_name()

        for enum in enum_items:
            new = prop.enumerated_value.enumerated_values.add()
            setattr(new, data_type, enum)
            new.is_selected = enum in selected_enum_items

    def load_from_pset_data(self, pset):
        if pset.is_a("IfcElementQuantity"):
            props = pset.Quantities
        elif pset.is_a("IfcPropertySet"):
            props = pset.HasProperties
        elif pset.is_a("IfcMaterialProperties") or pset.is_a("IfcProfileProperties"):
            props = pset.Properties

        for prop in props:
            if prop.is_a("IfcPropertyEnumeratedValue"):
                simple_prop = self.props.properties.add()
                simple_prop.value_type = "IfcPropertyEnumeratedValue"
                metadata = simple_prop.metadata
                metadata.name = prop.Name
                metadata.is_null = len(simple_prop.enumerated_value.enumerated_values) == 0
                metadata.is_optional = True
                metadata.set_value(prop.EnumerationReference.EnumerationValues[0].wrappedValue)

                enum_items = [v.wrappedValue for v in prop.EnumerationReference.EnumerationValues]
                selected_enum_items = [v.wrappedValue for v in prop.EnumerationValues]
                data_type = metadata.get_value_name()

                for enum in enum_items:
                    new = simple_prop.enumerated_value.enumerated_values.add()
                    setattr(new, data_type, enum)
                    new.is_selected = enum in selected_enum_items
            else:
                if prop.is_a("IfcPropertySingleValue"):
                    value = prop.NominalValue.wrappedValue
                elif prop.is_a("IfcPhysicalSimpleQuantity"):
                    value = prop[3]
                new_prop = self.props.properties.add()
                metadata = new_prop.metadata
                metadata.set_value(value)
                metadata.name = prop.Name
                metadata.is_null = value is None
                metadata.is_optional = True
                metadata.set_value(metadata.get_value_default() if metadata.is_null else value)


class DisablePsetEditing(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_pset_editing"
    bl_label = "Disable Pset Editing"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        props = get_pset_props(context, self.obj, self.obj_type)
        if props.active_pset_id:
            pset = tool.Ifc.get().by_id(props.active_pset_id)
            ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, self.obj, self.obj_type)
            if tool.Pset.is_pset_empty(pset):
                ifcopenshell.api.run(
                    "pset.remove_pset", tool.Ifc.get(), product=tool.Ifc.get().by_id(ifc_definition_id), pset=pset
                )
        props.active_pset_id = 0
        props.active_pset_name = ""
        props.active_pset_type = ""


class EditPset(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_pset"
    bl_label = "Edit Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()
    pset_id: bpy.props.IntProperty()
    properties: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        objects = tool.Blender.get_selected_objects()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, self.obj, self.obj_type)
        element = tool.Ifc.get().by_id(ifc_definition_id)
        properties = {}

        pset_id = self.pset_id or props.active_pset_id
        if pset_id:
            pset = self.file.by_id(pset_id)
        elif props.active_pset_type == "PSET":
            pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name=props.active_pset_name)
            props.active_pset_id = pset.id()
        elif props.active_pset_type == "QTO":
            pset = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name=props.active_pset_name)
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


        for obj in objects:
            element = blenderbim.tool.Ifc.get_entity(obj)
            pset_list = element.IsDefinedBy
            copy_of_properties = properties.copy()

            for rel in pset_list:
                rel_name = rel.RelatingPropertyDefinition.Name
                if rel.is_a("IfcRelDefinesByProperties") and rel_name == props.active_pset_name:
                    rel_ID = rel.RelatingPropertyDefinition.id()
                    rel_pset = rel.RelatingPropertyDefinition
                    if rel_pset.is_a() in ("IfcPropertySet", "IfcMaterialProperties", "IfcProfileProperties"):
                        ifcopenshell.api.run(
                            "pset.edit_pset",
                            self.file,
                            pset=rel_pset,
                            name=props.active_pset_name,
                            properties=copy_of_properties,
                            pset_template=blenderbim.bim.schema.ifc.psetqto.get_by_name(props.active_pset_name),
                        )
                    else:
                        for key, value in copy_of_properties.items():
                            if isinstance(value, float):
                                copy_of_properties[key] = round(value, 4)
                        ifcopenshell.api.run(
                            "pset.edit_qto",
                            self.file,
                            qto=rel_pset,
                            name=props.active_pset_name,
                            properties=copy_of_properties,
                        )
                        if tool.Cost.has_schedules():
                            tool.Cost.update_cost_items(pset=rel_pset)

        bpy.ops.bim.disable_pset_editing(obj=self.obj, obj_type=self.obj_type)
        tool.Blender.update_viewport()


class RemovePset(bpy.types.Operator, Operator):
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
            props = get_pset_props(context, obj, self.obj_type)
            ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, obj, self.obj_type)
            element = tool.Ifc.get().by_id(ifc_definition_id)
            pset = ifcopenshell.util.element.get_psets(element, should_inherit=False).get(pset_name, None)
            if pset:
                ifcopenshell.api.run(
                    "pset.remove_pset", tool.Ifc.get(), product=element, pset=tool.Ifc.get().by_id(pset["id"])
                )


class AddPset(bpy.types.Operator, Operator):
    bl_idname = "bim.add_pset"
    bl_label = "Add Pset"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        pset_name = get_pset_props(context, self.obj, self.obj_type).pset_name
        if self.obj_type == "Object":
            if context.selected_objects:
                objects = [o.name for o in tool.Blender.get_selected_objects()]
            else:
                objects = [context.active_object.name]
        else:
            objects = [self.obj]
        for obj in objects:
            ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, obj, self.obj_type)
            if not ifc_definition_id:
                continue
            element = tool.Ifc.get().by_id(ifc_definition_id)
            if pset_name in blenderbim.bim.schema.ifc.psetqto.get_applicable_names(element.is_a(), pset_only=True):
                bpy.ops.bim.enable_pset_editing(pset_id=0, pset_name=pset_name, pset_type="PSET", obj=obj, obj_type=self.obj_type)


class AddQto(bpy.types.Operator, Operator):
    bl_idname = "bim.add_qto"
    bl_label = "Add Qto"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Quantity Take Off"
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = get_pset_props(context, self.obj, self.obj_type)
        ifc_definition_id = blenderbim.bim.helper.get_obj_ifc_definition_id(context, self.obj, self.obj_type)
        element = tool.Ifc.get().by_id(ifc_definition_id)
        bpy.ops.bim.enable_pset_editing(pset_id=0, pset_name=props.qto_name, pset_type="QTO", obj=self.obj, obj_type=self.obj_type)


class CalculateQuantity(bpy.types.Operator):
    bl_idname = "bim.calculate_quantity"
    bl_label = "Calculate Quantity"
    bl_options = {"REGISTER", "UNDO"}
    prop: bpy.props.StringProperty()

    def execute(self, context):
        self.qto_calculator = QtoCalculator()
        obj = context.active_object
        prop = obj.PsetProperties.properties.get(self.prop)
        quantity = self.calculate_quantity(obj, context)

        if quantity is None:
            self.report({"ERROR"}, "Could not calculate quantity")
            return {"CANCELLED"}

        prop.metadata.float_value = quantity
        return {"FINISHED"}

    def calculate_quantity(self, obj, context):
        quantity = self.qto_calculator.calculate_quantity(obj.PsetProperties.active_pset_name, self.prop, obj)
        if quantity is None:
            return
        return round(quantity, 3)


class GuessQuantity(bpy.types.Operator):
    bl_idname = "bim.guess_quantity"
    bl_label = "Guess Quantity"
    bl_options = {"REGISTER", "UNDO"}
    prop: bpy.props.StringProperty()

    def execute(self, context):
        self.qto_calculator = QtoCalculator()
        obj = context.active_object
        prop = obj.PsetProperties.properties.get(self.prop)
        prop.metadata.float_value = self.guess_quantity(obj, context)
        return {"FINISHED"}

    def guess_quantity(self, obj, context):
        quantity = self.qto_calculator.guess_quantity(self.prop, [p.name for p in obj.PsetProperties.properties], obj)
        return round(quantity, 3) if quantity is not None else None


class CopyPropertyToSelection(bpy.types.Operator, Operator):
    bl_idname = "bim.copy_property_to_selection"
    bl_label = "Copy Property To Selection"
    name: bpy.props.StringProperty()

    def _execute(self, context):
        pset_id = context.active_object.PsetProperties.active_pset_id
        if pset_id:
            is_pset = tool.Ifc.get().by_id(pset_id).is_a("IfcPropertySet")
        else:
            is_pset = context.active_object.PsetProperties.active_pset_type == "PSET"
        pset_name = context.active_object.PsetProperties.active_pset_name
        prop_value = context.active_object.PsetProperties.properties.get(self.name).metadata.get_value()
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
    bl_label = "Add Edit Rule"
    bl_idname = "bim.add_property_to_edit"
    bl_options = {"REGISTER", "UNDO"}
    option: bpy.props.StringProperty()
    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        if self.index == -1:
            getattr(context.scene, self.option).add()
        else:
            getattr(context.scene, self.option)[self.index].enum_values.add()
        return {"FINISHED"}


class BIM_OT_remove_property_to_edit(bpy.types.Operator):
    bl_label = "Remove Property to Be Renamed"
    bl_idname = "bim.remove_property_to_edit"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()
    index2: bpy.props.IntProperty(default=-1)
    option: bpy.props.StringProperty()

    def execute(self, context):
        if self.index2 == -1:
            getattr(context.scene, self.option).remove(self.index)
        else:
            getattr(context.scene, self.option)[self.index].enum_values.remove(self.index2)
        return {"FINISHED"}


class BIM_OT_clear_list(bpy.types.Operator):
    bl_label = "Clear List of Properties"
    bl_idname = "bim.clear_list"
    bl_options = {"REGISTER", "UNDO"}
    option: bpy.props.StringProperty()

    def execute(self, context):
        getattr(context.scene, self.option).clear()
        return {"FINISHED"}


class BIM_OT_rename_parameters(bpy.types.Operator):
    bl_label = "Rename Parameters"
    bl_idname = "bim.rename_parameters"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Rename parameters that are subclasses of IfcElement"

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props_to_map = context.scene.RenameProperties
        ifc_file = IfcStore.get_file()
        all_ifc_elements = ifc_file.by_type("IfcElement")

        for ifc_element in all_ifc_elements:
            for definition in ifc_element.IsDefinedBy:
                if definition.is_a("IfcRelDefinesByProperties"):
                    prop_set = definition.RelatingPropertyDefinition
                    self.rename_property(prop_set, props_to_map, ifc_element)

        self.report({"INFO"}, "Finished applying changes")
        return {"FINISHED"}

    def rename_property(self, property_set, properties_to_map, ifc_element):
        if property_set.is_a() == "IfcPropertySet":
            property_container = property_set.HasProperties
        elif property_set.is_a() == "IfcElementQuantity":
            property_container = property_set.Quantities

        for obj_prop in property_container:
            for prop2map in properties_to_map:
                if prop2map.pset_name != property_set.Name:
                    continue
                if prop2map.existing_property_name == obj_prop.Name:
                    obj_prop.Name = prop2map.new_property_name


class BIM_OT_add_edit_custom_property(bpy.types.Operator):
    bl_label = "Add or Edit a Custom Property"
    bl_idname = "bim.add_edit_custom_property"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.AddEditProperties

        for obj in tool.Blender.get_selected_objects():
            ifc_definition_id = obj.BIMObjectProperties.ifc_definition_id
            if not ifc_definition_id:
                continue
            ifc_element = tool.Ifc.get().by_id(ifc_definition_id)

            for prop in props:
                value = getattr(prop, prop.get_value_name())
                primary_measure_type = prop.primary_measure_type

                if prop.template_type == "IfcPropertyEnumeratedValue":
                    value_ifc_entity = self.generate_enum_entity(prop)
                elif prop.template_type == "IfcPropertySingleValue":
                    value_ifc_entity = getattr(self.file, f"create{primary_measure_type}")(value)

                new_pset = ifcopenshell.api.run("pset.add_pset", self.file, product=ifc_element, name=prop.pset_name)
                ifcopenshell.api.run(
                    "pset.edit_pset", self.file, pset=new_pset, properties={prop.property_name: value_ifc_entity}
                )
        self.report({"INFO"}, "Finished applying changes")
        return {"FINISHED"}

    def generate_enum_entity(self, prop):
        prop_type = prop.get_value_name()
        prop_enum = self.file.create_entity(
            "IFCPROPERTYENUMERATION",
            Name=prop.property_name,
            EnumerationValues=tuple(
                self.file.create_entity(prop.primary_measure_type, ev[prop_type]) for ev in prop.enum_values
            ),
        )
        prop_enum_value = self.file.create_entity(
            "IFCPROPERTYENUMERATEDVALUE",
            Name=prop.property_name,
            EnumerationValues=tuple(
                self.file.create_entity(prop.primary_measure_type, ev[prop_type])
                for ev in prop.enum_values
                if ev.is_selected == True
            ),
            EnumerationReference=prop_enum,
        )
        return prop_enum_value


class BIM_OT_bulk_remove_psets(bpy.types.Operator):
    bl_label = "Bulk Remove Psets from Selected Objects"
    bl_idname = "bim.bulk_remove_psets"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Bulk remove psets from selected objects"
    index: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.DeletePsets

        for obj in tool.Blender.get_selected_objects():
            ifc_definition_id = obj.BIMObjectProperties.ifc_definition_id
            if not ifc_definition_id:
                continue
            ifc_element = tool.Ifc.get().by_id(ifc_definition_id)
            psets = ifcopenshell.util.element.get_psets(ifc_element)

            for prop in props:
                pset = prop.pset_name
                if pset in psets:
                    try:
                        ifcopenshell.api.run(
                            "pset.remove_pset",
                            self.file,
                            **{
                                "product": self.file.by_id(ifc_definition_id),
                                "pset": self.file.by_id(psets[pset]["id"]),
                            },
                        )
                    except KeyError:
                        pass  # Sometimes the pset id is not found, I'm not sure why this happens though. - vulevukusej

        self.report({"INFO"}, "Finished applying changes")
        return {"FINISHED"}
