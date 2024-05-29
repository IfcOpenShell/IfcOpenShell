# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.util.element
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.schema
from typing import Union


class Pset(blenderbim.core.tool.Pset):
    @classmethod
    def get_element_pset(
        cls, element: ifcopenshell.entity_instance, pset_name: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        pset = ifcopenshell.util.element.get_pset(element, pset_name)
        if pset:
            return tool.Ifc.get().by_id(pset["id"])

    @classmethod
    def get_pset_props(cls, obj, obj_type):
        if obj_type == "Object":
            return bpy.data.objects.get(obj).PsetProperties
        elif obj_type == "Material":
            return bpy.context.scene.MaterialPsetProperties
        elif obj_type == "MaterialSet":
            return bpy.data.objects.get(obj).MaterialSetPsetProperties
        elif obj_type == "MaterialSetItem":
            return bpy.data.objects.get(obj).MaterialSetItemPsetProperties
        elif obj_type == "Task":
            return bpy.context.scene.TaskPsetProperties
        elif obj_type == "Resource":
            return bpy.context.scene.ResourcePsetProperties
        elif obj_type == "Profile":
            return bpy.context.scene.ProfilePsetProperties
        elif obj_type == "WorkSchedule":
            return bpy.context.scene.WorkSchedulePsetProperties
        elif obj_type == "Group":
            return bpy.context.scene.GroupPsetProperties

    @classmethod
    def get_pset_name(cls, obj, obj_type, pset_type="PSET"):
        props = cls.get_pset_props(obj, obj_type)
        name = props.pset_name if pset_type == "PSET" else props.qto_name
        if name == "BBIM_CUSTOM":
            return ""
        return name

    @classmethod
    def is_pset_applicable(cls, element: ifcopenshell.entity_instance, pset_name: str) -> bool:
        return bool(
            pset_name
            in blenderbim.bim.schema.ifc.psetqto.get_applicable_names(
                element.is_a(), ifcopenshell.util.element.get_predefined_type(element), pset_only=True
            )
        )

    @classmethod
    def is_pset_empty(cls, pset):
        pset_dict = ifcopenshell.util.element.get_property_definition(pset)
        del pset_dict["id"]
        for value in pset_dict.values():
            if value is not None:
                return False
        return True

    @classmethod
    def enable_pset_editing(cls, pset_id=None, pset_name=None, pset_type=None, obj=None, obj_type=None):
        # TODO REFACTOR ONCE toll/CORE functions are available
        bpy.ops.bim.enable_pset_editing(
            pset_id=0, pset_name=cls.get_pset_name(obj, obj_type), pset_type="PSET", obj=obj, obj_type=obj_type
        )

    @classmethod
    def import_pset_from_existing(cls, pset, props):
        pset_props = []
        if pset.is_a("IfcElementQuantity"):
            pset_props = pset.Quantities
        elif pset.is_a("IfcPropertySet"):
            pset_props = pset.HasProperties
        elif pset.is_a("IfcMaterialProperties") or pset.is_a("IfcProfileProperties"):
            pset_props = pset.Properties

        for prop in pset_props:
            if props.properties.get(prop.Name):
                continue  # This property has already been added from a template
            if prop.is_a("IfcPropertyEnumeratedValue"):
                simple_prop = props.properties.add()
                simple_prop.name = prop.Name
                simple_prop.value_type = "IfcPropertyEnumeratedValue"
                metadata = simple_prop.metadata
                metadata.name = prop.Name
                metadata.is_null = len(simple_prop.enumerated_value.enumerated_values) == 0
                metadata.is_optional = True
                metadata.set_value(prop.EnumerationReference.EnumerationValues[0].wrappedValue)

                enum_items = [v.wrappedValue for v in prop.EnumerationReference.EnumerationValues]
                selected_enum_items = [v.wrappedValue for v in prop.EnumerationValues]
                data_type = metadata.get_value_name(display_only=True)

                for enum in enum_items:
                    new = simple_prop.enumerated_value.enumerated_values.add()
                    setattr(new, data_type, enum)
                    new.is_selected = enum in selected_enum_items
            else:
                if prop.is_a("IfcPropertySingleValue"):
                    value = prop.NominalValue.wrappedValue if prop.NominalValue else None
                elif prop.is_a("IfcPhysicalSimpleQuantity"):
                    value = prop[3]
                new_prop = props.properties.add()
                new_prop.name = prop.Name
                metadata = new_prop.metadata
                metadata.set_value(value)
                metadata.name = prop.Name
                metadata.is_null = value is None
                metadata.is_optional = True
                metadata.set_value(metadata.get_value_default() if metadata.is_null else value)

    @classmethod
    def get_prop_template_primitive_type(cls, prop_template):
        if prop_template.TemplateType in ["Q_LENGTH", "Q_AREA", "Q_VOLUME", "Q_WEIGHT", "Q_TIME"]:
            return "float"
        elif prop_template.TemplateType == "Q_COUNT":
            return "integer"
        return ifcopenshell.util.attribute.get_primitive_type(
            tool.Ifc.schema().declaration_by_name(prop_template.PrimaryMeasureType or "IfcLabel")
        )

    @classmethod
    def import_enumerated_value_from_template(cls, prop_template, data, props):
        enum_items = [v.wrappedValue for v in prop_template.Enumerators.EnumerationValues]
        selected_enum_items = data.get(prop_template.Name, []) or []

        prop = props.properties.add()
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

    @classmethod
    def import_single_value_from_template(cls, pset_template, prop_template, data, props):
        prop = props.properties.add()
        prop.name = prop_template.Name
        prop.value_type = "IfcPropertySingleValue"
        metadata = prop.metadata
        metadata.name = prop_template.Name
        metadata.is_null = data.get(prop_template.Name, None) is None
        metadata.is_optional = True
        metadata.is_uri = prop_template.PrimaryMeasureType == "IfcURIReference"
        metadata.data_type = cls.get_prop_template_primitive_type(prop_template)

        special_type = ""
        if (
            prop_template.PrimaryMeasureType
            in (
                "IfcPositiveLengthMeasure",
                "IfcLengthMeasure",
            )
            or prop_template.TemplateType == "Q_LENGTH"
        ):
            special_type = "LENGTH"
        elif prop_template.PrimaryMeasureType == "IfcAreaMeasure" or prop_template.TemplateType == "Q_AREA":
            special_type = "AREA"
        elif prop_template.PrimaryMeasureType == "IfcVolumeMeasure" or prop_template.TemplateType == "Q_VOLUME":
            special_type = "VOLUME"
        metadata.special_type = special_type

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

    @classmethod
    def import_pset_from_template(cls, pset_template, pset, props):
        if pset:
            data = ifcopenshell.util.element.get_property_definition(pset)
            del data["id"]
        else:
            data = {}
        for prop_template in pset_template.HasPropertyTemplates:
            if not prop_template.is_a("IfcSimplePropertyTemplate"):
                continue  # Other types not yet supported
            if prop_template.TemplateType == "P_SINGLEVALUE":
                cls.import_single_value_from_template(pset_template, prop_template, data, props)
            elif prop_template.TemplateType.startswith("Q_"):
                cls.import_single_value_from_template(pset_template, prop_template, data, props)
            elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                cls.import_enumerated_value_from_template(prop_template, data, props)
            else:
                # NOTE: currently unsupported types:
                # - P_BOUNDEDVALUE
                # - P_LISTVALUE
                # - P_REFERENCEVALUE
                # - P_TABLEVALUE
                pass

    @classmethod
    def clear_blender_pset_properties(cls, props):
        props.properties.clear()

    @classmethod
    def set_active_pset(cls, props, pset, has_template):
        props.active_pset_id = pset.id()
        props.active_pset_name = pset.Name
        props.active_pset_has_template = has_template

    @classmethod
    def enable_proposed_pset(cls, props, pset_name, pset_type, has_template):
        props.active_pset_id = 0
        props.active_pset_name = pset_name or "My_Data"
        props.active_pset_type = pset_type
        props.active_pset_has_template = has_template

    @classmethod
    def get_pset_template(cls, name):
        return blenderbim.bim.schema.ifc.psetqto.get_by_name(name)

    @classmethod
    def add_proposed_property(cls, name, value, props):
        if props.properties.get(name):
            return
        prop = props.properties.add()
        prop.name = name
        metadata = prop.metadata
        metadata.set_value(value)
        metadata.name = name
        metadata.is_null = value is None
        metadata.is_optional = True
        metadata.set_value(metadata.get_value_default() if metadata.is_null else value)

    @classmethod
    def cast_string_to_primitive(cls, value: str):
        value = value.strip()
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.lower() == "null" or value == "":
            return None
        try:
            value = int(value)
            return value
        except:
            try:
                value = float(value)
                return value
            except:
                return value
        return value
