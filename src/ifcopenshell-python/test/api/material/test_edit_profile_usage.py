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

import test.bootstrap
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.util.placement
from ifcopenshell.util.shape_builder import ShapeBuilder


# IfcMaterialProfileSetUsage added in IFC4.
class TestEditProfileUsageIFC4(test.bootstrap.IFC4):
    def test_update_cardinal_point(self):
        model = self.file
        builder = ShapeBuilder(model)

        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )

        material_set = ifcopenshell.api.material.add_material_set(model, name="B1", set_type="IfcMaterialProfileSet")
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")
        rectangle = builder.rectangle((100, 100))
        profile = builder.profile(rectangle)
        ifcopenshell.api.material.add_profile(model, profile_set=material_set, material=steel, profile=profile)
        beam = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBeam", name="B1.01")
        rel = ifcopenshell.api.material.assign_material(
            model, material=material_set, products=[beam], type="IfcMaterialProfileSetUsage"
        )
        assert isinstance(rel, ifcopenshell.entity_instance)
        usage = rel.RelatingMaterial
        assert usage.CardinalPoint is None

        representation = ifcopenshell.api.geometry.add_profile_representation(
            model,
            context=body,
            profile=profile,
            depth=1000,
            cardinal_point=5,
        )
        assert representation.Items[0].Position.Location.Coordinates == (0.0, 0.0, 0.0)
        ifcopenshell.api.geometry.assign_representation(model, product=beam, representation=representation)
        ifcopenshell.api.material.edit_profile_usage(model, usage=rel.RelatingMaterial, attributes={"CardinalPoint": 1})
        assert representation.Items[0].Position.Location.Coordinates == (-50.0, 50.0, 0.0)


class TestEditProfileUsageIFC4X3(test.bootstrap.IFC4X3, TestEditProfileUsageIFC4):
    pass
