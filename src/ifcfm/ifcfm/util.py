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
import ifcopenshell.util.schema
import ifcopenshell.util.attribute


def print_element(declaration, should_print_subtypes=True):
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
            types = sorted(types)
            for line in textwrap.wrap(", ".join(types), width=70):
                print("\t\t{}".format(line))
    if should_print_subtypes:
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


def print_all_documentation(schema="IFC4"):
    if schema == "IFC4":
        classes = ifcopenshell.util.fm.fmhem_classes_ifc4
    elif schema == "IFC2X3":
        classes = ifcopenshell.util.fm.fmhem_classes_ifc2x3
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema)
    class_queue = [schema.declaration_by_name("IfcElementType")]
    maintainable_declarations = []
    other_declarations = []
    while class_queue:
        declaration = class_queue.pop(0)
        class_queue.extend(declaration.subtypes())
        if declaration.is_abstract():
            continue
        is_maintainable = False
        for ifc_class in classes:
            if ifcopenshell.util.schema.is_a(declaration, ifc_class):
                is_maintainable = True
                break
        if is_maintainable:
            maintainable_declarations.append(declaration)
        else:
            other_declarations.append(declaration)
    print("# Maintainable classes\n")
    for declaration in maintainable_declarations:
        print_element(declaration, should_print_subtypes=False)
    print("\n\n# Other classes\n")
    for declaration in other_declarations:
        print_element(declaration, should_print_subtypes=False)


print_all_documentation("IFC2X3")
