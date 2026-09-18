# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.feature
import ifcopenshell.api.pset
import ifcopenshell.api.root

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestGetElementStatus(NewFile):
    def test_common_pset(self):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}

    def test_epset(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "EPset_Status")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}


class TestAssignStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.assign_status(status="NEW")
        assert subject.get_element_status(element) == {"NEW"}

        bpy.ops.bim.assign_status(status="EXISTING")
        assert subject.get_element_status(element) == {"EXISTING"}

        bpy.ops.bim.assign_status(status="EXISTING", should_unassign_status=True)
        assert subject.get_element_status(element) == set()


class TestApplyVisibilityToVoids(NewFile):
    def create_wall_with_opening(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        wall = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        opening = ifcopenshell.api.root.create_entity(ifc, "IfcOpeningElement")
        opening.Representation = ifc.createIfcProductDefinitionShape()
        ifcopenshell.api.feature.add_feature(ifc, feature=opening, element=wall)
        return wall, opening

    def test_hiding_a_voiding_opening_nulls_its_representation_and_restores_it(self):
        wall, opening = self.create_wall_with_opening()
        rep = opening.Representation
        subject.apply_visibility_to_voids(set())
        assert opening.Representation is None
        subject.apply_visibility_to_voids({wall, opening})
        assert opening.Representation == rep

    def test_openings_that_void_nothing_are_untouched(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        opening = ifcopenshell.api.root.create_entity(ifc, "IfcOpeningElement")
        rep = ifc.createIfcProductDefinitionShape()
        opening.Representation = rep
        subject.apply_visibility_to_voids(set())
        assert opening.Representation == rep

    def test_already_hidden_openings_are_not_restashed(self):
        wall, opening = self.create_wall_with_opening()
        rep = opening.Representation
        subject.apply_visibility_to_voids(set())
        subject.apply_visibility_to_voids(set())
        subject.apply_visibility_to_voids({wall, opening})
        assert opening.Representation == rep


class TestOpeningRepresentationsRestored(NewFile):
    def test_representations_are_restored_during_the_context_and_renulled_after(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        wall = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        opening = ifcopenshell.api.root.create_entity(ifc, "IfcOpeningElement")
        rep = ifc.createIfcProductDefinitionShape()
        opening.Representation = rep
        ifcopenshell.api.feature.add_feature(ifc, feature=opening, element=wall)

        subject.apply_visibility_to_voids(set())
        assert opening.Representation is None
        with subject.opening_representations_restored():
            assert opening.Representation == rep
        assert opening.Representation is None

        subject.apply_visibility_to_voids({wall, opening})
        assert opening.Representation == rep

    def test_no_stashed_representations_is_a_noop(self):
        bpy.ops.bim.create_project()
        with subject.opening_representations_restored():
            pass
