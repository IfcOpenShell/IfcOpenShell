# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.schema
import ifcopenshell.util.attribute
import blenderbim.tool as tool


def refresh():
    UnitsData.is_loaded = False


class UnitsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "unit_classes": cls.unit_classes(),
            "named_unit_types": cls.named_unit_types(),
            "conversion_unit_types": cls.conversion_unit_types(),
            "total_units": cls.get_total_units(),
        }
        cls.is_loaded = True

    @classmethod
    def unit_classes(cls):
        declarations = ifcopenshell.util.schema.get_subtypes(tool.Ifc.schema().declaration_by_name("IfcNamedUnit"))
        results = [(c, c, "") for c in sorted([d.name() for d in declarations])]
        results.extend([("IfcDerivedUnit", "IfcDerivedUnit", ""), ("IfcMonetaryUnit", "IfcMonetaryUnit", "")])
        return results

    @classmethod
    def named_unit_types(cls):
        values = ifcopenshell.util.attribute.get_enum_items(
            tool.Ifc.schema().declaration_by_name("IfcNamedUnit").all_attributes()[1]
        )
        return [(c, c, "") for c in sorted(values)]

    @classmethod
    def conversion_unit_types(cls):
        return [(u, u, "") for u in ifcopenshell.util.unit.si_conversions.keys()]

    @classmethod
    def get_total_units(cls):
        ifc = tool.Ifc.get()
        return len(ifc.by_type("IfcDerivedUnit") + ifc.by_type("IfcNamedUnit") + ifc.by_type("IfcMonetaryUnit"))
