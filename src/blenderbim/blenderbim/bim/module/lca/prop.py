
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
import olca
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

productsystems_enum = []


def purge():
    global productsystems_enum
    productsystems_enum = []


def get_product_systems(self, context):
    global productsystems_enum
    if not len(productsystems_enum):
        client = olca.Client(context.preferences.addons["blenderbim"].preferences.openlca_port)
        try:
            productsystems_enum = [
                (ps.name, ps.name, "") for ps in client.get_all(olca.ProductSystem)
            ]
        except:
            pass
    return productsystems_enum


class BIMLCAProperties(PropertyGroup):
    amount: FloatProperty(name="Amount")
    product_systems: EnumProperty(items=get_product_systems, name="Product Systems")
