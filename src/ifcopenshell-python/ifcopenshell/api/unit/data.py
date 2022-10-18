# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

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
