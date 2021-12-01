import ifcopenshell
import ifcopenshell.util.unit


class Data:
    is_loaded = False
    units = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.unit_assignment = []
        cls.units = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.file = file
        cls.unit_assignment = []
        cls.units = {}
        unit_assignment = cls.file.by_type("IfcUnitAssignment")
        if not unit_assignment:
            return
        for unit in unit_assignment[0].Units:
            cls.unit_assignment.append(unit.id())
        for unit in (
            cls.file.by_type("IfcDerivedUnit") + cls.file.by_type("IfcNamedUnit") + cls.file.by_type("IfcMonetaryUnit")
        ):
            cls.load_unit(unit)
        cls.is_loaded = True

    @classmethod
    def load_unit(cls, unit):
        if unit.is_a("IfcDerivedUnit"):
            data = unit.get_info()
            data["Elements"] = [{"Unit": e.Unit.id(), "Exponent": e.Exponent} for e in unit.Elements]
            for element in unit.Elements:
                cls.load_unit(element.Unit)
            cls.units[unit.id()] = data
        elif unit.is_a("IfcNamedUnit"):
            data = unit.get_info()
            if unit.is_a("IfcSIUnit"):
                data["Dimensions"] = ifcopenshell.util.unit.get_si_dimensions(unit.Name)
            else:
                data["Dimensions"] = unit.Dimensions.get_info()
            if unit.is_a("IfcConversionBasedUnit"):
                conversion_factor = unit.ConversionFactor.get_info()
                cls.load_unit(unit.ConversionFactor.UnitComponent)
                conversion_factor["UnitComponent"] = unit.ConversionFactor.UnitComponent.id()
                data["ConversionFactor"] = conversion_factor
            cls.units[unit.id()] = data
        elif unit.is_a("IfcMonetaryUnit"):
            cls.units[unit.id()] = unit.get_info()
