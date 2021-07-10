import ifcopenshell.util.unit


class Usecase():
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "length": {
                "is_metric": True,
                "raw": "MILLIMETERS"
            },
            "area": {
                "is_metric": True,
                "raw": "METERS"
            },
            "volume": {
                "is_metric": True,
                "raw": "METERS"
            },
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for unit_type, data in self.settings.items():
            if data["is_metric"]:
                data["ifc"] = self.create_metric_unit(unit_type, data)
            else:
                data["ifc"] = self.create_imperial_unit(unit_type, data)
        unit_assignment = self.file.by_type("IfcUnitAssignment")
        if unit_assignment:
            unit_assignment = unit_assignment[0]
            # TODO: handle unit rewriting, which is complicated
        else:
            unit_assignment = self.file.createIfcUnitAssignment([u["ifc"] for u in self.settings.values()])
            if self.file.schema == "IFC2X3":
                self.file.by_type("IfcProject")[0].UnitsInContext = unit_assignment
            else:
                self.file.by_type("IfcContext")[0].UnitsInContext = unit_assignment
        return unit_assignment

    def create_metric_unit(self, unit_type, data):
        type_prefix = ""
        if unit_type == "area":
            type_prefix = "SQUARE_"
        elif unit_type == "volume":
            type_prefix = "CUBIC_"
        return self.file.createIfcSIUnit(
            None,
            "{}UNIT".format(unit_type.upper()),
            ifcopenshell.util.unit.get_prefix(data["raw"]),
            type_prefix + ifcopenshell.util.unit.get_unit_name(data["raw"]),
        )

    def create_imperial_unit(self, unit_type, data):
        if unit_type == "length":
            dimensional_exponents = self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
            name_prefix = ""
        elif unit_type == "area":
            dimensional_exponents = self.file.createIfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
            name_prefix = "square"
        elif unit_type == "volume":
            dimensional_exponents = self.file.createIfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
            name_prefix = "cubic"
        si_unit = self.file.createIfcSIUnit(
            None,
            "{}UNIT".format(unit_type.upper()),
            None,
            "{}METRE".format(name_prefix.upper() + "_" if name_prefix else ""),
        )
        if data["raw"] == "INCHES":
            name = "{}inch".format(name_prefix + " " if name_prefix else "")
        elif data["raw"] == "FEET":
            name = "{}foot".format(name_prefix + " " if name_prefix else "")
        value_component = self.file.create_entity("IfcReal", **{"wrappedValue": ifcopenshell.util.unit.si_conversions[name]})
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)
        return self.file.createIfcConversionBasedUnit(
            dimensional_exponents, "{}UNIT".format(unit_type.upper()), name, conversion_factor
        )
