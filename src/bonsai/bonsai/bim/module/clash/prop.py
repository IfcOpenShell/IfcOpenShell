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
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute, BIMFilterGroup
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
from mathutils import Vector
from typing import TYPE_CHECKING, Literal, Union


class ClashSource(PropertyGroup):
    name: StringProperty(name="File")
    filter_groups: CollectionProperty(type=BIMFilterGroup, name="Filter Groups")
    mode: EnumProperty(
        items=[
            ("a", "All Elements", "All elements will be used for clashing"),
            ("i", "Include", "Only the selected elements are included for clashing"),
            ("e", "Exclude", "All elements except the selected elements are included for clashing"),
        ],
        name="Mode",
    )

    if TYPE_CHECKING:
        filter_groups: bpy.types.bpy_prop_collection_idprop[BIMFilterGroup]
        mode: Literal["a", "i", "e"]


class Clash(PropertyGroup):
    a_global_id: StringProperty(name="A")
    b_global_id: StringProperty(name="B")
    a_name: StringProperty(name="A Name")
    b_name: StringProperty(name="B Name")
    status: BoolProperty(name="Status", default=False)

    if TYPE_CHECKING:
        a_global_id: str
        b_global_id: str
        a_name: str
        b_name: str
        status: bool


class ClashSet(PropertyGroup):
    mode: EnumProperty(
        items=[
            (
                "intersection",
                "Intersection",
                "Detect objects that protrude or pierce another object",
                "PIVOT_MEDIAN",
                1,
            ),
            ("collision", "Collision", "Detect touching objects with any surface collision", "PIVOT_INDIVIDUAL", 2),
            ("clearance", "Clearance", "Detect objects within a proximity threshold", "PIVOT_ACTIVE", 3),
        ],
        name="Mode",
    )
    tolerance: FloatProperty(name="Tolerance", default=0.002)
    clearance: FloatProperty(name="Clearance", default=0.01)
    allow_touching: BoolProperty(name="Allow Touching", default=False)
    check_all: BoolProperty(name="Check All", default=False)
    a: CollectionProperty(name="Group A", type=ClashSource)
    b: CollectionProperty(name="Group B", type=ClashSource)
    clashes: CollectionProperty(name="Clashes", type=Clash)

    if TYPE_CHECKING:
        mode: Literal["intersection", "collision", "clearance"]
        tolerance: float
        clearance: float
        allow_touching: bool
        check_all: bool
        a: bpy.types.bpy_prop_collection_idprop[ClashSource]
        b: bpy.types.bpy_prop_collection_idprop[ClashSource]
        clashes: bpy.types.bpy_prop_collection_idprop[Clash]


class SmartClashGroup(PropertyGroup):
    number: StringProperty(name="Number")
    global_ids: CollectionProperty(name="GlobalIDs", type=StrProperty)

    if TYPE_CHECKING:
        number: str
        global_ids: bpy.types.bpy_prop_collection_idprop[StrProperty]


class BIMClashProperties(PropertyGroup):
    blender_clash_set_a: CollectionProperty(name="Blender Clash Set A", type=StrProperty)
    blender_clash_set_b: CollectionProperty(name="Blender Clash Set B", type=StrProperty)
    clash_sets: CollectionProperty(name="Clash Sets", type=ClashSet)
    should_create_clash_snapshots: BoolProperty(
        name="Create Snapshots", description="Create bcf snapshots", default=False
    )
    clash_results_path: StringProperty(name="Clash Results Path")
    smart_grouped_clashes_path: StringProperty(name="Smart Grouped Clashes Path")
    active_clash_set_index: IntProperty(name="Active Clash Set Index")
    active_clash_index: IntProperty(name="Active Clash Index")
    smart_clash_groups: CollectionProperty(name="Smart Clash Groups", type=SmartClashGroup)
    active_smart_group_index: IntProperty(name="Active Smart Group Index")
    smart_clash_grouping_max_distance: IntProperty(
        name="Smart Clash Grouping Max Distance", default=3, soft_min=1, soft_max=10
    )
    p1: FloatVectorProperty(name="P1", default=(0.0, 0.0, 0.0), subtype="XYZ")
    p2: FloatVectorProperty(name="P2", default=(0.0, 0.0, 0.0), subtype="XYZ")
    active_clash_text: StringProperty(name="Active Clash Text")
    export_path: StringProperty(
        name="Export Path",
        description=".bcf or .json file to export the clash results to",
        subtype="FILE_PATH",
    )

    if TYPE_CHECKING:
        blender_clash_set_a: bpy.types.bpy_prop_collection_idprop[StrProperty]
        blender_clash_set_b: bpy.types.bpy_prop_collection_idprop[StrProperty]
        clash_sets: bpy.types.bpy_prop_collection_idprop[ClashSet]
        should_create_clash_snapshots: bool
        clash_results_path: str
        smart_grouped_clashes_path: str
        active_clash_set_index: int
        active_clash_index: int
        smart_clash_groups: bpy.types.bpy_prop_collection_idprop[SmartClashGroup]
        active_smart_group_index: int
        smart_clash_grouping_max_distance: int
        p1: Vector
        p2: Vector
        active_clash_text: str
        export_path: str

    @property
    def active_clash_set(self) -> Union[ClashSet, None]:
        return tool.Blender.get_active_uilist_element(self.clash_sets, self.active_clash_set_index)

    @property
    def active_smart_group(self) -> Union[SmartClashGroup, None]:
        return tool.Blender.get_active_uilist_element(self.smart_clash_groups, self.active_smart_group_index)

    @property
    def active_clash(self) -> Union[Clash, None]:
        if not (clash_set := self.active_clash_set):
            return None
        return tool.Blender.get_active_uilist_element(clash_set.clashes, self.active_clash_index)
