import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "map_conversion": {},
            "projected_crs": {},
            "map_unit": "",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        map_conversion = self.file.by_type("IfcMapConversion")[0]
        projected_crs = self.file.by_type("IfcProjectedCRS")[0]
        for name, value in self.settings["map_conversion"].items():
            setattr(map_conversion, name, value)
        for name, value in self.settings["projected_crs"].items():
            setattr(projected_crs, name, value)
        self.remove_existing_map_unit(projected_crs)
        self.set_map_unit(projected_crs)

    def remove_existing_map_unit(self, projected_crs):
        if projected_crs.MapUnit and len(self.file.get_inverse(projected_crs.MapUnit)) == 1:
            # TODO: go deeper for conversion units
            self.file.remove(projected_crs.MapUnit)

    def set_map_unit(self, projected_crs):
        if not self.settings["map_unit"]:
            return

        if "METRE" in self.settings["map_unit"]:
            projected_crs.MapUnit = self.file.createIfcSIUnit(
                None,
                "LENGTHUNIT",
                ifcopenshell.util.unit.get_prefix(self.settings["map_unit"]),
                ifcopenshell.util.unit.get_unit_name(self.settings["map_unit"]),
            )
            return

        value_component = self.file.create_entity(
            "IfcReal", **{"wrappedValue": ifcopenshell.util.unit.si_conversions[self.settings["map_unit"]]}
        )
        si_unit = self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        projected_crs.MapUnit = self.file.createIfcConversionBasedUnit(
            self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0),
            "LENGTHUNIT",
            self.settings["map_unit"],
            self.file.createIfcMeasureWithUnit(value_component, si_unit),
        )
