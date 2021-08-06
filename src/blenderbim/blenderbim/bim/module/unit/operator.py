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


class LoadUnits(bpy.types.Operator):
    bl_idname = "bim.load_units"
    bl_label = "Load Units"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMUnitProperties
        while len(props.units) > 0:
            props.units.remove(0)

        for ifc_definition_id in Data.unit_assignment:
            unit = Data.units[ifc_definition_id]
            name = unit.get("Name", "")

            if unit["type"] == "IfcMonetaryUnit":
                name = unit["Currency"]

            if unit["type"] == "IfcSIUnit" and unit["Prefix"]:
                if "_" in name:
                    name_components = name.split("_")
                    name = f"{name_components[0]} {unit['Prefix']}{name_components[1]}"
                else:
                    name = f"{unit['Prefix']}{name}"

            icon = "MOD_MESHDEFORM"
            if unit["type"] == "IfcSIUnit":
                icon = "SNAP_GRID"
            elif unit["type"] == "IfcMonetaryUnit":
                icon = "COPY_ID"

            unit_type = unit.get("UserDefinedType", None)
            if not unit_type:
                unit_type = unit.get("UnitType", None)

            new = props.units.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = name
            new.unit_type = unit_type
            new.icon = icon

        props.is_editing = True
        # bpy.ops.bim.disable_editing_unit()
        return {"FINISHED"}
