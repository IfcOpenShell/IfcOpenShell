import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.spatial.data import Data
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


def getSpatialContainers(self, context, parent_id=None):
    Data.load()
    self.file = IfcStore.get_file()
    props = context.scene.BIMSpatialProperties
    while len(props.spatial_elements) > 0:
        props.spatial_elements.remove(0)

    if parent_id:
        props.active_decomposes_id = parent_id

    try:
        self.file.by_id(props.active_decomposes_id)
    except:
        props.active_decomposes_id = 0

    project_id = self.file.by_type("IfcProject")[0].id()

    if not props.active_decomposes_id:
        props.active_decomposes_id = project_id

    for ifc_definition_id, spatial_element in Data.spatial_elements.items():
        if spatial_element["Decomposes"] == props.active_decomposes_id:
            new = props.spatial_elements.add()
            new.name = spatial_element["Name"] or "Unnamed"
            new.long_name = spatial_element["LongName"] or ""
            new.has_decomposition = bool(spatial_element["IsDecomposedBy"])
            new.ifc_definition_id = ifc_definition_id

    if props.active_decomposes_id == project_id:
        props.active_decomposes_parent_id = 0
    else:
        props.active_decomposes_parent_id = Data.spatial_elements[props.active_decomposes_id]["Decomposes"]


class SpatialElement(PropertyGroup):
    name: StringProperty(name="Name")
    long_name: StringProperty(name="Long Name")
    has_decomposition: BoolProperty(name="Has Decomposition")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMSpatialProperties(PropertyGroup):
    spatial_elements: CollectionProperty(name="Spatial Elements", type=SpatialElement)
    active_spatial_element_index: IntProperty(name="Active Spatial Element Index")
    active_decomposes_id: IntProperty(name="Active Decomposes Id")
    active_decomposes_parent_id: IntProperty(name="Active Decomposes Parent Id")


class BIMObjectSpatialProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
