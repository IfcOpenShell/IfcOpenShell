import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_value": None, "attributes": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "AppliedValue" and value is not None:
                # TODO: support all applied value select types
                value = self.file.createIfcMonetaryMeasure(value)
            elif name == "UnitBasis":
                self.remove_existing_unit_basis()
                if value:
                    value_component = self.file.create_entity(
                        ifcopenshell.util.unit.get_unit_measure_type(value["UnitComponent"].UnitType),
                        value["ValueComponent"],
                    )
                    value = self.file.create_entity("IfcMeasureWithUnit", value_component, value["UnitComponent"])
            setattr(self.settings["cost_value"], name, value)

    def remove_existing_unit_basis(self):
        if (
            self.settings["cost_value"].UnitBasis
            and len(self.file.get_inverse(self.settings["cost_value"].UnitBasis)) == 1
        ):
            ifcopenshell.util.element.remove_deep(self.file, self.settings["cost_value"].UnitBasis)
