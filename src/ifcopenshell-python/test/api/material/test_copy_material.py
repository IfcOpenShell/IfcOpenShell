# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.element


class TestCopyMaterial(test.bootstrap.IFC4):
    def test_copy_a_single_material(self):
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        new = ifcopenshell.api.run("material.copy_material", self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcMaterial")) == 2

    def test_assignments_are_not_copied(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material)
        new = ifcopenshell.api.run("material.copy_material", self.file, material=material)
        assert material.AssociatedTo
        assert not new.AssociatedTo

    def test_copy_a_material_with_properties(self):
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=material, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"foo": "bar"})
        new = ifcopenshell.api.run("material.copy_material", self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcMaterial")) == 2
        assert new.HasProperties[0] != material.HasProperties[0]
        assert new.HasProperties[0].Properties[0] != material.HasProperties[0].Properties[0]
        assert ifcopenshell.util.element.get_pset(new, "Foo_Bar", "foo") == "bar"

    def test_copy_a_material_with_a_style_representation(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        context = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        style = ifcopenshell.api.run("style.add_style", self.file)
        ifcopenshell.api.run("style.assign_material_style", self.file, material=material, style=style, context=context)
        new = ifcopenshell.api.run("material.copy_material", self.file, material=material)
        assert new.Name == "CON01"
        assert len(self.file.by_type("IfcMaterialDefinitionRepresentation")) == 2
        assert new.HasRepresentation[0] != material.HasRepresentation[0]
        assert new.HasRepresentation[0].Representations[0] != material.HasRepresentation[0].Representations[0]
        assert new.HasRepresentation[0].Representations[0].ContextOfItems == context
