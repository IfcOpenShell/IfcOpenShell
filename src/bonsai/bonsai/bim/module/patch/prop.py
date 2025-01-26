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
import importlib
import importlib.util
from pathlib import Path
import ifcpatch
from bonsai.bim.prop import StrProperty, Attribute
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
        # Have to add a blank entry because otherwise default recipe might be not loaded
        # properly (need to ensure bim.update_ifc_patch_arguments will be called). See #5540.
        ifcpatchrecipes_enum.append(("-", "-", ""))

        ifcpatch_path = Path(importlib.util.find_spec("ifcpatch").submodule_search_locations[0])
        for filename in ifcpatch_path.joinpath("recipes").glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            docs = ifcpatch.extract_docs(f, "Patcher", "__init__", ("src", "file", "logger", "args"))
            ifcpatchrecipes_enum.append((f, f, docs.get("description", "") if docs else ""))
        ifcpatchrecipes_enum.sort(key=lambda x: x[0])
    return ifcpatchrecipes_enum


def update_ifc_patch_recipe(self, context):
    bpy.ops.bim.update_ifc_patch_arguments(recipe=self.ifc_patch_recipes)


class BIMPatchProperties(PropertyGroup):
    ifc_patch_recipes: EnumProperty(items=get_ifcpatch_recipes, name="Recipes", update=update_ifc_patch_recipe)
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args_attr: CollectionProperty(type=Attribute, name="Arguments")
    should_load_from_memory: BoolProperty(
        default=False,
        name="Load from Memory",
        description="Use IFC file currently loaded in Bonsai",
    )
