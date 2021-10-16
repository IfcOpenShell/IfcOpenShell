import ifcopenshell
import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"name": "foot", "conversion_offset": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        unit_type = ifcopenshell.util.unit.imperial_types.get(self.settings["name"], "USERDEFINED")
        dimensions = ifcopenshell.util.unit.named_dimensions[unit_type]
        exponents = self.file.createIfcDimensionalExponents(*dimensions)
        si_name = ifcopenshell.util.unit.si_type_names[unit_type]
        si_unit = self.file.createIfcSIUnit(UnitType=unit_type, Name=si_name)

        conversion_real = ifcopenshell.util.unit.si_conversions.get(self.settings["name"], 1)
        value_component = self.file.create_entity("IfcReal", **{"wrappedValue": conversion_real})
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)

        conversion_offset = self.settings["conversion_offset"]
        if not conversion_offset:
            conversion_offset = ifcopenshell.util.unit.si_offsets.get(self.settings["name"], 0)

        if conversion_offset:
            return self.file.createIfcConversionBasedUnitWithOffset(
                exponents, unit_type, self.settings["name"], conversion_factor, conversion_offset,
            )
        return self.file.createIfcConversionBasedUnit(
            exponents, unit_type, self.settings["name"], conversion_factor
        )
