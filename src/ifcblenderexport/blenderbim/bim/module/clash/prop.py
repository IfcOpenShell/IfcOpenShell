import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.owner.data import Data
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


class ClashSource(PropertyGroup):
    name: StringProperty(name="File")
    selector: StringProperty(name="Selector")
    mode: EnumProperty(
        items=[
            ("i", "Include", "Only the selected objects are included for clashing"),
            ("e", "Exclude", "All objects except the selected objects are included for clashing"),
        ],
        name="Mode",
    )


class ClashSet(PropertyGroup):
    name: StringProperty(name="Name")
    tolerance: FloatProperty(name="Tolerance")
    a: CollectionProperty(name="Group A", type=ClashSource)
    b: CollectionProperty(name="Group B", type=ClashSource)


class SmartClashGroup(PropertyGroup):
    number: StringProperty(name="Number")
    global_ids: CollectionProperty(name="GlobalIDs", type=StrProperty)


class BIMClashProperties(PropertyGroup):
    blender_clash_set_a: CollectionProperty(name="Blender Clash Set A", type=StrProperty)
    blender_clash_set_b: CollectionProperty(name="Blender Clash Set B", type=StrProperty)
    clash_sets: CollectionProperty(name="Clash Sets", type=ClashSet)
    should_create_clash_snapshots: BoolProperty(name="Create Snapshots", default=True)
    clash_results_path: StringProperty(name="Clash Results Path")
    smart_grouped_clashes_path: StringProperty(name="Smart Grouped Clashes Path")
    active_clash_set_index: IntProperty(name="Active Clash Set Index")
    smart_clash_groups: CollectionProperty(name="Smart Clash Groups", type=SmartClashGroup)
    active_smart_group_index: IntProperty(name="Active Smart Group Index")
    smart_clash_grouping_max_distance: IntProperty(
        name="Smart Clash Grouping Max Distance", default=3, soft_min=1, soft_max=10
    )
