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
import bonsai.bim.schema
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.doc
import ifcopenshell.util.element
import bonsai.tool as tool
from bonsai.bim.prop import Attribute, StrProperty
from bonsai.bim.module.pset.data import AddEditCustomPropertiesData, ObjectPsetsData, MaterialPsetsData
from bonsai.bim.module.material.data import ObjectMaterialData
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
from typing import Union, Literal


psetnames = {}
qtonames = {}


def purge():
    global psetnames
    global qtonames
    psetnames = {}
    qtonames = {}


def blender_formatted_enum_from_psets(psets: list[ifcopenshell.entity_instance]) -> list[tuple[str, str, str]]:
    enum_items = []
    version = tool.Ifc.get_schema()
    for pset in psets:
        doc = ifcopenshell.util.doc.get_property_set_doc(version, pset.Name) or {}
        enum_items.append((pset.Name, pset.Name, doc.get("description", "")))
    return enum_items


# TODO: unsafe?
def get_pset_name(self, context):
    pset_type = repr(self)
    prop_type = pset_type.split(".")[-1]
    results = []
    if "bpy.data.objects" in pset_type:
        if prop_type == "PsetProperties":
            results = get_object_pset_name(self, context)
        elif prop_type == "MaterialSetPsetProperties":
            results = get_material_set_pset_names(self, context)
        elif prop_type == "MaterialSetItemPsetProperties":
            results = get_material_set_item_pset_names(self, context)
    elif prop_type == "MaterialPsetProperties":
        results = get_material_pset_names(self, context)
    elif prop_type == "ResourcePsetProperties":
        results = get_resource_pset_names(self, context)
    elif prop_type == "GroupPsetProperties":
        results = get_group_pset_names(self, context)
    elif prop_type == "ProfilePsetProperties":
        results = get_profile_pset_names(self, context)
    elif prop_type == "WorkSchedulePsetProperties":
        results = get_work_schedule_pset_names(self, context)
    return [("BBIM_CUSTOM", "Custom Pset", "Create a property set without using a template."), None] + results


def get_object_pset_name(self, context):
    if not ObjectPsetsData.is_loaded:
        ObjectPsetsData.load()
    return ObjectPsetsData.data["pset_name"]


def get_material_pset_names(self, context):
    if not MaterialPsetsData.is_loaded:
        MaterialPsetsData.load()
    return MaterialPsetsData.data["pset_name"]


def get_material_set_pset_names(self, context):
    global psetnames
    if not ObjectMaterialData.is_loaded:
        ObjectMaterialData.load()
    ifc_class = ObjectMaterialData.data["material_class"]
    if not ifc_class or "Set" not in ifc_class:
        return []
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_material_set_item_pset_names(self, context):
    global psetnames
    ifc_definition_id = context.active_object.BIMObjectMaterialProperties.active_material_set_item_id
    if not ifc_definition_id:
        return []
    ifc_class = tool.Ifc.get().by_id(ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_task_qto_names(self, context):
    global qtonames
    ifc_class = "IfcTask"
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_resource_pset_names(self, context):
    global psetnames
    rprops = context.scene.BIMResourceProperties
    rtprops = context.scene.BIMResourceTreeProperties
    ifc_class = IfcStore.get_file().by_id(rtprops.resources[rprops.active_resource_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_resource_qto_names(self, context):
    global qtonames
    rprops = context.scene.BIMResourceProperties
    rtprops = context.scene.BIMResourceTreeProperties
    ifc_class = IfcStore.get_file().by_id(rtprops.resources[rprops.active_resource_index].ifc_definition_id).is_a()
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_group_pset_names(self, context):
    global psetnames
    ifc_class = "IfcGroup"
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_group_qto_names(self, context):
    global qtonames
    ifc_class = "IfcGroup"
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_profile_pset_names(self, context):
    global psetnames
    pprops = context.scene.BIMProfileProperties
    ifc_class = IfcStore.get_file().by_id(pprops.profiles[pprops.active_profile_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_work_schedule_pset_names(self, context):
    global psetnames
    ifc_class = "IfcWorkSchedule"
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


# TODO: unsafe?
def get_qto_name(self, context):
    pset_type = repr(self)
    prop_type = pset_type.split(".")[-1]
    if "bpy.data.objects" in pset_type:
        if prop_type == "PsetProperties":
            results = get_object_qto_name(self, context)
    elif prop_type == "TaskPsetProperties":
        results = get_task_qto_names(self, context)
    elif prop_type == "ResourcePsetProperties":
        results = get_resource_qto_names(self, context)
    elif prop_type == "GroupPsetProperties":
        results = get_group_qto_names(self, context)
    return [("BBIM_CUSTOM", "Custom Qto", "Create a quantity set without using a template."), None] + results


def get_object_qto_name(self, context):
    if not ObjectPsetsData.is_loaded:
        ObjectPsetsData.load()
    return ObjectPsetsData.data["qto_name"]


# TODO: unsafe?
def get_template_type(self, context):
    version = tool.Ifc.get_schema()
    for t in ("IfcPropertySingleValue", "IfcPropertyEnumeratedValue"):
        yield (t, t, ifcopenshell.util.doc.get_entity_doc(version, t).get("description", ""))


# TODO: unsafe?
def get_primary_measure_type(self, context):
    if not AddEditCustomPropertiesData.is_loaded:
        AddEditCustomPropertiesData.load()
    return AddEditCustomPropertiesData.data["primary_measure_type"]


class IfcPropertyEnumeratedValue(PropertyGroup):
    enumerated_values: CollectionProperty(type=Attribute)


class IfcProperty(PropertyGroup):
    metadata: PointerProperty(type=Attribute)
    value_type: EnumProperty(
        items=[(v, v, v) for v in ("IfcPropertySingleValue", "IfcPropertyEnumeratedValue")], name="Value Type"
    )
    enumerated_value: PointerProperty(type=IfcPropertyEnumeratedValue)


class PsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_has_template: BoolProperty(name="Active Pset Has Template")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: EnumProperty(
        name="Active Pset Type",
        items=((i, i, "") for i in ("-", "PSET", "QTO")),
        default="-",
    )
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_pset_name, name="Pset Name")
    qto_name: EnumProperty(items=get_qto_name, name="Qto Name")
    # Proposed property.
    prop_name: StringProperty(name="Property Name", default="MyProperty")
    prop_value: StringProperty(name="Property Value", default="Some Value")


class RenameProperties(PropertyGroup):
    pset_name: StringProperty(name="Pset")
    existing_property_name: StringProperty(name="Existing Property Name")
    new_property_name: StringProperty(name="New Property Name")


class AddEditProperties(PropertyGroup):
    pset_name: StringProperty(name="Pset")
    property_name: StringProperty(name="Property")
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")
    primary_measure_type: EnumProperty(items=get_primary_measure_type, name="Primary Measure Type")
    template_type: EnumProperty(items=get_template_type, name="Template Type")
    enum_values: CollectionProperty(name="Enum Values", type=Attribute)

    def get_value_name(self) -> Union[Literal["string_value", "bool_value", "int_value", "float_value"], None]:
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


class DeletePsets(PropertyGroup):
    pset_name: StringProperty(name="Pset")


class GlobalPsetProperties(PropertyGroup):
    pset_filter: StringProperty(name="Pset Filter", options={"TEXTEDIT_UPDATE"})
    qto_filter: StringProperty(name="Qto Filter", options={"TEXTEDIT_UPDATE"})
