# IfcFM - IFC for facility management
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcFM.
#
# IfcFM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcFM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcFM.  If not, see <http://www.gnu.org/licenses/>.


import textwrap
import ifcopenshell
import ifcopenshell.util.fm
import ifcopenshell.util.attribute


def print_element(declaration, levels=0):
    if declaration.name() == "IfcCooledBeamType":
        return
    if declaration.is_abstract():
        print("{}{} (abstract)".format("\t\t" * levels, declaration.name()))
    else:
        types = []
        for attribute in declaration.all_attributes():
            if attribute.name() == "PredefinedType":
                types = ifcopenshell.util.attribute.get_enum_items(attribute)
        print("{}{}".format("\t\t" * levels, declaration.name()))
        if types:
            for line in textwrap.wrap(", ".join(types), width=60):
                print("{}{}".format("\t\t" * (levels + 1), line))
    for subtype in declaration.subtypes():
        print_element(subtype, levels=levels + 1)


def print_fmhem_documentation(schema="IFC4"):
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
    for ifc_class in ifcopenshell.util.fm.fmhem_classes:
        try:
            declaration = schema.declaration_by_name(ifc_class)
            print_element(declaration)
        except:
            pass
