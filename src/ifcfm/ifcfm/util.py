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


def print_element(declaration):
    if declaration.name() in ifcopenshell.util.fm.fmhem_excluded_classes:
        pass
    elif declaration.is_abstract():
        pass
    else:
        types = []
        for attribute in declaration.all_attributes():
            if attribute.name() == "PredefinedType":
                types = list(ifcopenshell.util.attribute.get_enum_items(attribute))
                if "NOTDEFINED" in types:
                    types.remove("NOTDEFINED")
        print("{}".format(declaration.name()))
        if types:
            for line in textwrap.wrap(", ".join(types), width=70):
                print("\t\t{}".format(line))
    for subtype in declaration.subtypes():
        print_element(subtype)


def print_fmhem_documentation(schema="IFC4"):
    if schema == "IFC4":
        classes = ifcopenshell.util.fm.fmhem_classes_ifc4
    elif schema == "IFC2X3":
        classes = ifcopenshell.util.fm.fmhem_classes_ifc2x3
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
    for ifc_class in classes:
        try:
            declaration = schema.declaration_by_name(ifc_class)
            print_element(declaration)
        except:
            pass

print_fmhem_documentation("IFC2X3")
