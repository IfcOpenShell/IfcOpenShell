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
import ifcopenshell.api.root
import ifcopenshell.api.constraint
import ifcopenshell.util.constraint


class TestUnassignConstraint(test.bootstrap.IFC4):
    def test_unassigning_a_constraint(self):
        constraint = ifcopenshell.api.constraint.add_objective(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.constraint.assign_constraint(self.file, products=[element, element2], constraint=constraint)
        ifcopenshell.api.constraint.unassign_constraint(self.file, products=[element, element2], constraint=constraint)
        assert ifcopenshell.util.constraint.get_constrained_elements(element) == set()
        assert len(self.file.by_type("IfcRelAssociatesConstraint")) == 0

    def test_doing_nothing_if_no_constraint(self):
        constraint = ifcopenshell.api.constraint.add_objective(self.file)
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.constraint.unassign_constraint(self.file, products=[element, element2], constraint=constraint)
        assert ifcopenshell.util.constraint.get_constrained_elements(element) == set()
        assert ifcopenshell.util.constraint.get_constrained_elements(element2) == set()

    def test_updating_the_rel_when_a_reference_is_removed_with_multipled_elements(self):
        constraint = ifcopenshell.api.constraint.add_objective(self.file)
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.constraint.assign_constraint(self.file, products=[element1], constraint=constraint)
        rel = self.file.by_type("IfcRelAssociatesConstraint")[0]

        ifcopenshell.api.constraint.assign_constraint(self.file, products=[element2, element3], constraint=constraint)
        ifcopenshell.api.constraint.unassign_constraint(self.file, products=[element1, element2], constraint=constraint)
        assert rel.RelatedObjects == (element3,)


class TestUnassignConstraintIFC2X3(test.bootstrap.IFC2X3, TestUnassignConstraint):
    pass
