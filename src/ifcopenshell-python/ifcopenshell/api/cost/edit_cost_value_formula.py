import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.unit
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_value": None, "formula": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        try:
            data = ifcopenshell.util.cost.unserialise_cost_value(self.settings["formula"], self.settings["cost_value"])
        except:
            return
        self.edit_cost_value(data)

    def edit_cost_value(self, data, parent=None):
        ifc = data.get("ifc", None)
        if not ifc:
            ifc = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=parent)
        if "AppliedValue" in data:
            if data["AppliedValue"]:
                ifc.AppliedValue = self.file.createIfcMonetaryMeasure(data["AppliedValue"])
            else:
                ifc.AppliedValue = None
        ifc.Category = data["Category"] if "Category" in data else None
        ifc.ArithmeticOperator = data["ArithmeticOperator"] if "ArithmeticOperator" in data else None
        if "Components" in data:
            for component in data["Components"]:
                self.edit_cost_value(component, ifc)
