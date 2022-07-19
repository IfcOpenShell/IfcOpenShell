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

import os
import bpy
import ifcopenshell
from blenderbim.bim.module.pset_template.data import PsetTemplatesData
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
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
from ifcopenshell.api.pset_template.data import Data


psettemplatefiles_enum = []
psettemplates_enum = []


def purge():
    global psettemplatefiles_enum
    global psettemplates_enum
    psettemplatefiles_enum = []
    psettemplates_enum = []


def updatePsetTemplateFiles(self, context):
    global psettemplates_enum
    IfcStore.pset_template_path = os.path.join(
        context.scene.BIMProperties.data_dir,
        "pset",
        context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
    )
    IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)
    updatePsetTemplates(self, context)


def getPsetTemplateFiles(self, context):
    global psettemplatefiles_enum
    if len(psettemplatefiles_enum) < 1:
        files = os.listdir(os.path.join(context.scene.BIMProperties.data_dir, "pset"))
        psettemplatefiles_enum.extend([(f.replace(".ifc", ""), f.replace(".ifc", ""), "") for f in files])
    return psettemplatefiles_enum


def updatePsetTemplates(self, context):
    global psettemplates_enum
    psettemplates_enum.clear()
    getPsetTemplates(self, context)


def getPsetTemplates(self, context):
    global psettemplates_enum
    if len(psettemplates_enum) < 1:
        if not IfcStore.pset_template_file:
            IfcStore.pset_template_path = os.path.join(
                context.scene.BIMProperties.data_dir,
                "pset",
                context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
            )
            IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)
        templates = IfcStore.pset_template_file.by_type("IfcPropertySetTemplate")
        psettemplates_enum.extend([(str(t.id()), t.Name, "") for t in templates])
        Data.load(IfcStore.pset_template_file)
    return psettemplates_enum


def get_primary_measure_type(self, context):
    if not PsetTemplatesData.is_loaded:
        PsetTemplatesData.load()
    return PsetTemplatesData.data["primary_measure_type"]


def get_template_type(self, context):
    return [
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
    ]


class PsetTemplate(PropertyGroup):
    global_id: StringProperty(name="Global ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    template_type: EnumProperty(items=get_template_type, name="Template Type")
    applicable_entity: StringProperty(name="Applicable Entity")


class EnumerationValues(PropertyGroup):
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")


class PropTemplate(PropertyGroup):
    global_id: StringProperty(name="Global ID")
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    primary_measure_type: EnumProperty(items=get_primary_measure_type, name="Primary Measure Type")
    template_type: EnumProperty(
        items=[("P_SINGLEVALUE", "P_SINGLEVALUE", ""), ("P_ENUMERATEDVALUE", "P_ENUMERATEDVALUE", "")],
        name="Template Type",
    )
    enum_values: CollectionProperty(type=EnumerationValues)

    def get_value_name(self):
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


class BIMPsetTemplateProperties(PropertyGroup):
    pset_template_files: EnumProperty(
        items=getPsetTemplateFiles, name="Pset Template Files", update=updatePsetTemplateFiles
    )
    pset_templates: EnumProperty(items=getPsetTemplates, name="Pset Template Files")
    active_pset_template_id: IntProperty(name="Active Pset Template Id")
    active_prop_template_id: IntProperty(name="Active Prop Template Id")
    active_pset_template: PointerProperty(type=PsetTemplate)
    active_prop_template: PointerProperty(type=PropTemplate)
    new_template_filename: StringProperty("New TemplateFileName")
