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

from typing import TYPE_CHECKING, Literal, get_args

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

QuickFavoriteValueType = Literal["float_value", "bool_value", "int_value", "string_value"]


class QuickFavoriteProperty(PropertyGroup):
    name: StringProperty(name="Name", default="")  # pyright: ignore[reportRedeclaration]
    display_name: StringProperty(name="Display Name", default="")  # pyright: ignore[reportRedeclaration]
    value_prop: EnumProperty(  # pyright: ignore[reportRedeclaration]
        name="Value Prop",
        items=tuple((v, v, "") for v in get_args(QuickFavoriteValueType)),
    )
    string_value: StringProperty(name="String Value", default="")  # pyright: ignore[reportRedeclaration]
    float_value: FloatProperty(name="Float Value", default=0.0)  # pyright: ignore[reportRedeclaration]
    int_value: IntProperty(name="Int Value", default=0)  # pyright: ignore[reportRedeclaration]
    bool_value: BoolProperty(name="Bool Value", default=False)  # pyright: ignore[reportRedeclaration]
    is_active: BoolProperty(  # pyright: ignore[reportRedeclaration]
        name="Is Active",
        description="Only active properties will be added to the operator when invoked from Quick Favorites",
        default=False,
    )

    if TYPE_CHECKING:
        name: str
        display_name: str
        value_prop: QuickFavoriteValueType
        string_value: str
        float_value: float
        int_value: int
        bool_value: bool
        is_active: bool


class QuickFavoritesItem(PropertyGroup):
    is_expanded: BoolProperty(name="Is Expanded", default=True)  # pyright: ignore[reportRedeclaration]
    search: StringProperty(name="Search", default="")  # pyright: ignore[reportRedeclaration]
    properties: CollectionProperty(type=QuickFavoriteProperty)  # pyright: ignore[reportRedeclaration]
    operator_id: StringProperty(name="Operator ID", default="")  # pyright: ignore[reportRedeclaration]
    label: StringProperty(  # pyright: ignore[reportRedeclaration]
        name="Label",
        description="Label that will be used in Quick Favorites for this operator",
        default="",
    )

    if TYPE_CHECKING:
        is_expanded: bool
        search: str
        properties: bpy.types.bpy_prop_collection_idprop[QuickFavoriteProperty]
        operator_id: str
        label: str


class BIMMiscProperties(PropertyGroup):
    total_storeys: IntProperty(  # pyright: ignore[reportRedeclaration]
        name="Total Storeys",
        description="Number of storeys above object's storey to take into account for resizing",
        default=1,
    )
    override_colour: FloatVectorProperty(  # pyright: ignore[reportRedeclaration]
        name="Override Colour", subtype="COLOR", default=(1, 0, 0, 1), min=0.0, max=1.0, size=4
    )
    quick_favorites: CollectionProperty(type=QuickFavoritesItem)  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        total_storeys: int
        override_colour: tuple[float, float, float, float]
        quick_favorites: bpy.types.bpy_prop_collection_idprop[QuickFavoritesItem]
