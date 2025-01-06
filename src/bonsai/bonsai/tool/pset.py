# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.schema
from typing import Union, Literal, Any
from typing_extensions import assert_never


class Pset(bonsai.core.tool.Pset):
    PSET_TYPE = Literal["PSET", "QTO"]

    @classmethod
    def get_element_pset(
        cls, element: ifcopenshell.entity_instance, pset_name: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        pset = ifcopenshell.util.element.get_pset(element, pset_name)
        if pset:
            return tool.Ifc.get().by_id(pset["id"])

    @classmethod
    def get_pset_props(cls, obj: str, obj_type: tool.Ifc.OBJECT_TYPE) -> bpy.types.PropertyGroup:
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
        assert_never(obj_type)

    @classmethod
    def get_pset_name(cls, obj: str, obj_type: tool.Ifc.OBJECT_TYPE, pset_type: PSET_TYPE = "PSET") -> str:
        props = cls.get_pset_props(obj, obj_type)
        name = props.pset_name if pset_type == "PSET" else props.qto_name
        if name == "BBIM_CUSTOM":
            return ""
        return name

    @classmethod
    def is_pset_applicable(cls, element: ifcopenshell.entity_instance, pset_name: str) -> bool:
        if element.is_a("IfcMaterialDefinition"):
            predefined_type = getattr(element, "Category", None)
        else:
            predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        return bool(
            pset_name
            in bonsai.bim.schema.ifc.psetqto.get_applicable_names(element.is_a(), predefined_type, pset_only=True)
        )

    @classmethod
    def is_pset_empty(cls, pset: ifcopenshell.entity_instance) -> bool:
        pset_dict = ifcopenshell.util.element.get_property_definition(pset)
        del pset_dict["id"]
        for value in pset_dict.values():
            if value is not None:
                return False
        return True

    @classmethod
    def enable_pset_editing(
        cls, pset_id: int, pset_name: str, pset_type: PSET_TYPE, obj: str, obj_type: tool.Ifc.OBJECT_TYPE
    ) -> None:
        # TODO REFACTOR ONCE tool/CORE functions are available
        bpy.ops.bim.enable_pset_editing(
            pset_id=0, pset_name=cls.get_pset_name(obj, obj_type), pset_type="PSET", obj=obj, obj_type=obj_type
        )

    @classmethod
    def get_special_type_for_prop(cls, prop_or_prop_template: ifcopenshell.entity_instance) -> str:
        special_type = ""
        if prop_or_prop_template.is_a("IfcPropertyTemplate"):
            primary_measure_type = prop_or_prop_template.PrimaryMeasureType
            template_type = prop_or_prop_template.TemplateType
            if primary_measure_type in ("IfcPositiveLengthMeasure", "IfcLengthMeasure") or template_type == "Q_LENGTH":
                special_type = "LENGTH"
            elif primary_measure_type == "IfcAreaMeasure" or template_type == "Q_AREA":
                special_type = "AREA"
            elif primary_measure_type == "IfcVolumeMeasure" or template_type == "Q_VOLUME":
                special_type = "VOLUME"
        else:
            if prop_or_prop_template.is_a("IfcPropertySingleValue"):
                value = prop_or_prop_template.NominalValue
                if value is not None:
                    value_type = value.is_a()
                    if value_type in ("IfcLengthMeasure", "IfcPositiveLengthMeasure"):
                        special_type = "LENGTH"
                    elif value_type == "IfcAreaMeasure":
                        special_type = "AREA"
                    elif value_type == "IfcVolumeMeasure":
                        special_type = "VOLUME"
            elif prop_or_prop_template.is_a("IfcPhysicalSimpleQuantity"):
                prop_class = prop_or_prop_template.is_a()
                if prop_class == "IfcQuantityArea":
                    special_type = "AREA"
                elif prop_class == "IfcQuantityVolume":
                    special_type = "VOLUME"
                elif prop_class == "IfcQuantityLength":
                    special_type = "LENGTH"
        return special_type

    @classmethod
    def import_pset_from_existing(cls, pset: ifcopenshell.entity_instance, props: bpy.types.PropertyGroup) -> None:
        pset_props = []
        if pset.is_a("IfcElementQuantity"):
            pset_props = pset.Quantities
        elif pset.is_a("IfcPropertySet"):
            pset_props = pset.HasProperties
        elif pset.is_a("IfcMaterialProperties") or pset.is_a("IfcProfileProperties"):
            pset_props = pset.Properties

        for prop in sorted(pset_props, key=lambda p: p.Name):
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
                enum_reference = prop.EnumerationReference
                selected_enum_items = [v.wrappedValue for v in (prop.EnumerationValues or ())]

                # If there is no reference, then just use the current values.
                if enum_reference is None:
                    enum_items = selected_enum_items
                else:
                    enum_items = [v.wrappedValue for v in enum_reference.EnumerationValues]

                # In theory there could be no reference and no current values,
                # nothing to show then, I guess.
                if not enum_items:
                    continue

                # Trigger metadata to detect data_type.
                metadata.set_value(enum_items[0])
                data_type = metadata.get_value_name()

                # Fill enum items.
                for enum in enum_items:
                    new = simple_prop.enumerated_value.enumerated_values.add()
                    setattr(new, data_type, enum)
                    new.is_selected = enum in selected_enum_items
            else:
                if prop.is_a("IfcPropertySingleValue"):
                    value = prop.NominalValue.wrappedValue if prop.NominalValue else None
                elif prop.is_a("IfcPhysicalSimpleQuantity"):
                    value = prop[3]
                else:
                    assert False
                new_prop = props.properties.add()
                new_prop.name = prop.Name
                metadata = new_prop.metadata
                metadata.set_value(value)
                metadata.name = prop.Name
                metadata.is_null = value is None
                metadata.is_optional = True
                metadata.special_type = cls.get_special_type_for_prop(prop)
                metadata.set_value(metadata.get_value_default() if metadata.is_null else value)

    @classmethod
    def get_prop_template_primitive_type(cls, prop_template: ifcopenshell.entity_instance) -> str:
        if prop_template.TemplateType in ["Q_LENGTH", "Q_AREA", "Q_VOLUME", "Q_WEIGHT", "Q_TIME"]:
            return "float"
        elif prop_template.TemplateType == "Q_COUNT":
            return "integer"
        return ifcopenshell.util.attribute.get_primitive_type(
            tool.Ifc.schema().declaration_by_name(prop_template.PrimaryMeasureType or "IfcLabel")
        )

    @classmethod
    def get_selected_pset_elements(
        cls, obj_name: str, obj_type: tool.Ifc.OBJECT_TYPE, pset: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
        elements: list[ifcopenshell.entity_instance]

        if obj_type == "Object":
            elements = [
                element
                for obj in tool.Blender.get_selected_objects()
                if (element := tool.Ifc.get_entity(obj)) and element in pset_elements
            ]
        else:
            element_id = tool.Blender.get_obj_ifc_definition_id(obj_name, obj_type)
            assert element_id
            elements = [ifc_file.by_id(element_id)]

        return elements

    @classmethod
    def import_enumerated_value_from_template(
        cls, prop_template: ifcopenshell.entity_instance, data: dict[str, Any], props: bpy.types.PropertyGroup
    ) -> None:
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
    def import_single_value_from_template(
        cls,
        pset_template: ifcopenshell.entity_instance,
        prop_template: ifcopenshell.entity_instance,
        data: dict[str, Any],
        props: bpy.types.PropertyGroup,
    ) -> None:
        prop = props.properties.add()
        prop.name = prop_template.Name
        prop.value_type = "IfcPropertySingleValue"
        metadata = prop.metadata
        metadata.name = prop_template.Name
        metadata.is_null = data.get(prop_template.Name, None) is None
        metadata.is_optional = True
        metadata.is_uri = prop_template.PrimaryMeasureType == "IfcURIReference"
        metadata.data_type = cls.get_prop_template_primitive_type(prop_template)
        metadata.special_type = cls.get_special_type_for_prop(prop_template)

        if metadata.data_type == "string":
            metadata.string_value = "" if metadata.is_null else str(data[prop_template.Name])
        elif metadata.data_type == "integer":
            metadata.int_value = 0 if metadata.is_null else int(data[prop_template.Name])
        elif metadata.data_type == "float":
            metadata.float_value = 0.0 if metadata.is_null else float(data[prop_template.Name])
        elif metadata.data_type == "boolean":
            metadata.bool_value = False if metadata.is_null else bool(data[prop_template.Name])

        metadata.ifc_class = pset_template.Name
        bonsai.bim.helper.add_attribute_description(metadata, prop_template)

    @classmethod
    def import_pset_from_template(
        cls,
        pset_template: ifcopenshell.entity_instance,
        pset: Union[ifcopenshell.entity_instance, None],
        props: bpy.types.PropertyGroup,
    ) -> None:
        if pset:
            data = ifcopenshell.util.element.get_property_definition(pset, verbose=True)
            del data["id"]
        else:
            data = {}
        simplified_data = {prop_name: prop_data["value"] for prop_name, prop_data in data.items()}

        # For every prop we first ensure that existing prop value type matches the template value type
        # to prevent data loss and error casting data.
        # Property will be added later by import_pset_from_existing.
        for prop_template in sorted(pset_template.HasPropertyTemplates, key=lambda p: p.Name):
            if not prop_template.is_a("IfcSimplePropertyTemplate"):
                continue  # Other types not yet supported
            prop_data = data.get(prop_template.Name)
            if prop_template.TemplateType == "P_SINGLEVALUE":
                if prop_data:
                    if prop_data["class"] != "IfcPropertySingleValue":
                        continue
                    template_data_type = cls.get_prop_template_primitive_type(prop_template)
                    existing_data_type = prop_data.get("value_type", None)
                    if existing_data_type and template_data_type != existing_data_type:
                        continue
                    continue
                cls.import_single_value_from_template(pset_template, prop_template, simplified_data, props)

            elif prop_template.TemplateType.startswith("Q_"):
                cls.import_single_value_from_template(pset_template, prop_template, simplified_data, props)

            elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                if prop_data and prop_data["class"] != "IfcPropertyEnumeratedValue":
                    continue
                cls.import_enumerated_value_from_template(prop_template, simplified_data, props)

            else:
                # NOTE: currently unsupported types:
                # - P_BOUNDEDVALUE
                # - P_LISTVALUE
                # - P_REFERENCEVALUE
                # - P_TABLEVALUE
                pass

    @classmethod
    def clear_blender_pset_properties(cls, props: bpy.types.PropertyGroup) -> None:
        props.properties.clear()

    @classmethod
    def set_active_pset(
        cls, props: bpy.types.PropertyGroup, pset: ifcopenshell.entity_instance, has_template: bool
    ) -> None:
        props.active_pset_id = pset.id()
        props.active_pset_name = pset.Name
        props.active_pset_has_template = has_template

    @classmethod
    def enable_proposed_pset(
        cls, props: bpy.types.PropertyGroup, pset_name: str, pset_type: PSET_TYPE, has_template: bool
    ) -> None:
        props.active_pset_id = 0
        props.active_pset_name = pset_name or "My_Data"
        props.active_pset_type = pset_type
        props.active_pset_has_template = has_template

    @classmethod
    def get_pset_template(cls, name: str) -> Union[ifcopenshell.entity_instance, None]:
        return bonsai.bim.schema.ifc.psetqto.get_by_name(name)

    @classmethod
    def add_proposed_property(cls, name: str, value: Any, props: bpy.types.PropertyGroup) -> Union[None, str]:
        from ifcopenshell.api.pset.edit_qto import infer_property_type

        if props.properties.get(name):
            return f"Property '{name}' already exists."
        special_type = ""
        if props.active_pset_type == "QTO":
            if not isinstance(value, (float, int)):
                return f"Quantity sets support only numeric values. Provided value: '{value}' ({type(value).__name__})."
            property_type = infer_property_type(name, value)
            if property_type in ("Area", "Length", "Volume"):
                special_type = property_type.upper()
        prop = props.properties.add()
        prop.name = name
        metadata = prop.metadata
        metadata.set_value(value)
        metadata.name = name
        metadata.is_null = value is None
        metadata.is_optional = True
        metadata.special_type = special_type
        metadata.set_value(metadata.get_value_default() if metadata.is_null else value)

    @classmethod
    def cast_string_to_primitive(cls, value: str) -> Any:
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

    @classmethod
    def reset_proposed_property_fields(cls, props: bpy.types.PropertyGroup) -> None:
        reset_props = ("prop_name", "prop_value")
        bl_rna_props = props.bl_rna.properties
        for prop_name in reset_props:
            setattr(props, prop_name, bl_rna_props[prop_name].default)
