import ifcopenshell
import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"unit_type": "LENGTHUNIT", "name": "METRE", "prefix": None, "conversion_offset": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["unit_type"] == "LENGTHUNIT":
            dimensional_exponents = self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
            si_unit = self.file.createIfcSIUnit(UnitType=self.settings["unit_type"], Name="METRE")
        elif self.settings["unit_type"] == "AREAUNIT":
            dimensional_exponents = self.file.createIfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
            si_unit = self.file.createIfcSIUnit(UnitType=self.settings["unit_type"], Name="SQUARE_METRE")
        elif self.settings["unit_type"] == "VOLUMEUNIT":
            dimensional_exponents = self.file.createIfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
            si_unit = self.file.createIfcSIUnit(UnitType=self.settings["unit_type"], Name="CUBIC_METRE")

        conversion_real = ifcopenshell.util.unit.si_conversions.get(self.settings["name"], 1)
        value_component = self.file.create_entity("IfcReal", **{"wrappedValue": conversion_real})
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)

        if self.settings["conversion_offset"]:
            return self.file.createIfcConversionBasedUnit(
                dimensional_exponents,
                self.settings["unit_type"],
                self.settings["name"],
                conversion_factor,
                self.settings["conversion_offset"],
            )
        return self.file.createIfcConversionBasedUnit(
            dimensional_exponents, self.settings["unit_type"], self.settings["name"], conversion_factor
        )
