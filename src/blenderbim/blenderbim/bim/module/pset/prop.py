import bpy
import blenderbim.bim.schema
from blenderbim.bim.prop import Attribute
from ifcopenshell.api.pset.data import Data
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


def getPsetNames(self, context):
    global psetnames
    obj = context.active_object
    if not obj.BIMObjectProperties.ifc_definition_id:
        return []
    element = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
    ifc_class = element.is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
    assigned_names = [
        Data.psets[p]["Name"] for p in Data.products[obj.BIMObjectProperties.ifc_definition_id]["psets"]
    ]
    return [p for p in psetnames[ifc_class] if p[0] not in assigned_names]


def getMaterialPsetNames(self, context):
    global psetnames
    ifc_class = "IfcMaterial"
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
    return psetnames[ifc_class]


def getTaskQtoNames(self, context):
    global qtonames
    ifc_class = "IfcTask"
    if ifc_class not in qtonames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
    return qtonames[ifc_class]


def getResourceQtoNames(self, context):
    global qtonames
    rprops = context.scene.BIMResourceProperties
    rtprops = context.scene.BIMResourceTreeProperties
    ifc_class = IfcStore.get_file().by_id(rtprops.resources[rprops.active_resource_index].ifc_definition_id).is_a()
    if ifc_class not in qtonames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
        qtonames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
    return qtonames[ifc_class]


def getProfilePsetNames(self, context):
    global psetnames
    pprops = context.scene.BIMProfileProperties
    ifc_class = IfcStore.get_file().by_id(pprops.profiles[pprops.active_profile_index].ifc_definition_id).is_a()
    if ifc_class not in psetnames:
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
        psetnames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
    return psetnames[ifc_class]


def getQtoNames(self, context):
    global qtonames
    if "/" in context.active_object.name:
        ifc_class = context.active_object.name.split("/")[0]
        if ifc_class not in qtonames:
            psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, qto_only=True)
            qtonames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
        return qtonames[ifc_class]
    return []


class PsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    pset_name: EnumProperty(items=getPsetNames, name="Pset Name")
    qto_name: EnumProperty(items=getQtoNames, name="Qto Name")


class MaterialPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    pset_name: EnumProperty(items=getMaterialPsetNames, name="Pset Name")


class TaskPsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    qto_name: EnumProperty(items=getTaskQtoNames, name="Qto Name")


class ResourcePsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    qto_name: EnumProperty(items=getResourceQtoNames, name="Qto Name")


class ProfilePsetProperties(PropertyGroup):
    active_pset_id: IntProperty(name="Active Pset ID")
    active_pset_name: StringProperty(name="Pset Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    pset_name: EnumProperty(items=getProfilePsetNames, name="Pset Name")
