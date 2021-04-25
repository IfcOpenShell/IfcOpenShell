import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data
from blenderbim.bim.prop import StrProperty, Attribute
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


def updateResourceName(self, context):
    props = context.scene.BIMResourceProperties
    if not props.is_resource_update_enabled or self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "resource.edit_resource",
        self.file,
        **{"resource": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    Data.load(IfcStore.get_file())
    if props.active_resource_id == self.ifc_definition_id:
        attribute = props.resource_attributes.get("Name")
        attribute.string_value = self.name


class Resource(PropertyGroup):
    name: StringProperty(name="Name", update=updateResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class BIMResourceTreeProperties(PropertyGroup):
    resources: CollectionProperty(name="Resources", type=Resource)


class BIMResourceProperties(PropertyGroup):
    resource_attributes: CollectionProperty(name="Resource Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing")
    active_resource_index: IntProperty(name="Active Resource Index")
    active_resource_id: IntProperty(name="Active Resource Id")
    contracted_resources: StringProperty(name="Contracted Resources", default="[]")
    is_resource_update_enabled: BoolProperty(name="Is Resource Update Enabled", default=True)
    is_loaded: BoolProperty(name="Is Editing")
