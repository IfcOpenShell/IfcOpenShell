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
import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.shape as subject
import test.bootstrap


def create_wall_in_millimetre_file(file: ifcopenshell.file) -> ifcopenshell.entity_instance:
    ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
    unit = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.unit.assign_unit(file, units=[unit])
    model = ifcopenshell.api.context.add_context(file, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    wall = ifcopenshell.api.root.create_entity(file, ifc_class="IfcWall")
    matrix = np.eye(4)
    matrix[:3, 3] = (1.0, 2.0, 3.0)
    ifcopenshell.api.geometry.edit_object_placement(file, product=wall, matrix=matrix, is_si=True)
    representation = ifcopenshell.api.geometry.add_wall_representation(
        file, context=body, length=1.0, height=3.0, thickness=0.2
    )
    ifcopenshell.api.geometry.assign_representation(file, product=wall, representation=representation)
    return wall


def create_file_unit_shape(wall: ifcopenshell.entity_instance):
    settings = ifcopenshell.geom.settings()
    settings.set("convert-back-units", True)
    return ifcopenshell.geom.create_shape(settings, wall)


class TestGetElementVerticesIFC4(test.bootstrap.IFC4):
    def test_matching_the_shape_vertices_for_si_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
        assert np.allclose(
            subject.get_element_vertices(wall, shape.geometry), subject.get_shape_vertices(shape, shape.geometry)
        )

    def test_matching_the_shape_vertices_for_file_unit_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = create_file_unit_shape(wall)
        assert np.allclose(
            subject.get_element_vertices(wall, shape.geometry, is_si=False),
            subject.get_shape_vertices(shape, shape.geometry),
        )


class TestGetElementBboxCentroidIFC4(test.bootstrap.IFC4):
    def test_matching_the_shape_centroid_for_si_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
        assert np.allclose(
            subject.get_element_bbox_centroid(wall, shape.geometry),
            subject.get_shape_bbox_centroid(shape, shape.geometry),
        )

    def test_matching_the_shape_centroid_for_file_unit_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = create_file_unit_shape(wall)
        assert np.allclose(
            subject.get_element_bbox_centroid(wall, shape.geometry, is_si=False),
            subject.get_shape_bbox_centroid(shape, shape.geometry),
        )


class TestGetElementBottomElevationIFC4(test.bootstrap.IFC4):
    def test_returning_metres_for_si_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
        assert subject.get_element_bottom_elevation(wall, shape.geometry) == pytest.approx(3.0)

    def test_returning_file_units_for_file_unit_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = create_file_unit_shape(wall)
        assert subject.get_element_bottom_elevation(wall, shape.geometry, is_si=False) == pytest.approx(3000.0)


class TestGetElementTopElevationIFC4(test.bootstrap.IFC4):
    def test_returning_metres_for_si_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), wall)
        assert subject.get_element_top_elevation(wall, shape.geometry) == pytest.approx(6.0)

    def test_returning_file_units_for_file_unit_geometry(self):
        wall = create_wall_in_millimetre_file(self.file)
        shape = create_file_unit_shape(wall)
        assert subject.get_element_top_elevation(wall, shape.geometry, is_si=False) == pytest.approx(6000.0)
