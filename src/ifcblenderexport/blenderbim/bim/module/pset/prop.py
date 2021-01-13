import bpy
from blenderbim.bim.prop import Attribute
import blenderbim.bim.schema
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


def getPsetNames(self, context):
    global psetnames
    if "/" in context.active_object.name:
        ifc_class = context.active_object.name.split("/")[0]
        if ifc_class not in psetnames:
            psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(ifc_class, pset_only=True)
            psetnames[ifc_class] = [(p.Name, p.Name, "") for p in psets]
        return psetnames[ifc_class]
    return []


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
