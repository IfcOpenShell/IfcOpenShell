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
#
# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.guid

import ifcpatch
import test.bootstrap


class TestAssignConstituentFractions(test.bootstrap.IFC4):
    def test_run_assigns_fractions_from_layer_widths(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        constituent_set = ifcopenshell.api.material.add_material_set(
            self.file, name="Wall Materials", set_type="IfcMaterialConstituentSet"
        )
        material_a = ifcopenshell.api.material.add_material(self.file, name="Brick")
        material_b = ifcopenshell.api.material.add_material(self.file, name="Insulation")
        constituent_a = ifcopenshell.api.material.add_constituent(self.file, constituent_set, material_a, name="Layer1")
        constituent_b = ifcopenshell.api.material.add_constituent(self.file, constituent_set, material_b, name="Layer2")
        ifcopenshell.api.material.assign_material(
            self.file, products=[element], type="IfcMaterialConstituentSet", material=constituent_set
        )

        complex_quantities = [
            self.file.create_entity(
                "IfcPhysicalComplexQuantity",
                Name="Layer1",
                Discrimination="layer",
                HasQuantities=[self.file.create_entity("IfcQuantityLength", Name="Width", LengthValue=0.1)],
            ),
            self.file.create_entity(
                "IfcPhysicalComplexQuantity",
                Name="Layer2",
                Discrimination="layer",
                HasQuantities=[self.file.create_entity("IfcQuantityLength", Name="Width", LengthValue=0.2)],
            ),
        ]
        qto = self.file.create_entity(
            "IfcElementQuantity",
            GlobalId=ifcopenshell.guid.new(),
            Name="Qto_WallBaseQuantities",
            Quantities=complex_quantities,
        )
        self.file.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=qto,
        )

        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "AssignConstituentFractions", "arguments": []}
        )

        assert constituent_a.Fraction == pytest.approx(1 / 3, rel=1e-6)
        assert constituent_b.Fraction == pytest.approx(2 / 3, rel=1e-6)


class TestAssignConstituentFractionsIFC2X3(test.bootstrap.IFC2X3):
    def test_run_is_a_no_op_since_constituent_sets_do_not_exist_in_ifc2x3(self):
        """IfcMaterialConstituentSet is an IFC4 concept absent from IFC2X3.
        Running this recipe against an IFC2X3 file must not raise, even
        though the schema has no equivalent to convert."""
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "AssignConstituentFractions", "arguments": []}
        )

        assert element.Name is None
