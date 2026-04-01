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

import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.representation
import test.bootstrap


class TestCopyRepresentation(test.bootstrap.IFC4):
    def _body_context(self):
        body = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        if body is None:
            model = self.file.createIfcGeometricRepresentationContext(
                ContextType="Model",
                CoordinateSpaceDimension=3,
                Precision=1e-5,
                WorldCoordinateSystem=self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
                ),
            )
            body = self.file.createIfcGeometricRepresentationSubContext(
                ContextIdentifier="Body",
                ContextType="Model",
                TargetView="MODEL_VIEW",
                ParentContext=model,
            )
        return body

    def _add_body_rep(self, element):
        body = self._body_context()
        rep = ifcopenshell.api.geometry.add_wall_representation(
            self.file, context=body, length=5.0, height=3.0, thickness=0.2
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)
        return rep

    def test_copy_to_empty_target(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        self._add_body_rep(wall_a)

        result = ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        assert result is not None
        assert result.is_a("IfcShapeRepresentation")
        target_rep = ifcopenshell.util.representation.get_representation(wall_b, "Model", "Body")
        assert target_rep is not None
        assert target_rep == result

    def test_source_rep_entities_are_distinct(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        source_rep = self._add_body_rep(wall_a)

        new_rep = ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        assert new_rep.id() != source_rep.id()
        assert new_rep.Items[0].id() != source_rep.Items[0].id()

    def test_context_is_shared_not_copied(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        source_rep = self._add_body_rep(wall_a)

        new_rep = ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        assert new_rep.ContextOfItems.id() == source_rep.ContextOfItems.id()

    def test_replaces_existing_target_rep(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        self._add_body_rep(wall_a)
        old_rep = self._add_body_rep(wall_b)
        old_rep_id = old_rep.id()

        ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        try:
            self.file.by_id(old_rep_id)
            assert False, "old representation still exists"
        except RuntimeError:
            pass  # entity was removed, as expected

    def test_source_unchanged_after_copy(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        source_rep = self._add_body_rep(wall_a)
        source_rep_id = source_rep.id()

        ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        assert self.file.by_id(source_rep_id) is not None  # source must still exist
        assert ifcopenshell.util.representation.get_representation(wall_a, "Model", "Body") is not None

    def test_returns_none_when_no_matching_rep(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        result = ifcopenshell.api.geometry.copy_representation(self.file, source=wall_a, target=wall_b)

        assert result is None

    def test_custom_context_identifier(self):
        wall_a = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall_b = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        self._add_body_rep(wall_a)

        # "Axis" doesn't exist on wall_a, so should return None
        result = ifcopenshell.api.geometry.copy_representation(
            self.file, source=wall_a, target=wall_b, context_identifier="Axis"
        )

        assert result is None


class TestCopyRepresentationIFC2X3(test.bootstrap.IFC2X3, TestCopyRepresentation):
    pass
