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
import importlib
from pathlib import Path
import ifcpatch
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


ifcpatchrecipes_enum = []


def purge():
    global ifcpatchrecipes_enum
    ifcpatchrecipes_enum = []


def get_ifcpatch_recipes(self, context):
    global ifcpatchrecipes_enum
    if len(ifcpatchrecipes_enum) < 1:
        ifcpatchrecipes_enum.clear()
        ifcpatch_path = Path(importlib.util.find_spec("ifcpatch").submodule_search_locations[0])
        for filename in ifcpatch_path.joinpath("recipes").glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            docs = ifcpatch.extract_docs(f, "Patcher", "__init__", ("src", "file", "logger", "args"))
            ifcpatchrecipes_enum.append((f, f, docs.get("description", "") if docs else ""))
    return ifcpatchrecipes_enum


def update_ifc_patch_recipe(self, context):
    bpy.ops.bim.update_ifc_patch_arguments(recipe=self.ifc_patch_recipes)


class BIMPatchProperties(PropertyGroup):
    ifc_patch_recipes: EnumProperty(items=get_ifcpatch_recipes, name="Recipes", update=update_ifc_patch_recipe)
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
    ifc_patch_args_attr: CollectionProperty(type=Attribute, name="Arguments")
