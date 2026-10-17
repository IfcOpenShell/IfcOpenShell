# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.util.element

import bonsai.tool as tool
from bonsai.tool.drawing import Drawing as subject
from test.bim.bootstrap import NewFile


class TestElementClasses(NewFile):
    def test_no_classes_by_default(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")
        assert subject.get_element_classes(element) == []

    def test_add_and_remove_classes(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSlab")

        subject.add_element_class(element, "dashed")
        subject.add_element_class(element, "fill-grey")
        assert subject.get_element_classes(element) == ["dashed", "fill-grey"]
        assert ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes") == "dashed fill-grey"

        subject.add_element_class(element, "dashed")
        assert subject.get_element_classes(element) == ["dashed", "fill-grey"]

        subject.remove_element_class(element, "dashed")
        assert subject.get_element_classes(element) == ["fill-grey"]

        subject.remove_element_class(element, "dashed")
        assert subject.get_element_classes(element) == ["fill-grey"]

    def test_classes_are_sanitised(self):
        assert subject.sanitise_class_name("  fill grey  ") == "fill-grey"
        assert subject.sanitise_class_name("fill-grey") == "fill-grey"
        assert subject.sanitise_class_name("Wall_1") == "Wall_1"
        assert subject.sanitise_class_name("2thick") == "thick"
        assert subject.sanitise_class_name("!!!") == ""

    def test_preserves_existing_annotation_pset(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation")
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Classes": "small", "Symbol": "dot"})
        subject.add_element_class(element, "dashed")
        assert subject.get_element_classes(element) == ["small", "dashed"]
        assert ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Symbol") == "dot"
