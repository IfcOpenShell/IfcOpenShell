# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import test.bim.bootstrap


class TestAddSubcontext(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_adding_a_subcontext(self):
        return """
        Given an empty IFC project
        When I press "bim.add_subcontext(context='Model')"
        Then nothing interesting happens
        """


class TestRemoveSubcontext(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_removing_a_subcontext(self):
        return """
        Given an empty IFC project
        And the variable "context_id" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
        When I press "bim.remove_subcontext(ifc_definition_id={context_id})"
        Then nothing interesting happens
        """
