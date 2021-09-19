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


class TestExecuteIfcPatch(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_executing_ifcpatch(self):
        return """
        Given I set "scene.BIMPatchProperties.ifc_patch_recipes" to "OffsetObjectPlacements"
        And I set "scene.BIMPatchProperties.ifc_patch_input" to "{cwd}/test/files/basic.ifc"
        And I set "scene.BIMPatchProperties.ifc_patch_output" to "{cwd}/test/files/basic-patched.ifc"
        And I set "scene.BIMPatchProperties.ifc_patch_args" to "[123454321,0,0,0]"
        When I press "bim.execute_ifc_patch"
        Then the file "{cwd}/test/files/basic-patched.ifc" should contain "123454321"
        """
