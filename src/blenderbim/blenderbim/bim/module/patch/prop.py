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
from .helper import extract_docs
from .operator import UpdateIfcPatchArguments


ifcpatchrecipes_enum = []


def purge():
    global ifcpatchrecipes_enum
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
            docs = extract_docs(ifcpatch, f, "Patcher", "__init__", ("src", "file", "logger", "args"))
            ifcpatchrecipes_enum.append((f, f, docs.get("description","") if docs else ""))
    return ifcpatchrecipes_enum

def update_ifc_patch_recipe(self, context):
    bpy.ops.bim.update_ifc_patch_arguments(recipe = self.ifc_patch_recipes)


class BIMPatchProperties(PropertyGroup):
    ifc_patch_recipes: EnumProperty(items=getIfcPatchRecipes, name="Recipes", update=update_ifc_patch_recipe)
    ifc_patch_input: StringProperty(default="", name="IFC Patch Input IFC")
    ifc_patch_output: StringProperty(default="", name="IFC Patch Output IFC")
    ifc_patch_args: StringProperty(default="", name="Arguments")
    ifc_patch_args_attr: CollectionProperty(type=Attribute, name="Arguments")
