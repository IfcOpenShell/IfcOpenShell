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
#
# This file was generated with the assistance of an AI coding tool.

import numpy as np
import ifcopenshell.util.representation as subject
import test.bootstrap


def translation_matrix(dx: float, dy: float, dz: float) -> np.ndarray:
    m = np.eye(4)
    m[0, 3] = dx
    m[1, 3] = dy
    m[2, 3] = dz
    return m


def rotation_z_matrix(degrees: float, dx: float = 0, dy: float = 0, dz: float = 0) -> np.ndarray:
    theta = np.radians(degrees)
    m = np.eye(4)
    m[0, 0] = np.cos(theta)
    m[0, 1] = -np.sin(theta)
    m[1, 0] = np.sin(theta)
    m[1, 1] = np.cos(theta)
    m[0, 3] = dx
    m[1, 3] = dy
    m[2, 3] = dz
    return m


class TestResolveItems(test.bootstrap.IFC4):
    def add_mapped_item(self, mapped_representation, matrix: np.ndarray):
        target = self.file.createIfcCartesianTransformationOperator3D(
            Axis1=self.file.createIfcDirection(tuple(matrix[:3, 0].tolist())),
            Axis2=self.file.createIfcDirection(tuple(matrix[:3, 1].tolist())),
            LocalOrigin=self.file.createIfcCartesianPoint(tuple(matrix[:3, 3].tolist())),
            Scale=1.0,
            Axis3=self.file.createIfcDirection(tuple(matrix[:3, 2].tolist())),
        )
        source = self.file.createIfcRepresentationMap(
            MappingOrigin=self.file.createIfcAxis2Placement3D(
                Location=self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ),
            MappedRepresentation=mapped_representation,
        )
        return self.file.createIfcMappedItem(MappingSource=source, MappingTarget=target)

    def wrap(self, mapped_representation, matrix: np.ndarray):
        item = self.add_mapped_item(mapped_representation, matrix)
        return self.file.createIfcShapeRepresentation(RepresentationType="MappedRepresentation", Items=[item])

    def test_outer_translation_is_not_dropped_when_the_inner_mapped_item_is_identity(self):
        # See #3019: when the inner IfcMappedItem's own transform happens to
        # be the identity, the accumulated outer transform must still be
        # carried through, not discarded.
        innermost = self.file.createIfcShapeRepresentation(Items=[self.file.createIfcExtrudedAreaSolid()])
        inner = self.wrap(innermost, np.eye(4))
        outer_matrix = translation_matrix(10, 20, 30)
        outer = self.wrap(inner, outer_matrix)

        results = subject.resolve_items(outer)

        assert len(results) == 1
        assert np.allclose(results[0]["matrix"], outer_matrix)

    def test_inner_translation_is_kept_when_the_outer_mapped_item_is_identity(self):
        innermost = self.file.createIfcShapeRepresentation(Items=[self.file.createIfcExtrudedAreaSolid()])
        inner_matrix = translation_matrix(5, 6, 7)
        inner = self.wrap(innermost, inner_matrix)
        outer = self.wrap(inner, np.eye(4))

        results = subject.resolve_items(outer)

        assert len(results) == 1
        assert np.allclose(results[0]["matrix"], inner_matrix)

    def test_non_identity_transforms_compose_outer_after_inner(self):
        innermost = self.file.createIfcShapeRepresentation(Items=[self.file.createIfcExtrudedAreaSolid()])
        inner_matrix = translation_matrix(10, 0, 0)
        inner = self.wrap(innermost, inner_matrix)
        outer_matrix = rotation_z_matrix(90, dx=100)
        outer = self.wrap(inner, outer_matrix)

        results = subject.resolve_items(outer)

        expected = outer_matrix @ inner_matrix
        assert len(results) == 1
        assert np.allclose(results[0]["matrix"], expected)

    def test_three_levels_deep_with_an_identity_middle_item(self):
        innermost = self.file.createIfcShapeRepresentation(Items=[self.file.createIfcExtrudedAreaSolid()])
        inner_matrix = translation_matrix(1, 2, 3)
        inner = self.wrap(innermost, inner_matrix)
        middle = self.wrap(inner, np.eye(4))
        outer_matrix = translation_matrix(10, 20, 30)
        outer = self.wrap(middle, outer_matrix)

        results = subject.resolve_items(outer)

        expected = outer_matrix @ np.eye(4) @ inner_matrix
        assert len(results) == 1
        assert np.allclose(results[0]["matrix"], expected)
