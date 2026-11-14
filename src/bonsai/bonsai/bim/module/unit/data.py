# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.util.attribute
import ifcopenshell.util.schema
import ifcopenshell.util.unit
from ifcopenshell.util.doc import get_entity_doc

import bonsai.tool as tool


def refresh():
    UnitsData.is_loaded = False


class UnitsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "assigned_units": cls.assigned_units(),
            "unit_classes": cls.unit_classes(),
            "named_unit_types": cls.named_unit_types(),
            "conversion_unit_types": cls.conversion_unit_types(),
            "derived_unit_types": cls.derived_unit_types(),
            "named_units": cls.named_units(),
            "total_units": cls.get_total_units(),
        }
        cls.is_loaded = True

    @classmethod
    def assigned_units(cls) -> list[tuple[str, str, str]]:
        unit_assignment = ifcopenshell.util.unit.get_unit_assignment(tool.Ifc.get())
        if not unit_assignment:
            return []
        priority = ("LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT")
        results = []
        for unit in unit_assignment.Units or []:
            if unit.is_a("IfcMonetaryUnit"):
                unit_type, name = "MONETARYUNIT", unit.Currency
            elif unit.is_a("IfcDerivedUnit"):
                unit_type = unit.UnitType
                if unit_type == "USERDEFINED" and unit.UserDefinedType:
                    unit_type = unit.UserDefinedType
                name = " ".join(
                    f"{ifcopenshell.util.unit.get_full_unit_name(e.Unit)}^{e.Exponent}" for e in unit.Elements
                )
            else:
                unit_type, name = unit.UnitType, ifcopenshell.util.unit.get_full_unit_name(unit)
            results.append((unit_type, name, unit.is_a()))
        results.sort(key=lambda r: (priority.index(r[0]) if r[0] in priority else len(priority), r[0]))
        return results

    @classmethod
    def unit_classes(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        assert (entity := tool.Ifc.schema().declaration_by_name("IfcNamedUnit").as_entity())
        declarations = ifcopenshell.util.schema.get_subtypes(entity)
        version = tool.Ifc.get_schema()
        classes = sorted([d.name() for d in declarations]) + ["IfcDerivedUnit", "IfcMonetaryUnit"]
        results = [
            (
                c,
                c,
                get_entity_doc(version, c).get("description", ""),
                tool.Unit.get_icon_for_unit_class(c),
                i,
            )
            for i, c in enumerate(classes)
        ]
        return results

    @classmethod
    def named_unit_types(cls):
        assert (entity := tool.Ifc.schema().declaration_by_name("IfcNamedUnit").as_entity())
        values = ifcopenshell.util.attribute.get_enum_items(entity.all_attributes()[1])
        return [(c, c, "") for c in sorted(values)]

    @classmethod
    def conversion_unit_types(cls):
        return [(u, u, "") for u in ifcopenshell.util.unit.si_conversions.keys()]

    @classmethod
    def derived_unit_types(cls):
        assert (entity := tool.Ifc.schema().declaration_by_name("IfcDerivedUnit").as_entity())
        values = ifcopenshell.util.attribute.get_enum_items(entity.all_attributes()[1])
        # USERDEFINED is skipped as it additionally requires a UserDefinedType.
        return [(c, c, "") for c in sorted(values) if c != "USERDEFINED"]

    @classmethod
    def named_units(cls):
        results = []
        for unit in sorted(tool.Ifc.get().by_type("IfcNamedUnit"), key=lambda u: u.id()):
            name = ifcopenshell.util.unit.get_full_unit_name(unit)
            results.append((str(unit.id()), f"{name} ({unit.UnitType})", ""))
        return results

    @classmethod
    def get_total_units(cls):
        ifc = tool.Ifc.get()
        return len(ifc.by_type("IfcDerivedUnit") + ifc.by_type("IfcNamedUnit") + ifc.by_type("IfcMonetaryUnit"))
