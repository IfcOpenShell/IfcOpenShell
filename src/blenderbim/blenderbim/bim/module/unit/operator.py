import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.unit.data import Data


class AssignUnit(bpy.types.Operator):
    bl_idname = "bim.assign_unit"
    bl_label = "Assign Unit"

    def execute(self, context):
        ifcopenshell.api.run("unit.assign_unit", IfcStore.get_file(), **self.get_units())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}

    def get_units(self):
        units = {
            "length": {
                "ifc": None,
                "is_metric": bpy.context.scene.unit_settings.system != "IMPERIAL",
                "raw": bpy.context.scene.unit_settings.length_unit,
            },
            "area": {
                "ifc": None,
                "is_metric": bpy.context.scene.unit_settings.system != "IMPERIAL",
                "raw": bpy.context.scene.unit_settings.length_unit,
            },
            "volume": {
                "ifc": None,
                "is_metric": bpy.context.scene.unit_settings.system != "IMPERIAL",
                "raw": bpy.context.scene.unit_settings.length_unit,
            },
        }
        for data in units.values():
            if data["raw"] == "ADAPTIVE":
                if data["is_metric"]:
                    data["raw"] = "METERS"
                else:
                    data["raw"] = "FEET"
        return units
