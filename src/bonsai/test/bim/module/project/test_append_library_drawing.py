# This file was generated with the assistance of an AI coding tool.
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

import bpy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.group
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewFile


class TestAppendLibraryElement(NewFile):
    def test_appending_a_drawing_recreates_its_drawing_group(self):
        library = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        drawing = ifcopenshell.api.root.create_entity(
            library, ifc_class="IfcAnnotation", predefined_type="DRAWING", name="Plan"
        )
        ifcopenshell.api.geometry.edit_object_placement(library, product=drawing)
        group = ifcopenshell.api.group.add_group(library, name="Plan")
        ifcopenshell.api.group.edit_group(library, group=group, attributes={"ObjectType": "DRAWING"})
        ifcopenshell.api.group.assign_group(library, products=[drawing], group=group)
        IfcStore.library_file = library
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        bpy.ops.bim.append_library_element(definition=drawing.id())

        appended = ifc.by_type("IfcAnnotation")[0]
        assert tool.Drawing.get_drawing_group(appended)
        assert tool.Ifc.get_object(appended) is None

    def test_appending_an_aggregate_creates_objects_for_its_parts(self):
        library = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject")
        assembly = ifcopenshell.api.root.create_entity(library, ifc_class="IfcElementAssembly", name="Module")
        part = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWall", name="Panel")
        ifcopenshell.api.aggregate.assign_object(library, products=[part], relating_object=assembly)
        IfcStore.library_file = library
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.bim.append_library_element(definition=assembly.id())

        assert tool.Ifc.get_object(ifc.by_type("IfcWall")[0])
