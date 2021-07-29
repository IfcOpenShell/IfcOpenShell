import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.unit.data import Data


class AssignUnit(bpy.types.Operator):
    bl_idname = "bim.assign_unit"
    bl_label = "Assign Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("unit.assign_unit", IfcStore.get_file(), **self.get_units(context))
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

    def get_units(self, context):
        scene = context.scene
        units = {
            "length": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
            "area": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
            "volume": {
                "ifc": None,
                "is_metric": scene.unit_settings.system != "IMPERIAL",
                "raw": scene.unit_settings.length_unit,
            },
        }
        for data in units.values():
            if data["raw"] == "ADAPTIVE":
                if data["is_metric"]:
                    data["raw"] = "METERS"
                else:
                    data["raw"] = "FEET"
        return units
