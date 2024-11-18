# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020-2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
from ifcopenshell.util.doc import get_attribute_doc
from bonsai.bim.module.pset_template.data import PsetTemplatesData
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.ifc import IfcStore
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def updatePsetTemplateFiles(self, context):
    IfcStore.pset_template_file = None
    PsetTemplatesData.is_loaded = False
    PsetTemplatesData.data["pset_template_files"] = PsetTemplatesData.pset_template_files()
    PsetTemplatesData.data["pset_templates"] = PsetTemplatesData.pset_templates()

    # Ensure enum is valid.
    self["pset_templates"] = 0
    updatePsetTemplates(self, context)

    PsetTemplatesData.data["primary_measure_type"] = PsetTemplatesData.primary_measure_type()
    PsetTemplatesData.data["property_template_type"] = PsetTemplatesData.property_template_type()


def getPsetTemplateFiles(self, context):
    if not PsetTemplatesData.is_loaded:
        PsetTemplatesData.load()
    return PsetTemplatesData.data["pset_template_files"]


def updatePsetTemplates(self, context):
    PsetTemplatesData.data["pset_template"] = PsetTemplatesData.pset_template()
    PsetTemplatesData.data["prop_templates"] = PsetTemplatesData.prop_templates()


def getPsetTemplates(self, context):
    if not PsetTemplatesData.is_loaded:
        PsetTemplatesData.load()
    return PsetTemplatesData.data["pset_templates"]


def get_primary_measure_type(self, context):
    if not PsetTemplatesData.is_loaded:
        PsetTemplatesData.load()
    return PsetTemplatesData.data["primary_measure_type"]


def get_property_template_type(self, context):
    if not PsetTemplatesData.is_loaded:
        PsetTemplatesData.load()
    return PsetTemplatesData.data["property_template_type"]


TEMPLATE_TYPE_ENUM_ITEMS = (
    (
        "PSET_TYPEDRIVENONLY",
        "Pset - IfcTypeObject",
        "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
    ),
    (
        "PSET_TYPEDRIVENOVERRIDE",
        "Pset - IfcTypeObject - Override",
        "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
    ),
    (
        "PSET_OCCURRENCEDRIVEN",
        "Pset - IfcObject",
        "The property sets defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.",
    ),
    (
        "PSET_PERFORMANCEDRIVEN",
        "Pset - IfcPerformanceHistory",
        "The property sets defined by this IfcPropertySetTemplate can only be assigned to IfcPerformanceHistory.",
    ),
    (
        "QTO_TYPEDRIVENONLY",
        "Qto - IfcTypeObject",
        "The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcTypeObject.",
    ),
    (
        "QTO_TYPEDRIVENOVERRIDE",
        "Qto - IfcTypeObject - Override",
        "The element quantity defined by this IfcPropertySetTemplate can be assigned to subtypes of IfcTypeObject and can be overridden by an element quantity with same name at subtypes of IfcObject.",
    ),
    (
        "QTO_OCCURRENCEDRIVEN",
        "Qto - IfcObject",
        "The element quantity defined by this IfcPropertySetTemplate can only be assigned to subtypes of IfcObject.",
    ),
    (
        "NOTDEFINED",
        "Not defined",
        "No restriction provided, the property sets defined by this IfcPropertySetTemplate can be assigned to any entity, if not otherwise restricted by the ApplicableEntity attribute.",
    ),
)


class PsetTemplate(PropertyGroup):
    global_id: StringProperty(
        name="Global ID",
        description=get_attribute_doc("IFC4", "IfcPropertySetTemplate", "GlobalId"),
    )
    name: StringProperty(
        name="Name",
        description=get_attribute_doc("IFC4", "IfcPropertySetTemplate", "Name"),
    )
    description: StringProperty(
        name="Description",
        description=get_attribute_doc("IFC4", "IfcPropertySetTemplate", "Description"),
    )
    template_type: EnumProperty(
        items=TEMPLATE_TYPE_ENUM_ITEMS,
        name="Template Type",
        description=get_attribute_doc("IFC4", "IfcPropertySetTemplate", "TemplateType"),
    )
    applicable_entity: StringProperty(
        name="Applicable Entity",
        description=get_attribute_doc("IFC4", "IfcPropertySetTemplate", "ApplicableEntity"),
    )


class EnumerationValues(PropertyGroup):
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")


class PropTemplate(PropertyGroup):
    global_id: StringProperty(
        name="Global ID",
        description=get_attribute_doc("IFC4", "IfcPropertyTemplate", "GlobalId"),
    )
    name: StringProperty(
        name="Name",
        description=get_attribute_doc("IFC4", "IfcPropertyTemplate", "Name"),
    )
    description: StringProperty(
        name="Description",
        description=get_attribute_doc("IFC4", "IfcPropertyTemplate", "Description"),
    )
    primary_measure_type: EnumProperty(items=get_primary_measure_type, name="Primary Measure Type")
    template_type: EnumProperty(items=get_property_template_type, name="Template Type")
    enum_values: CollectionProperty(type=EnumerationValues)

    def get_value_name(self) -> str:
        if self.primary_measure_type == "-":
            return "string_value"
        ifc_data_type = IfcStore.get_schema().declaration_by_name(self.primary_measure_type)
        data_type = ifcopenshell.util.attribute.get_primitive_type(ifc_data_type)
        if data_type == "string":
            return "string_value"
        elif data_type == "boolean":
            return "bool_value"
        elif data_type == "integer":
            return "int_value"
        elif data_type == "float":
            return "float_value"
        else:
            assert False, "Unknown data type"


class BIMPsetTemplateProperties(PropertyGroup):
    pset_template_files: EnumProperty(
        items=getPsetTemplateFiles,
        name="Pset Template Files",
        description="Pset Template File",
        update=updatePsetTemplateFiles,
    )
    pset_templates: EnumProperty(
        items=getPsetTemplates,
        name="Pset Templates",
        description="Pset Template",
        update=updatePsetTemplates,
    )
    active_pset_template_id: IntProperty(name="Active Pset Template Id")
    active_prop_template_id: IntProperty(name="Active Prop Template Id")
    active_pset_template: PointerProperty(type=PsetTemplate)
    active_prop_template: PointerProperty(type=PropTemplate)
