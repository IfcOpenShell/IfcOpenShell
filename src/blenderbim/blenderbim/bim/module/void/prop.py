import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty


class VoidProperties(PropertyGroup):
    desired_opening: PointerProperty(name="Desired Opening To Fill", type=bpy.types.Object)
