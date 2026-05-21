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

from typing import TYPE_CHECKING, Any, Literal, cast, get_args

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from bonsai.bim.module.misc.data import QuickFavoritesData

QuickFavoriteValueType = Literal["float_value", "bool_value", "int_value", "string_value", "enum_value"]


class QuickFavoriteEnumItem(PropertyGroup):
    name: StringProperty(name="Name", default="")
    display_name: StringProperty(name="Display Name", default="")
    description: StringProperty(name="Description", default="")

    if TYPE_CHECKING:
        name: str
        display_name: str
        description: str


def get_enum_items(self: "QuickFavoriteProperty", context: bpy.types.Context | None) -> list[tuple[str, str, str]]:
    return [(item.name, item.display_name, item.description) for item in self.enum_items]


class QuickFavoriteProperty(PropertyGroup):
    name: StringProperty(name="Name", default="")
    display_name: StringProperty(name="Display Name", default="")
    value_prop: EnumProperty(
        name="Value Prop",
        items=tuple((v, v, "") for v in get_args(QuickFavoriteValueType)),
    )
    string_value: StringProperty(name="String Value", default="")
    float_value: FloatProperty(name="Float Value", default=0.0)
    int_value: IntProperty(name="Int Value", default=0)
    bool_value: BoolProperty(name="Bool Value", default=False)
    enum_value: EnumProperty(name="Enum Value", items=get_enum_items)
    enum_items: CollectionProperty(type=QuickFavoriteEnumItem)
    is_active: BoolProperty(
        name="Is Active",
        description="Only active properties will be added to the operator when invoked from Quick Favorites",
        default=False,
    )

    def set_value(self, value: Any) -> None:
        setattr(self, self.value_prop, value)

    def set_enum_items(self, items: list[tuple[str, str, str]]) -> None:
        self.enum_items.clear()
        for identifier, name, description in items:
            item = self.enum_items.add()
            item.name = identifier
            item.display_name = name
            item.description = description

    if TYPE_CHECKING:
        name: str
        display_name: str
        value_prop: QuickFavoriteValueType
        string_value: str
        float_value: float
        int_value: int
        bool_value: bool
        enum_value: str
        enum_items: bpy.types.bpy_prop_collection_idprop[QuickFavoriteEnumItem]
        is_active: bool


def get_operator_suggestions(self: "QuickFavoritesItem", context: bpy.types.Context, edit_text: str) -> list[str]:
    if not QuickFavoritesData.is_loaded:
        QuickFavoritesData.load()
    return QuickFavoritesData.data["operators"]


class QuickFavoritesItem(PropertyGroup):
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    search: StringProperty(
        name="Search",
        default="",
        search=get_operator_suggestions,
        # Resetting `search_options`, allowing users only to use suggestions.
        search_options=set(),
    )
    properties: CollectionProperty(type=QuickFavoriteProperty)
    operator_id: StringProperty(
        name="Operator ID",
        default="",
    )
    label: StringProperty(
        name="Label",
        description="Label that will be used in Quick Favorites for this operator",
        default="",
    )

    def get_searched_operator(self) -> bpy.types.Struct | None:
        if not self.search:
            return None
        search_label = self.search
        name = search_label.split(" - ", 1)[0]
        module, func = name.split(".", 1)
        op = getattr(getattr(bpy.ops, module), func)
        rna = cast(bpy.types.Struct, op.get_rna_type())
        return rna

    if TYPE_CHECKING:
        is_expanded: bool
        search: str
        """Internal property set when confirming results of the search field"""
        properties: bpy.types.bpy_prop_collection_idprop[QuickFavoriteProperty]
        operator_id: str
        label: str


class BIMMiscProperties(PropertyGroup):
    total_storeys: IntProperty(
        name="Total Storeys",
        description="Number of storeys above object's storey to take into account for resizing",
        default=1,
    )
    override_colour: FloatVectorProperty(
        name="Override Colour", subtype="COLOR", default=(1, 0, 0, 1), min=0.0, max=1.0, size=4
    )
    quick_favorites: CollectionProperty(type=QuickFavoritesItem)

    if TYPE_CHECKING:
        total_storeys: int
        override_colour: tuple[float, float, float, float]
        quick_favorites: bpy.types.bpy_prop_collection_idprop[QuickFavoritesItem]
