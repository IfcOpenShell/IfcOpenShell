# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.util.element
import ifcopenshell.util.shape_builder
import test.bootstrap


class TestSetShapeAspectConstituents(test.bootstrap.IFC4):
    def setup_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        item = builder.sphere()
        rep = builder.get_representation(body, [item])
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)
        return element, body

    def test_reuses_existing_constituent_set_when_names_match(self):
        element, body = self.setup_element()
        aluminium = ifcopenshell.api.material.add_material(self.file, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(self.file, name="GLZ01", category="glass")
        materials = {"Framing": aluminium, "Glazing": glass}

        ifcopenshell.api.material.set_shape_aspect_constituents(
            self.file, element=element, context=body, materials=materials
        )
        material_set = ifcopenshell.util.element.get_material(element)
        assert material_set.is_a("IfcMaterialConstituentSet")
        constituents = {c.Name: c for c in material_set.MaterialConstituents}

        # Simulate the user (or another API call) customising a constituent,
        # e.g. setting a quantity fraction, after the set was first created.
        constituents["Framing"].Fraction = 0.42

        # Calling the function again with the exact same materials must reuse
        # the existing constituent set rather than tearing it down and
        # rebuilding it, otherwise any such customisation is silently lost.
        ifcopenshell.api.material.set_shape_aspect_constituents(
            self.file, element=element, context=body, materials=materials
        )

        material_set_again = ifcopenshell.util.element.get_material(element)
        assert material_set_again == material_set
        constituents_again = {c.Name: c for c in material_set_again.MaterialConstituents}
        assert constituents_again["Framing"] == constituents["Framing"]
        assert constituents_again["Framing"].Fraction == 0.42

    def test_recreates_constituent_set_when_names_differ(self):
        element, body = self.setup_element()
        aluminium = ifcopenshell.api.material.add_material(self.file, name="AL01", category="aluminium")
        glass = ifcopenshell.api.material.add_material(self.file, name="GLZ01", category="glass")

        ifcopenshell.api.material.set_shape_aspect_constituents(
            self.file, element=element, context=body, materials={"Framing": aluminium}
        )
        material_set = ifcopenshell.util.element.get_material(element)
        old_framing = next(c for c in material_set.MaterialConstituents if c.Name == "Framing")
        # Tag the original constituent so we can tell, regardless of any STEP
        # id recycling, whether it is the same instance after the next call.
        old_framing.Description = "ORIGINAL_TAG"

        ifcopenshell.api.material.set_shape_aspect_constituents(
            self.file, element=element, context=body, materials={"Framing": aluminium, "Glazing": glass}
        )
        material_set_again = ifcopenshell.util.element.get_material(element)
        assert {c.Name for c in material_set_again.MaterialConstituents} == {"Framing", "Glazing"}
        # The names differ from the original set, so it must have been torn
        # down and rebuilt: the tagged constituent must not survive.
        assert all(c.Description != "ORIGINAL_TAG" for c in material_set_again.MaterialConstituents)
