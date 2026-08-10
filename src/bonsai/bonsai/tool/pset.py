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

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal, Union, assert_never

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import ifcopenshell.util.unit

import bonsai.bim.helper
import bonsai.bim.schema
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.pset.prop import (
        AddEditPropertyEntry,
        DeletePsetEntry,
        GlobalPsetProperties,
        PsetProperties,
        RenamePropertyEntry,
    )
    from bonsai.bim.prop import Attribute


class Pset(bonsai.core.tool.Pset):
    PSET_TYPE = Literal["PSET", "QTO"]
    BulkOperationType = Literal["ADD_EDIT", "RENAME", "DELETE"]
    BULK_OPERATION_TYPES = ("ADD_EDIT", "RENAME", "DELETE")

    @classmethod
    def get_global_pset_props(cls) -> GlobalPsetProperties:
        return bpy.context.scene.GlobalPsetProperties

    @classmethod
    def get_bulk_operation_collection(cls, operation_type: BulkOperationType) -> Union[
        bpy.types.bpy_prop_collection_idprop[AddEditPropertyEntry],
        bpy.types.bpy_prop_collection_idprop[RenamePropertyEntry],
        bpy.types.bpy_prop_collection_idprop[DeletePsetEntry],
    ]:
        props = cls.get_global_pset_props()
        if operation_type == "ADD_EDIT":
            return props.psets_to_add_edit
        elif operation_type == "RENAME":
            return props.psets_to_rename
        elif operation_type == "DELETE":
            return props.psets_to_delete
        else:
            assert False

    @classmethod
    def get_element_pset(
        cls, element: ifcopenshell.entity_instance, pset_name: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        pset = ifcopenshell.util.element.get_pset(element, pset_name)
        if pset:
            return tool.Ifc.get().by_id(pset["id"])

    @classmethod
    def upsert_pset(
        cls,
        element: ifcopenshell.entity_instance,
        pset_name: str,
        properties: dict[str, Any],
    ) -> ifcopenshell.entity_instance:
        """Get or create ``pset_name`` on ``element``, write ``properties``, return the pset.
        Centralises the get-element-pset → add-pset-if-missing → edit-pset idiom."""
        ifc_file = tool.Ifc.get()
        pset = cls.get_element_pset(element, pset_name)
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name=pset_name)
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties=properties)
        return pset

    @classmethod
    def write_bbim_data(
        cls,
        element: ifcopenshell.entity_instance,
        pset_name: str,
        data: dict[str, Any],
    ) -> ifcopenshell.entity_instance:
        """Get or create the BBIM_<Type> pset and write ``data`` as the IfcText-serialised
        JSON ``Data`` property. Canonical writer for parametric-modifier pset state."""
        data_text = tool.Ifc.get().createIfcText(json.dumps(data, default=list))
        return cls.upsert_pset(element, pset_name, {"Data": data_text})

    @classmethod
    def get_pset_props(cls, obj: str, obj_type: tool.Ifc.OBJECT_TYPE) -> PsetProperties:
        if obj_type == "Object":
            return bpy.data.objects[obj].PsetProperties
        elif obj_type == "Material":
            return bpy.context.scene.MaterialPsetProperties
        elif obj_type == "MaterialSetItem":
            return bpy.data.objects[obj].MaterialSetItemPsetProperties
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
        elif obj_type == "Zone":
            return bpy.context.scene.ZonePsetProperties
        elif obj_type == "Cost":
            # No psets for cost items currently.
            assert False, obj_type
        assert_never(obj_type)

    @classmethod
    def get_pset_name(cls, obj: str, obj_type: tool.Ifc.OBJECT_TYPE, pset_type: PSET_TYPE = "PSET") -> str:
        props = cls.get_pset_props(obj, obj_type)
        name = props.pset_name if pset_type == "PSET" else props.qto_name
        if name in ("BBIM_CUSTOM", "BBIM_BSDD"):
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
            in bonsai.bim.schema.ifc.psetqto.get_applicable_names(
                element.is_a(), predefined_type, pset_only=True, schema=tool.Ifc.get_schema()
            )
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

    # Templates for quantities can specify their kind via TemplateType (e.g.
    # "Q_LENGTH") instead of PrimaryMeasureType. IfcQuantityCount has no
    # associated measure/unit, so it is intentionally absent here.
    QUANTITY_TEMPLATE_TYPE_TO_SPECIAL_TYPE = {
        "Q_LENGTH": "LENGTH",
        "Q_AREA": "AREA",
        "Q_VOLUME": "VOLUME",
        "Q_WEIGHT": "MASS",
        "Q_TIME": "TIME",
    }

    @classmethod
    def get_special_type_for_measure_class(cls, measure_class: str) -> str:
        """Get the ``special_type`` (an IfcUnitEnum value with "UNIT" stripped) for an IFC measure class.

        :param measure_class: An IFC measure class name, e.g. "IfcLengthMeasure".
        :return: E.g. "LENGTH", or "" if the class has no associated unit type.
        """
        if not measure_class.endswith("Measure"):
            return ""
        unit_type = ifcopenshell.util.unit.get_measure_unit_type(measure_class)
        return unit_type[: -len("UNIT")] if unit_type.endswith("UNIT") else ""

    @classmethod
    def get_special_type_for_unit(cls, unit: ifcopenshell.entity_instance) -> str:
        """Get the ``special_type`` (an IfcUnitEnum value with "UNIT" stripped) directly from
        a Unit entity, for properties whose NominalValue is a generic numeric type (e.g.
        IfcReal) rather than a proper measure class, but which still carry a real Unit.
        """
        unit_type = getattr(unit, "UnitType", None)
        if unit_type and unit_type != "USERDEFINED":
            return unit_type[: -len("UNIT")] if unit_type.endswith("UNIT") else ""
        dimension_type = ifcopenshell.util.unit.identify_unit_dimensions(unit)
        return dimension_type[: -len("UNIT")] if dimension_type else ""

    @classmethod
    def get_special_type_for_prop(cls, prop_or_prop_template: ifcopenshell.entity_instance) -> str:
        """Classify a property/quantity/template by its measure type.

        :return: An IfcUnitEnum value with the "UNIT" suffix stripped (e.g.
            "LENGTH", "PRESSURE"), "URI" for IfcURIReference, or "" if the
            value has no associated unit type.
        """
        if prop_or_prop_template.is_a("IfcPropertyTemplate"):
            primary_measure_type = prop_or_prop_template.PrimaryMeasureType
            if primary_measure_type == "IfcURIReference":
                return "URI"
            if primary_measure_type:
                return cls.get_special_type_for_measure_class(primary_measure_type)
            return cls.QUANTITY_TEMPLATE_TYPE_TO_SPECIAL_TYPE.get(prop_or_prop_template.TemplateType, "")
        elif prop_or_prop_template.is_a("IfcPropertySingleValue"):
            value = prop_or_prop_template.NominalValue
            if value is not None:
                special_type = cls.get_special_type_for_measure_class(value.is_a())
                if special_type:
                    return special_type
                # Some property sets declare a generic numeric type (e.g. IfcReal) rather
                # than a proper measure class, relying on an explicit Unit attribute alone to
                # convey the dimension. Still measurable -- derive special_type from the Unit
                # itself rather than (fruitlessly) from NominalValue's declared type.
                if value.is_a() in ("IfcReal", "IfcInteger"):
                    if unit := getattr(prop_or_prop_template, "Unit", None):
                        return cls.get_special_type_for_unit(unit)
        elif prop_or_prop_template.is_a("IfcPhysicalSimpleQuantity"):
            entity = prop_or_prop_template.wrapped_data.declaration().as_entity()
            measure_class = entity.attribute_by_index(3).type_of_attribute().declared_type().name()
            return cls.get_special_type_for_measure_class(measure_class)
        return ""

    @classmethod
    def get_unit_symbol_for_special_type(cls, special_type: str, ifc_file: ifcopenshell.file) -> str:
        """Get the project's default unit symbol for a `special_type` (see `get_special_type_for_prop`).

        Used where there's no property instance to check for a `Unit` override
        (e.g. a template, or a native IFC entity attribute, neither of which
        can carry one).
        """
        if not special_type or special_type == "URI":
            return ""
        unit = ifcopenshell.util.unit.get_project_unit(ifc_file, f"{special_type}UNIT")
        return ifcopenshell.util.unit.get_unit_symbol(unit) if unit else ""

    @classmethod
    def get_unit_symbol_for_prop(cls, prop: ifcopenshell.entity_instance, ifc_file: ifcopenshell.file) -> str:
        """Get the unit symbol for an existing property/quantity, respecting its own `Unit` override.

        Gated on the property being classified as measurable (see `get_special_type_for_prop`,
        which already accounts for a Unit attached to a generic numeric value) -- this only
        excludes a Unit attached to a property whose value has no numeric/measure semantics at
        all (e.g. text), where a stray Unit shouldn't be surfaced as a resolved unit.
        """
        if not cls.is_measurable_special_type(cls.get_special_type_for_prop(prop)):
            return ""
        unit = ifcopenshell.util.unit.get_property_unit(prop, ifc_file)
        return ifcopenshell.util.unit.get_unit_symbol(unit) if unit else ""

    # special_type values that don't denote a real unit-bearing measure (see get_special_type_for_prop).
    NON_MEASURABLE_SPECIAL_TYPES = frozenset({"", "DATE", "DATETIME", "LOGICAL", "URI", "DURATION"})

    @classmethod
    def is_measurable_special_type(cls, special_type: str) -> bool:
        """True if `special_type` (see `get_special_type_for_prop`) denotes a real unit-bearing measure."""
        return special_type not in cls.NON_MEASURABLE_SPECIAL_TYPES

    @classmethod
    def get_candidate_units_for_special_type(
        cls, special_type: str, ifc_file: ifcopenshell.file
    ) -> list[ifcopenshell.entity_instance]:
        """All units in the file usable as an override for a `special_type` (see `get_special_type_for_prop`)."""
        if not cls.is_measurable_special_type(special_type):
            return []
        return ifcopenshell.util.unit.get_candidate_units(ifc_file, f"{special_type}UNIT")

    @classmethod
    def resolve_effective_unit(
        cls, special_type: str, unit_id: int, ifc_file: ifcopenshell.file
    ) -> Union[ifcopenshell.entity_instance, None]:
        """The unit a value is currently expressed in: its own override (`unit_id`, a STEP id,
        0 meaning "no override"), or the project default for `special_type` otherwise."""
        if unit_id:
            return ifc_file.by_id(unit_id)
        return ifcopenshell.util.unit.get_project_unit(ifc_file, f"{special_type}UNIT")

    @classmethod
    def convert_attribute_unit(cls, metadata: "Attribute", new_unit_id: int, ifc_file: ifcopenshell.file) -> None:
        """Rescale `metadata.float_value` in place so its physical quantity is preserved when
        switching from its current effective unit to the unit named by `new_unit_id` (0 = project
        default). No-op for non-measurable attributes or when old and new resolve to the same unit.
        """
        if not cls.is_measurable_special_type(metadata.special_type):
            return
        old_unit = cls.resolve_effective_unit(metadata.special_type, metadata.unit_id, ifc_file)
        new_unit = cls.resolve_effective_unit(metadata.special_type, new_unit_id, ifc_file)
        if old_unit is None or new_unit is None or old_unit == new_unit:
            return
        old_scale = ifcopenshell.util.unit.get_unit_scale(old_unit)
        new_scale = ifcopenshell.util.unit.get_unit_scale(new_unit)
        metadata.float_value = metadata.float_value * old_scale / new_scale

    @classmethod
    def import_pset_from_existing(
        cls,
        pset: ifcopenshell.entity_instance,
        props: PsetProperties,
        pset_template: Union[ifcopenshell.entity_instance, None],
    ) -> None:
        """
        :param pset_template: Pset Template to use as a source for descriptions.
        """
        pset_props: tuple[ifcopenshell.entity_instance, ...] = ()
        if pset.is_a("IfcElementQuantity"):
            pset_props = pset.Quantities
        elif pset.is_a("IfcPropertySet"):
            pset_props = pset.HasProperties
        elif pset.is_a("IfcMaterialProperties") or pset.is_a("IfcProfileProperties"):
            pset_props = pset.Properties

        # If this Pset's owning element is classified against a bSDD class that defines
        # this Pset, recognise properties matching bSDD property codes as picklists,
        # even though the Pset wasn't necessarily created through the bSDD add-property UI.
        bsdd_allowed_values: dict[str, list[str]] = {}
        if pset.is_a("IfcPropertySet"):
            elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            if elements:
                try:
                    bsdd_allowed_values = tool.Bsdd.get_bsdd_pset_property_values(next(iter(elements)), pset.Name)
                except Exception:
                    pass

        prop_templates: dict[str, ifcopenshell.entity_instance] = {}
        if pset_template:
            prop_templates = {prop.Name: prop for prop in pset_template.HasPropertyTemplates}

        def process_prop_description(metadata: Attribute) -> None:
            prop_name = metadata.name
            if prop_name not in prop_templates:
                return
            bonsai.bim.helper.add_attribute_description(metadata, prop_templates[prop_name])

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
                process_prop_description(metadata)
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
                metadata.unit_symbol = cls.get_unit_symbol_for_prop(prop, tool.Ifc.get())
                # The prop's OWN Unit override only, not the resolved project-default fallback
                # get_unit_symbol_for_prop() above already accounted for. Some real-world files
                # (e.g. certain exporters) set Unit on properties that aren't actually measures --
                # ignore it there, since we only ever treat Unit as meaningful for measurable
                # special_types (matching the UI picker's own gating).
                own_unit = getattr(prop, "Unit", None) if cls.is_measurable_special_type(metadata.special_type) else None
                metadata.unit_id = own_unit.id() if own_unit else 0
                metadata.unit_id_enum = str(metadata.unit_id)
                metadata.set_value(metadata.get_value_default() if metadata.is_null else value)
                process_prop_description(metadata)

                if prop.is_a("IfcPropertySingleValue") and (possible_values := bsdd_allowed_values.get(prop.Name)):
                    str_value = None if value is None else str(value)
                    if str_value is not None and str_value not in possible_values:
                        # Preserve a legacy/imported value that doesn't match the current
                        # bSDD enumeration instead of silently dropping it.
                        possible_values = [*possible_values, str_value]
                    metadata.enum_items = json.dumps(possible_values)
                    metadata.data_type = "enum"
                    if str_value is not None:
                        metadata.enum_value = str_value

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
        metadata.special_type = "URI" if prop_template.PrimaryMeasureType == "IfcURIReference" else ""
        bonsai.bim.helper.add_attribute_description(metadata, prop_template)

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
        props: PsetProperties,
    ) -> None:
        prop = props.properties.add()
        prop.name = prop_template.Name
        prop.value_type = "IfcPropertySingleValue"
        metadata = prop.metadata
        metadata.name = prop_template.Name
        metadata.is_null = data.get(prop_template.Name, None) is None
        metadata.is_optional = True
        metadata.data_type = cls.get_prop_template_primitive_type(prop_template)
        metadata.special_type = cls.get_special_type_for_prop(prop_template)
        metadata.unit_symbol = cls.get_unit_symbol_for_special_type(metadata.special_type, tool.Ifc.get())

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
        props: PsetProperties,
    ) -> None:
        if pset:
            data = ifcopenshell.util.element.get_property_definition(pset, verbose=True)
            del data["id"]
        else:
            data = {}
        simplified_data = {prop_name: prop_data["value"] for prop_name, prop_data in data.items()}

        # For every prop we first ensure that existing prop value type matches the template value type
        # to prevent data loss and error casting data.
        # Existing property will be added later by import_pset_from_existing.
        for prop_template in sorted(pset_template.HasPropertyTemplates, key=lambda p: p.Name):
            if (
                not prop_template.is_a("IfcSimplePropertyTemplate")
                or prop_template.PrimaryMeasureType == "IfcComplexNumber"
            ):
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
                if prop_data:
                    continue  # Existing quantity will be added later by import_pset_from_existing.
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
        metadata.unit_symbol = cls.get_unit_symbol_for_special_type(special_type, tool.Ifc.get())
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
