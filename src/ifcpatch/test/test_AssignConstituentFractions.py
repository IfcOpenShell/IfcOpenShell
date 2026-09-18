# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Louis Trümpler <louis@lt.plus>
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

import pytest

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit

import ifcpatch
import test.bootstrap


class TestAssignConstituentFractions(test.bootstrap.IFC4):
    # IfcMaterialConstituentSet is an IFC4+ concept (Reference View MVD), so
    # this recipe is only meaningful on IFC4 and is not run against IFC2X3.

    def add_layer_base_quantities(self, element, widths: dict[str, float]):
        quantities = []
        for name, width in widths.items():
            width_qty = self.file.create_entity("IfcQuantityLength", Name="Width", LengthValue=width)
            quantities.append(
                self.file.create_entity(
                    "IfcPhysicalComplexQuantity", Name=name, Discrimination="LAYER", HasQuantities=[width_qty]
                )
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
            RelatedObjects=[element],
            RelatingPropertyDefinition=qto,
        )

    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        constituent_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        concrete = ifcopenshell.api.material.add_material(self.file, name="Concrete")
        insulation = ifcopenshell.api.material.add_material(self.file, name="Insulation")
        constituent1 = ifcopenshell.api.material.add_constituent(
            self.file, constituent_set=constituent_set, material=concrete
        )
        constituent1.Name = "Concrete"
        constituent2 = ifcopenshell.api.material.add_constituent(
            self.file, constituent_set=constituent_set, material=insulation
        )
        constituent2.Name = "Insulation"
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialConstituentSet", material=constituent_set
        )
        self.add_layer_base_quantities(wall, {"Concrete": 0.1, "Insulation": 0.2})

        output = ifcpatch.execute({"file": self.file, "recipe": "AssignConstituentFractions", "arguments": []})

        constituents = {c.Name: c.Fraction for c in output.by_type("IfcMaterialConstituent")}
        assert constituents["Concrete"] == pytest.approx(1 / 3)
        assert constituents["Insulation"] == pytest.approx(2 / 3)

    def test_skips_constituent_set_without_layer_quantities_instead_of_crashing(self):
        # Regression test: a constituent set whose associated element has no
        # *BaseQuantities (or none with a "layer" discriminated complex
        # quantity) used to raise a bare AssertionError, aborting the whole
        # patch. It must be skipped instead.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        constituent_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        concrete = ifcopenshell.api.material.add_material(self.file, name="Concrete")
        constituent = ifcopenshell.api.material.add_constituent(
            self.file, constituent_set=constituent_set, material=concrete
        )
        constituent.Name = "Concrete"
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialConstituentSet", material=constituent_set
        )
        # No BaseQuantities at all on the wall.

        output = ifcpatch.execute({"file": self.file, "recipe": "AssignConstituentFractions", "arguments": []})

        assert output.by_type("IfcMaterialConstituent")[0].Fraction is None
