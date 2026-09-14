# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

# remove_resource tests is partially covered by test_add_resource_quantity.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.resource
import ifcopenshell.api.root
import ifcopenshell.validate
import test.bootstrap


class TestRemoveResource(test.bootstrap.IFC4):
    def test_removing_the_only_resource_removes_its_declaration(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="P")
        crew = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        assert self.file.by_type("IfcRelDeclares")

        ifcopenshell.api.resource.remove_resource(self.file, resource=crew)

        # An empty RelatedDefinitions is not a valid value: the declaration
        # must be removed instead of left pointing at nothing.
        assert not self.file.by_type("IfcRelDeclares")

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(self.file, logger)
        assert not logger.statements, logger.statements

    def test_removing_one_of_several_declared_resources_keeps_the_declaration(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="P")
        crew1 = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        crew2 = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        rel = crew1.HasContext[0]

        ifcopenshell.api.resource.remove_resource(self.file, resource=crew1)

        assert self.file.by_type("IfcRelDeclares") == [rel]
        assert rel.RelatedDefinitions == (crew2,)
