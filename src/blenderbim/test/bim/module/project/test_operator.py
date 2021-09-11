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


class TestCreateProject(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_creating_a_project(self):
        return """
        When I press "bim.create_project"
        Then an IFC file exists
        And the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
        And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
        """


class TestLoadProject(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_loading_a_project(self):
        return """
        When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
        Then an IFC file exists
        And "scene.BIMProjectProperties.is_loading" is "True"
        """


class TestLoadProjectElements(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_loading_all_project_elements(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I press "bim.load_project_elements(mode='ALL')"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
        And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
        And the object "IfcSlab/Slab" is an "IfcSlab"
        And the object "IfcWall/Wall" is an "IfcWall"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
        And "scene.BIMProjectProperties.is_loading" is "False"
        """
