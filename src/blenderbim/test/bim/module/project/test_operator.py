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
        And the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
        And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
        And the object "IfcSlab/Slab" is an "IfcSlab"
        And the object "IfcWall/Wall" is an "IfcWall"
        And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
        And the object "IfcBeam/Beam" is an "IfcBeam"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcElementAssembly/Empty" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBeam/Beam" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
        And "scene.BIMProjectProperties.is_loading" is "False"
        """

    @test.bim.bootstrap.scenario
    def test_loading_a_project_in_advanced_mode(self):
        return """
        When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        Then an IFC file exists
        And "scene.BIMProjectProperties.is_loading" is "True"
        And the object "IfcProject/My Project" does not exist
        """


class TestLoadProjectElements(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_loading_all_project_elements(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "NONE"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
        And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
        And the object "IfcSlab/Slab" is an "IfcSlab"
        And the object "IfcWall/Wall" is an "IfcWall"
        And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
        And the object "IfcBeam/Beam" is an "IfcBeam"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcElementAssembly/Empty" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBeam/Beam" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
        And "scene.BIMProjectProperties.is_loading" is "False"
        """

    @test.bim.bootstrap.scenario
    def test_loading_objects_filtered_by_decomposition(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "DECOMPOSITION"
        Then "scene.BIMProjectProperties.filter_categories['IfcSite/My Site'].total_elements" is "0"
        Then "scene.BIMProjectProperties.filter_categories['IfcBuilding/My Building'].total_elements" is "0"
        Then "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Ground Floor'].total_elements" is "1"
        Then "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Level 1'].total_elements" is "2"
        When I set "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Level 1'].is_selected" to "True"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
        And the object "IfcWall/Wall" is an "IfcWall"
        And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
        And the object "IfcBeam/Beam" is an "IfcBeam"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcElementAssembly/Empty" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBeam/Beam" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBuildingStorey/Ground Floor" does not exist
        And the object "IfcSlab/Slab" does not exist
        """

    @test.bim.bootstrap.scenario
    def test_loading_objects_filtered_by_ifc_class(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "IFC_CLASS"
        Then "scene.BIMProjectProperties.filter_categories['IfcWall'].total_elements" is "1"
        And "scene.BIMProjectProperties.filter_categories['IfcSlab'].total_elements" is "1"
        And "scene.BIMProjectProperties.filter_categories['IfcElementAssembly'].total_elements" is "1"
        And "scene.BIMProjectProperties.filter_categories['IfcBeam'].total_elements" is "1"
        When I set "scene.BIMProjectProperties.filter_categories['IfcSlab'].is_selected" to "True"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
        And the object "IfcSlab/Slab" is an "IfcSlab"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcBuildingStorey/Level 1" does not exist
        And the object "IfcWall/Wall" does not exist
        """

    @test.bim.bootstrap.scenario
    def test_loading_objects_filtered_by_whitelist(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "WHITELIST"
        And I set "scene.BIMProjectProperties.filter_query" to ".IfcSlab"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
        And the object "IfcSlab/Slab" is an "IfcSlab"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
        And the object "IfcBuildingStorey/Level 1" does not exist
        And the object "IfcWall/Wall" does not exist
        """

    @test.bim.bootstrap.scenario
    def test_loading_objects_filtered_by_blacklist(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "BLACKLIST"
        And I set "scene.BIMProjectProperties.filter_query" to ".IfcSlab"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" is an "IfcSite"
        And the object "IfcBuilding/My Building" is an "IfcBuilding"
        And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
        And the object "IfcWall/Wall" is an "IfcWall"
        And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
        And the object "IfcBeam/Beam" is an "IfcBeam"
        And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
        And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
        And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
        And the object "IfcElementAssembly/Empty" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBeam/Beam" is in the collection "IfcElementAssembly/Empty"
        And the object "IfcBuildingStorey/Ground Floor" does not exist
        And the object "IfcSlab/Slab" does not exist
        """

    @test.bim.bootstrap.scenario
    def test_loading_no_objects_due_to_filter(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
        And I set "scene.BIMProjectProperties.filter_mode" to "IFC_CLASS"
        And I press "bim.load_project_elements"
        Then the object "IfcProject/My Project" is an "IfcProject"
        And the object "IfcSite/My Site" does not exist
        And the object "IfcBuilding/My Building" does not exist
        And the object "IfcBuildingStorey/Ground Floor" does not exist
        And the object "IfcBuildingStorey/Level 1" does not exist
        And the object "IfcSlab/Slab" does not exist
        And the object "IfcWall/Wall" does not exist
        """

    @test.bim.bootstrap.scenario
    def test_manual_offset_of_object_placements(self):
        return """
        Given I press "bim.load_project(filepath='{cwd}/test/files/manual-geolocation.ifc', is_advanced=True)"
        When I set "scene.BIMProjectProperties.should_offset_model" to "True"
        And I set "scene.BIMProjectProperties.model_offset_coordinates" to "-268388.5, -5774506.0, -21.899999618530273"
        And I press "bim.load_project_elements"
        Then the object "IfcPlate/1780 x 270 PRECAST WALL" is at "0,0,0"
        """


class TestUnloadProject(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_unloading_a_project(self):
        return """
        When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
        And I press "bim.unload_project"
        Then an IFC file does not exist
        And "scene.BIMProjectProperties.is_loading" is "False"
        """


class TestLinkIFC(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_linking_an_ifc(self):
        return """
        Given I press "bim.create_project"
        When I press "bim.link_ifc(filepath='{cwd}/test/files/basic.blend')"
        Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.blend'].is_loaded" is "True"
        And the object "IfcWall/Wall" exists
        And the object "IfcSlab/Slab" exists
        And the object "IfcElementAssembly/Empty" exists
        And the object "IfcBeam/Beam" exists
        And the object "IfcBuildingStorey/Ground Floor" exists
        And the object "IfcBuildingStorey/Level 1" exists
        """
