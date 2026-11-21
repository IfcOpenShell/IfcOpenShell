# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bonsai Contributors
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.guid
import pytest

import ifcpatch
import test.bootstrap


class TestAssignConstituentFractionsZeroWidth(test.bootstrap.IFC4):
    def test_constituent_with_zero_width_gets_a_zero_fraction(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        constituent_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        quantities = []
        for name, width in {"Membrane": 0.0, "Insulation": 0.1, "Board": 0.2}.items():
            material = ifcopenshell.api.material.add_material(self.file, name=name)
            constituent = ifcopenshell.api.material.add_constituent(
                self.file, constituent_set=constituent_set, material=material
            )
            constituent.Name = name
            width_quantity = self.file.create_entity("IfcQuantityLength", Name="Width", LengthValue=width)
            quantities.append(
                self.file.create_entity(
                    "IfcPhysicalComplexQuantity", Name=name, Discrimination="LAYER", HasQuantities=[width_quantity]
                )
            )
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialConstituentSet", material=constituent_set
        )
        qto = self.file.create_entity(
            "IfcElementQuantity",
            GlobalId=ifcopenshell.guid.new(),
            Name="Qto_WallBaseQuantities",
            Quantities=quantities,
        )
        self.file.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[wall],
            RelatingPropertyDefinition=qto,
        )

        output = ifcpatch.execute({"file": self.file, "recipe": "AssignConstituentFractions", "arguments": []})

        fractions = {c.Name: c.Fraction for c in output.by_type("IfcMaterialConstituent")}
        assert fractions["Membrane"] == 0.0
        assert fractions["Insulation"] == pytest.approx(1 / 3)
        assert fractions["Board"] == pytest.approx(2 / 3)
