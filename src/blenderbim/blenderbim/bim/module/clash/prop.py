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
    should_create_clash_snapshots: BoolProperty(name="Create Snapshots", default=False)
    clash_results_path: StringProperty(name="Clash Results Path")
    smart_grouped_clashes_path: StringProperty(name="Smart Grouped Clashes Path")
    active_clash_set_index: IntProperty(name="Active Clash Set Index")
    smart_clash_groups: CollectionProperty(name="Smart Clash Groups", type=SmartClashGroup)
    active_smart_group_index: IntProperty(name="Active Smart Group Index")
    smart_clash_grouping_max_distance: IntProperty(
        name="Smart Clash Grouping Max Distance", default=3, soft_min=1, soft_max=10
    )

    @property
    def active_clash_set(self):
        if not self.clash_sets:
            return None
        return self.clash_sets[self.active_clash_set_index]

    @property
    def active_smart_group(self):
        if not self.smart_clash_groups:
            return None
        return self.smart_clash_groups[self.active_smart_group_index]
