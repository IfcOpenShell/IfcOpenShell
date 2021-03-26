import bpy
import importlib
from pathlib import Path
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


def getIfcPatchRecipes(self, context):
    global ifcpatchrecipes_enum
    if len(ifcpatchrecipes_enum) < 1:
        ifcpatchrecipes_enum.clear()
        ifcpatch_path = Path(importlib.util.find_spec("ifcpatch").submodule_search_locations[0])
        for filename in ifcpatch_path.joinpath("recipes").glob("*.py"):
            f = str(filename.stem)
            if f == "__init__":
                continue
            ifcpatchrecipes_enum.append((f, f, ""))
    return ifcpatchrecipes_enum


class BIMPatchProperties(PropertyGroup):
    ifc_patch_recipes: EnumProperty(items=getIfcPatchRecipes, name="Recipes")
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
