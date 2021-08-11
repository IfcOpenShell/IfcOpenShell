import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.cost.data import Data
from ifcopenshell.api.pset.data import Data as PsetData
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
quantitynames_enum = []
quantitynames_count = []


def purge():
    global quantitytypes_enum
    global quantitynames_enum
    global quantitynames_count
    quantitytypes_enum = []
    quantitynames_enum = []
    quantitynames_count = []


def getQuantityTypes(self, context):
    global quantitytypes_enum
    if len(quantitytypes_enum) == 0 and IfcStore.get_schema():
        quantitytypes_enum = []
        quantitytypes_enum.extend(
            [
                (t.name(), t.name(), "")
                for t in IfcStore.get_schema().declaration_by_name("IfcPhysicalSimpleQuantity").subtypes()
            ]
        )
    return quantitytypes_enum


def getQuantityNames(self, context):
    global quantitynames_enum
    global quantitynames_count
    ifc_file = IfcStore.get_file()
    total_selected_objects = len(context.selected_objects)
    if total_selected_objects != quantitynames_count or total_selected_objects == 1:
        quantitynames_enum = []
        quantitynames_count = total_selected_objects
        names = set()
        for obj in context.selected_objects:
            element_id = obj.BIMObjectProperties.ifc_definition_id
            if not element_id:
                continue
            potential_names = set()
            if element_id not in PsetData.products:
                PsetData.load(ifc_file, element_id)
            for qto_id in PsetData.products[element_id]["qtos"]:
                qto = PsetData.qtos[qto_id]
                [potential_names.add(PsetData.properties[p]["Name"]) for p in qto["Properties"]]
            names = names.intersection(potential_names) if names else potential_names
        quantitynames_enum.extend([(n, n, "") for n in names])
    return quantitynames_enum


def update_cost_item_index(self, context):
    bpy.ops.bim.load_cost_item_quantities()


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


class CostItemProduct(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    total_quantity: FloatProperty(name="Total Quantity")


class BIMCostProperties(PropertyGroup):
    cost_schedule_attributes: CollectionProperty(name="Cost Schedule Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_cost_schedule_id: IntProperty(name="Active Cost Schedule Id")
    cost_items: CollectionProperty(name="Cost Items", type=CostItem)
    active_cost_item_id: IntProperty(name="Active Cost Id")
    cost_item_editing_type: StringProperty(name="Cost Item Editing Type")
    active_cost_item_index: IntProperty(name="Active Cost Item Index", update=update_cost_item_index)
    cost_item_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    contracted_cost_items: StringProperty(name="Contracted Cost Items", default="[]")
    quantity_types: EnumProperty(items=getQuantityTypes, name="Quantity Types")
    quantity_names: EnumProperty(items=getQuantityNames, name="Quantity Names")
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
    cost_column: StringProperty(name="Cost Column")
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    columns: CollectionProperty(name="Columns", type=StrProperty)
    active_column_index: IntProperty(name="Active Column Index")
    cost_item_products: CollectionProperty(name="Cost Item Products", type=CostItemProduct)
    active_cost_item_product_index: IntProperty(name="Active Cost Item Product Index")
