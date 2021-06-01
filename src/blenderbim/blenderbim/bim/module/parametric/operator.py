import bpy
from blenderbim.bim.ifc import IfcStore


class ActivateParametricEngine(bpy.types.Operator):
    bl_idname = "bim.activate_parametric_engine"
    bl_label = "Activate Parametric Engine"

    def execute(self, context):
        return {"FINISHED"}
