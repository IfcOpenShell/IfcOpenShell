# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bonsai.bim.prop import StrProperty


class BIMCityJsonProperties(PropertyGroup):
    def get_lods(self, context):
        global LODS_ENUM_ITEMS
        LODS_ENUM_ITEMS = [(item.name, "LOD" + item.name, "Level of Detail " + item.name) for item in self.lods]
        return LODS_ENUM_ITEMS

    # TODO: instead of subtype it would be nice to have a helper operator that allows filtered file browsing
    input: StringProperty(name="CityJSON Input", default="", subtype="FILE_PATH")
    output: StringProperty(name="IFC Output", default="", subtype="FILE_PATH")
    name: StringProperty(name="Identifier", default="")
    split_lod: BoolProperty(name="Should Split LOD", default=True)
    lods: CollectionProperty(name="LODs", type=StrProperty)
    lod: EnumProperty(name="LOD", description="", items=get_lods, options={"ANIMATABLE"}, default=None)
    is_lod_found: BoolProperty(name="Is LOD Found", default=False)
    load_after_convert: BoolProperty(name="Load After Converting", default=True)
