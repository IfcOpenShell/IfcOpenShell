import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.cost.data import Data
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


quantitytypes_enum = []


def purge():
    global quantitytypes_enum
    quantitytypes_enum = []


def getQuantityTypes(self, context):
    global quantitytypes_enum
    if len(quantitytypes_enum) == 0 and IfcStore.get_schema():
        quantitytypes_enum.clear()
        quantitytypes_enum = [("QTO", "Qto", "Derive quantities from IFC quantity sets")]
        quantitytypes_enum.extend(
            [
                (t.name(), t.name(), "")
                for t in IfcStore.get_schema().declaration_by_name("IfcPhysicalSimpleQuantity").subtypes()
            ]
        )
    return quantitytypes_enum


def updateCostItemName(self, context):
    if self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    props = context.scene.BIMCostProperties
    ifcopenshell.api.run(
        "cost.edit_cost_item",
        self.file,
        **{"cost_item": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    Data.load(IfcStore.get_file())
    if props.active_cost_item_id == self.ifc_definition_id:
        attribute = props.cost_item_attributes.get("Name")
        attribute.string_value = self.name


class CostItem(PropertyGroup):
    name: StringProperty(name="Name", update=updateCostItemName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class BIMCostProperties(PropertyGroup):
    cost_schedule_attributes: CollectionProperty(name="Cost Schedule Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_cost_schedule_id: IntProperty(name="Active Cost Schedule Id")
    cost_items: CollectionProperty(name="Work Calendar", type=CostItem)
    active_cost_item_id: IntProperty(name="Active Cost Id")
    cost_item_editing_type: StringProperty(name="Cost Item Editing Type")
    active_cost_item_index: IntProperty(name="Active Cost Item Index")
    cost_item_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    contracted_cost_items: StringProperty(name="Contracted Cost Items", default="[]")
    quantity_types: EnumProperty(items=getQuantityTypes, name="Quantity Types")
    qto_name: StringProperty(name="Qto Name")
    prop_name: StringProperty(name="Prop Name")
    active_cost_item_quantity_id: IntProperty(name="Active Cost Item Quantity Id")
    quantity_attributes: CollectionProperty(name="Quantity Attributes", type=Attribute)
    cost_types: EnumProperty(
        items=[
            ("FIXED", "Fixed", "The cost value is a fixed number"),
            ("SUM", "Sum", "The cost value is automatically derived from the sum of all nested cost items"),
            ("CATEGORY", "Category", "The cost value represents a single category"),
        ],
        name="Cost Types",
    )
    cost_category: StringProperty(name="Cost Category")
    active_cost_item_value_id: IntProperty(name="Active Cost Item Value Id")
    cost_value_attributes: CollectionProperty(name="Cost Value Attributes", type=Attribute)
