# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import numpy
import test.bootstrap
import ifcopenshell.api.feature
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.util.placement


class TestAddFeature(test.bootstrap.IFC4X3):
    def test_adding_a_surface_feature(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        feature = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSurfaceFeature")
        ifcopenshell.api.feature.add_feature(self.file, feature=feature, element=wall)
        assert wall.HasSurfaceFeatures[0].RelatedSurfaceFeatures == (feature,)


class TestAddFeature(test.bootstrap.IFC4):
    def test_adding_an_opening(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening

    def test_adding_a_projection(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        projection = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectionElement")
        ifcopenshell.api.feature.add_feature(self.file, feature=projection, element=wall)
        assert wall.HasProjections[0].RelatedFeatureElement == projection

    def test_adding_a_surface_feature(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        feature = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSurfaceFeature")
        ifcopenshell.api.feature.add_feature(self.file, feature=feature, element=wall)
        assert wall.IsDecomposedBy[0].RelatedObjects == (feature,)

    def test_adding_an_opening_twice(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening
        assert len(wall.HasOpenings) == 1

    def test_adding_an_opening_which_is_already_voiding_another_element(self):
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=slab)
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        assert not slab.HasOpenings
        assert wall.HasOpenings[0].RelatedOpeningElement == opening

    def test_assigning_an_opening_does_not_shift_object_placements(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        matrix1 = numpy.array(
            (
                (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0),
                (0.0, 0.0, 1.0, 1.0),
                (0.0, 0.0, 0.0, 1.0),
            )
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix1.copy(), is_si=False)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=opening, matrix=matrix1.copy(), is_si=False)
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        assert opening.ObjectPlacement.PlacementRelTo.PlacesObject[0] == wall
        assert numpy.array_equal(ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement), matrix1)

    def test_not_updating_placement_if_placement_is_not_relative(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        placement = self.file.createIfcGridPlacement()
        opening.ObjectPlacement = placement
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=wall)
        assert opening.ObjectPlacement == placement


class TestAddFeatureIFC2X3(test.bootstrap.IFC2X3, TestAddFeature):
    def test_adding_a_surface_feature(self):
        pass
