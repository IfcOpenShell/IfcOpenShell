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
from bonsai.bim.module.pset.data import (
    AddEditCustomPropertiesData,
    ObjectPsetsData,
    MaterialPsetsData,
    PsetsGeneralData,
)
from bonsai.bim.module.material.data import ObjectMaterialData
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
from typing import Union, Literal, TYPE_CHECKING, get_args, Literal

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
def get_pset_name(self: "PsetProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
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
    elif prop_type == "ZonePsetProperties":
        results = get_zone_pset_names(self, context)

    if not PsetsGeneralData.is_loaded:
        PsetsGeneralData.load()

    items: list[tool.Blender.BLENDER_ENUM_ITEM]
    items = [("BBIM_CUSTOM", "Custom Pset", "Create a property set without using a template.")]
    bsdd_items = PsetsGeneralData.data["bsdd_enum_items"]
    if bsdd_items:
        items.append(None)
        items.extend(bsdd_items)
    items.append(None)
    items.extend(results)
    return items


def get_object_pset_name(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not ObjectPsetsData.is_loaded:
        ObjectPsetsData.load()
    return ObjectPsetsData.data["pset_name"]


def get_material_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not MaterialPsetsData.is_loaded:
        MaterialPsetsData.load()
    return MaterialPsetsData.data["pset_name"]


def get_material_set_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    if not ObjectMaterialData.is_loaded:
        ObjectMaterialData.load()
    ifc_class = ObjectMaterialData.data["material_class"]
    if not ifc_class or "Set" not in ifc_class:
        return []
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_material_set_item_pset_names(
    self: "PsetProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    obj = context.active_object
    assert obj
    omprops = tool.Material.get_object_material_props(obj)
    if not (ifc_definition_id := omprops.active_material_set_item_id):
        return []
    ifc_class = tool.Ifc.get().by_id(ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_task_qto_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global qtonames
    ifc_class = "IfcTask"
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True, schema=tool.Ifc.get_schema())
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_resource_pset_names(self: "PsetProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    active_resource = tool.Resource.get_resource_props().active_resource
    assert active_resource
    ifc_class = tool.Ifc.get().by_id(active_resource.ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_resource_qto_names(self: "PsetProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global qtonames
    active_resource = tool.Resource.get_resource_props().active_resource
    assert active_resource
    ifc_class = tool.Ifc.get().by_id(active_resource.ifc_definition_id).is_a()
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True, schema=tool.Ifc.get_schema())
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_group_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    ifc_class = "IfcGroup"
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_group_qto_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global qtonames
    ifc_class = "IfcGroup"
    if ifc_class not in qtonames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True, schema=tool.Ifc.get_schema())
        qtonames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return qtonames[ifc_class]


def get_profile_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    pprops = tool.Profile.get_profile_props()
    ifc_class = tool.Ifc.get().by_id(pprops.profiles[pprops.active_profile_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_work_schedule_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    ifc_class = "IfcWorkSchedule"
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


def get_zone_pset_names(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    global psetnames
    ifc_class = "IfcZone"
    if ifc_class not in psetnames:
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True, schema=tool.Ifc.get_schema())
        psetnames[ifc_class] = blender_formatted_enum_from_psets(psets)
    return psetnames[ifc_class]


# TODO: unsafe?
def get_qto_name(self: "PsetProperties", context: bpy.types.Context) -> tool.Blender.BLENDER_ENUM_ITEMS:
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
    else:
        assert False
    return [("BBIM_CUSTOM", "Custom Qto", "Create a quantity set without using a template."), None] + list(results)


def get_object_qto_name(self: "PsetProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not ObjectPsetsData.is_loaded:
        ObjectPsetsData.load()
    return ObjectPsetsData.data["qto_name"]


# TODO: unsafe?
def get_template_type(self: "AddEditPropertyEntry", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    version = tool.Ifc.get_schema()
    for t in ("IfcPropertySingleValue", "IfcPropertyEnumeratedValue"):
        yield (t, t, ifcopenshell.util.doc.get_entity_doc(version, t).get("description", ""))


# TODO: unsafe?
def get_primary_measure_type(self: "AddEditPropertyEntry", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not AddEditCustomPropertiesData.is_loaded:
        AddEditCustomPropertiesData.load()
    return AddEditCustomPropertiesData.data["primary_measure_type"]


class IfcPropertyEnumeratedValue(PropertyGroup):
    enumerated_values: CollectionProperty(type=Attribute)

    if TYPE_CHECKING:
        enumerated_values: bpy.types.bpy_prop_collection_idprop[Attribute]


IfcPropertyValueType = Literal["IfcPropertySingleValue", "IfcPropertyEnumeratedValue"]


class IfcProperty(PropertyGroup):
    metadata: PointerProperty(type=Attribute)
    value_type: EnumProperty(items=[(v, v, v) for v in get_args(IfcPropertyValueType)], name="Value Type")
    enumerated_value: PointerProperty(type=IfcPropertyEnumeratedValue)

    if TYPE_CHECKING:
        metadata: Attribute
        value_type: IfcPropertyValueType
        enumerated_value: IfcPropertyEnumeratedValue


class PsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_has_template: BoolProperty(name="Active Pset Has Template")
    active_pset_name: StringProperty(name="Pset Name")
    active_pset_type: EnumProperty(
        name="Active Pset Type",
        items=[(i, i, "") for i in ("-", "PSET", "QTO")],
        default="-",
    )
    properties: CollectionProperty(name="Properties", type=IfcProperty)
    pset_name: EnumProperty(items=get_pset_name, name="Pset Name")
    qto_name: EnumProperty(items=get_qto_name, name="Qto Name")
    # Proposed property.
    prop_name: StringProperty(name="Property Name", default="MyProperty")
    prop_value: StringProperty(name="Property Value", default="Some Value")

    if TYPE_CHECKING:
        active_pset_id: int
        active_pset_has_template: bool
        active_pset_name: str
        active_pset_type: Literal["-", "PSET", "QTO"]
        properties: bpy.types.bpy_prop_collection_idprop[IfcProperty]
        pset_name: str
        qto_name: str
        prop_name: str
        prop_value: str


class RenamePropertyEntry(PropertyGroup):
    name: StringProperty(name="Pset")
    existing_property_name: StringProperty(name="Existing Property Name")
    new_property_name: StringProperty(name="New Property Name")

    if TYPE_CHECKING:
        name: str
        existing_property_name: str
        new_property_name: str


class AddEditPropertyEntry(PropertyGroup):
    pset_name: StringProperty(name="Pset")
    name: StringProperty(name="Property")
    string_value: StringProperty(name="Value")
    bool_value: BoolProperty(name="Value")
    int_value: IntProperty(name="Value")
    float_value: FloatProperty(name="Value")
    primary_measure_type: EnumProperty(items=get_primary_measure_type, name="Primary Measure Type")
    template_type: EnumProperty(items=get_template_type, name="Template Type")
    enum_values: CollectionProperty(name="Enum Values", type=Attribute)

    if TYPE_CHECKING:
        pset_name: str
        name: str
        string_value: str
        bool_value: bool
        int_value: int
        float_value: float
        primary_measure_type: str
        template_type: str
        enum_values: bpy.types.bpy_prop_collection_idprop[Attribute]

    def get_value_name(self) -> Union[Literal["string_value", "bool_value", "int_value", "float_value"], None]:
        schema = tool.Ifc.schema()
        ifc_data_type = schema.declaration_by_name(self.primary_measure_type)
        data_type = ifcopenshell.util.attribute.get_primitive_type(ifc_data_type)
        if data_type == "string":
            return "string_value"
        elif data_type == "boolean":
            return "bool_value"
        elif data_type == "integer":
            return "int_value"
        elif data_type == "float":
            return "float_value"


# This class is needed just to make tooltip more descriptive.
class DeletePsetEntry(PropertyGroup):
    name: StringProperty(name="Pset to Remove")

    if TYPE_CHECKING:
        name: str


class GlobalPsetProperties(PropertyGroup):
    pset_filter: StringProperty(name="Pset Filter", options={"TEXTEDIT_UPDATE"})
    qto_filter: StringProperty(name="Qto Filter", options={"TEXTEDIT_UPDATE"})

    # Bulk operations.
    psets_to_delete: CollectionProperty(type=DeletePsetEntry)  # pyright: ignore[reportRedeclaration]
    psets_to_rename: CollectionProperty(type=RenamePropertyEntry)  # pyright: ignore[reportRedeclaration]
    psets_to_add_edit: CollectionProperty(type=AddEditPropertyEntry)  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        pset_filter: str
        qto_filter: str
        psets_to_delete: bpy.types.bpy_prop_collection_idprop[DeletePsetEntry]
        psets_to_rename: bpy.types.bpy_prop_collection_idprop[RenamePropertyEntry]
        psets_to_add_edit: bpy.types.bpy_prop_collection_idprop[AddEditPropertyEntry]
