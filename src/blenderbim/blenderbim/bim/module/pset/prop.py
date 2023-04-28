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
import blenderbim.bim.schema
import ifcopenshell
import ifcopenshell.util.element
import blenderbim.tool as tool
from blenderbim.bim.prop import Attribute, StrProperty
from blenderbim.bim.module.pset.data import AddEditCustomPropertiesData
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


psetnames = {}
qtonames = {}


def purge():
    global psetnames
    global qtonames
    psetnames = {}
    qtonames = {}


def blender_formatted_enum_from_psets(psets):
    enum_items = []
    version = tool.Ifc.get_schema()
    for pset in psets:
        doc = ifcopenshell.util.doc.get_property_set_doc(version, pset.Name) or {}
        enum_items.append((pset.Name, pset.Name, doc.get("description", "")))
    return enum_items


def get_pset_names(self, context):
    global psetnames
    obj = context.active_object
    if not obj.BIMObjectProperties.ifc_definition_id:
        return []
    element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
    ifc_class = element.is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    assigned_names = ifcopenshell.util.element.get_psets(element, psets_only=True).keys()
    return [p for p in psetnames[ifc_class] if p[0] not in assigned_names]


def get_material_pset_names(self, context):
    global psetnames
    ifc_class = "IfcMaterial"
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_material_set_pset_names(self, context):
    global psetnames
    element = tool.Ifc.get_entity(context.active_object)
    if not element:
        return []
    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
    if not material or "Set" not in material.is_a():
        return []
    ifc_class = material.is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_material_set_item_pset_names(self, context):
    global psetnames
    ifc_definition_id = context.active_object.BIMObjectMaterialProperties.active_material_set_item_id
    if not ifc_definition_id:
        return []
    ifc_class = tool.Ifc.get().by_id(ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_task_qto_names(self, context):
    global qtonames
    ifc_class = "IfcTask"
    if ifc_class not in qtonames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_resource_pset_names(self, context):
    global psetnames
    rprops = context.scene.BIMResourceProperties
    rtprops = context.scene.BIMResourceTreeProperties
    ifc_class = IfcStore.get_file().by_id(rtprops.resources[rprops.active_resource_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_resource_qto_names(self, context):
    global qtonames
    rprops = context.scene.BIMResourceProperties
    rtprops = context.scene.BIMResourceTreeProperties
    ifc_class = IfcStore.get_file().by_id(rtprops.resources[rprops.active_resource_index].ifc_definition_id).is_a()
    if ifc_class not in qtonames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_profile_pset_names(self, context):
    global psetnames
    pprops = context.scene.BIMProfileProperties
    ifc_class = IfcStore.get_file().by_id(pprops.profiles[pprops.active_profile_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_work_schedule_pset_names(self, context):
    global psetnames
    ifc_class = "IfcWorkSchedule"
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_qto_names(self, context):
    global qtonames
    if "/" in context.active_object.name:
        ifc_class = context.active_object.name.split("/")[0]
        if ifc_class not in qtonames:
            psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
            qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
        return qtonames[ifc_class]
    return []


def get_template_type(self, context):
    version = tool.Ifc.get_schema()
    for t in ("IfcPropertySingleValue", "IfcPropertyEnumeratedValue"):
        yield (t, t, ifcopenshell.util.doc.get_entity_doc(version, t).get("description", ""))


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
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_pset_names, name="Pset Name")
    qto_name: EnumProperty(items=get_qto_names, name="Qto Name")


class MaterialPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_material_pset_names, name="Pset Name")


class MaterialSetPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_material_set_pset_names, name="Pset Name")


class MaterialSetItemPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_material_set_item_pset_names, name="Pset Name")


class TaskPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    qto_name: EnumProperty(items=get_task_qto_names, name="Qto Name")


class ResourcePsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_resource_pset_names, name="Pset Name")
    qto_name: EnumProperty(items=get_resource_qto_names, name="Qto Name")


class ProfilePsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_profile_pset_names, name="Pset Name")


class WorkSchedulePsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: StringProperty(name="Active Pset Type")
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_work_schedule_pset_names, name="Pset Name")


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


class DeletePsets(PropertyGroup):
    pset_name: StringProperty(name="Pset")
