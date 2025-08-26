# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import pytest
import ifcpatch
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.util.element
import ifcopenshell.util.representation
import test.bootstrap


class TestMergeDuplicateTypes(test.bootstrap.IFC4):
    def test_run(self):
        context = self.file.createIfcGeometricRepresentationContext()

        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WallType")
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall_type1, representation=rep)
        ifcopenshell.api.material.assign_material(self.file, products=[wall_type1], type="IfcMaterialLayerSet")
        ifcopenshell.api.type.assign_type(
            self.file,
            related_objects=[wall1],
            relating_type=wall_type1,
            should_map_representations=False,
        )

        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType", name="WallType")
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall_type2, representation=rep)
        ifcopenshell.api.material.assign_material(self.file, products=[wall_type2], type="IfcMaterialLayerSet")
        ifcopenshell.api.type.assign_type(
            self.file,
            related_objects=[wall2],
            relating_type=wall_type2,
            should_map_representations=False,
        )

        output = ifcpatch.execute({"file": self.file, "recipe": "MergeDuplicateTypes", "arguments": ["Name"]})

        assert len(output.by_type("IfcWall")) == 2
        wall_types = output.by_type("IfcWallType")
        assert len(wall_types) == 1
        wall_type = wall_types[0]
        assert set(ifcopenshell.util.element.get_types(wall_type)) == set(output.by_type("IfcWall"))

        # test not to remap representation
        assert ifcopenshell.util.representation.get_representation(wall1, context=context) == None
        assert ifcopenshell.util.representation.get_representation(wall2, context=context) == None

        # and not to create material usages
        assert ifcopenshell.util.element.get_material(wall1, should_inherit=False) == None
        assert ifcopenshell.util.element.get_material(wall2, should_inherit=False) == None


class TestMergeDuplicateTypesIFC2X3(test.bootstrap.IFC2X3, TestMergeDuplicateTypes):
    pass
