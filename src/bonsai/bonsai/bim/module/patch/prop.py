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

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Union

import bpy
import ifcpatch
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from bonsai.bim.prop import Attribute

ifcpatchrecipes_enum: list[tuple[str, str, str]] = []


def purge():
    global ifcpatchrecipes_enum
    ifcpatchrecipes_enum = []


def get_ifcpatch_recipes(self: "BIMPatchProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
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
            if docs is None:
                description = ""
            else:
                description = docs["description"]
                inputs = docs["inputs"]
                if inputs:
                    if description:
                        description += "\n\n"
                    description += "Parameters:"
                    for param, input_data in inputs.items():
                        description += f"\n\n- {param}: {input_data['description']}"
            ifcpatchrecipes_enum.append((f, f, description))
        ifcpatchrecipes_enum.sort(key=lambda x: x[0])
    return ifcpatchrecipes_enum


def update_ifc_patch_recipe(self: "BIMPatchProperties", context: bpy.types.Context) -> None:
    bpy.ops.bim.update_ifc_patch_arguments(recipe=self.ifc_patch_recipes)
    # Blender's script.execute_preset mutates the menu class's bl_label to
    # the loaded preset's display name (used as a "currently selected"
    # indicator). The label persists across recipe changes — making the new
    # recipe's menu falsely show the previous recipe's preset name. Reset
    # the label to the menu's canonical title so it always matches the
    # active recipe's preset list.
    menu_cls = getattr(bpy.types, "BIM_MT_ifc_patch_presets", None)
    if menu_cls is not None:
        menu_cls.bl_label = "IFC Patch Presets"


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

    if TYPE_CHECKING:
        ifc_patch_recipes_enum: Union[Literal["-"], str]
        ifc_patch_input: str
        ifc_patch_output: str
        ifc_patch_args_attr: bpy.types.bpy_prop_collection_idprop[Attribute]
        should_load_from_memory: bool
