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
import importlib.util
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
        ifcpatch_path = Path(
            importlib.util.find_spec("ifcpatch").submodule_search_locations[0]
        )
        for filename in ifcpatch_path.joinpath("recipes").glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            docs = ifcpatch.extract_docs(
                f, "Patcher", "__init__", ("src", "file", "logger", "args")
            )
            ifcpatchrecipes_enum.append(
                (f, f, docs.get("description", "") if docs else "")
            )
    return sorted(ifcpatchrecipes_enum, key=lambda x: x[0])


def update_ifc_patch_recipe(self, context):
    bpy.ops.bim.update_ifc_patch_arguments(recipe=self.ifc_patch_recipes)


def get_patch_props(context):
    return context.scene.BIMPatchProperties


def update_coordinate_mode(self, context):
    props = get_patch_props(context)
    mode = props.ifc_patch_args_attr.get("mode")
    setattr(mode, "string_value", props.ifc_patch_reset_absolute_coordinates_mode)


def update_coordinate_threshold(self, context):
    props = get_patch_props(context)
    offset = props.ifc_patch_reset_absolute_coordinates_offset
    offset_threshold = props.ifc_patch_reset_absolute_coordinates_threshold
    threshold = props.ifc_patch_args_attr.get("d")
    threshold.set_value(offset_threshold if offset != "select" else "0")


def update_coordinate_offset(self, context):
    props = get_patch_props(context)
    x = props.ifc_patch_args_attr.get("a")
    y = props.ifc_patch_args_attr.get("b")
    z = props.ifc_patch_args_attr.get("c")
    offset_x = props.ifc_patch_reset_absolute_coordinates_offset_x
    offset_y = props.ifc_patch_reset_absolute_coordinates_offset_y
    offset_z = props.ifc_patch_reset_absolute_coordinates_offset_z
    x.set_value(offset_x)
    y.set_value(offset_y)
    z.set_value(offset_z)


class BIMPatchProperties(PropertyGroup):
    ifc_patch_recipes: EnumProperty(
        items=get_ifcpatch_recipes, name="Recipes", update=update_ifc_patch_recipe
    )
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
    ifc_patch_args_attr: CollectionProperty(type=Attribute, name="Arguments")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
    ifc_patch_reset_absolute_coordinates_mode: EnumProperty(
        items=(
            ("geometry", "Geometry", "Geometry"),
            ("placement", "Placement", "Placement"),
            ("both", "Both", "Both"),
        ),
        name="Mode",
        default="geometry",
        update=update_coordinate_mode,
    )
    ifc_patch_reset_absolute_coordinates_offset: EnumProperty(
        items=(
            ("auto", "Auto", "Auto"),
            ("manual", "Manual", "Manual"),
            ("select", "Please Select", "Please Select"),
        ),
        name="Offset",
        default="select",
        update=update_coordinate_threshold,
    )
    ifc_patch_reset_absolute_coordinates_threshold: StringProperty(
        name="Offset Value",
        default="1000000",
        update=update_coordinate_threshold,
    )
    ifc_patch_reset_absolute_coordinates_offset_x: StringProperty(
        name="a", default="0", update=update_coordinate_offset
    )
    ifc_patch_reset_absolute_coordinates_offset_y: StringProperty(
        name="b", default="0", update=update_coordinate_offset
    )
    ifc_patch_reset_absolute_coordinates_offset_z: StringProperty(
        name="c", default="0", update=update_coordinate_offset
    )
