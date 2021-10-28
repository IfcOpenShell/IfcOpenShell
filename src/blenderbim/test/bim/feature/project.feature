@project
Feature: Project

Scenario: Create project
    Given an empty Blender session
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

Scenario: Append library element
    Given an empty IFC project
    When I press "bim.select_library_file(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.change_library_element(element_name='IfcTypeProduct')"
    And I press "bim.change_library_element(element_name='IfcSlabType')"
    And I press "bim.append_library_element(definition=242, prop_index=0)"
    Then the object "IfcSlabType/Slab" is an "IfcSlabType"
    And the object "IfcSlabType/Slab" is in the collection "Types"

Scenario: Append library element - append two elements sharing a material
    Given an empty IFC project
    And I press "bim.select_library_file(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.change_library_element(element_name='IfcTypeProduct')"
    And I press "bim.change_library_element(element_name='IfcSlabType')"
    And I press "bim.append_library_element(definition=242, prop_index=0)"
    When I press "bim.rewind_library"
    And I press "bim.change_library_element(element_name='IfcWallType')"
    And I press "bim.append_library_element(definition=291, prop_index=0)"
    Then the object "IfcSlabType/Slab" is an "IfcSlabType"
    And the object "IfcSlabType/Slab" is in the collection "Types"
    And the object "IfcWallType/Wall" is an "IfcWallType"
    And the object "IfcWallType/Wall" is in the collection "Types"
    And the object "IfcSlabType/Slab" has the material "SurfaceStyle"
    And the object "IfcWallType/Wall" has the material "SurfaceStyle"

Scenario: Load project
    Given an empty Blender session
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

Scenario: Load project - advanced mode
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    Then an IFC file exists
    And "scene.BIMProjectProperties.is_loading" is "True"
    And the object "IfcProject/My Project" does not exist

Scenario: Load project elements - load all project elements
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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
    And the object "IfcSlab/Slab" has data which is an IFC representation
    And the object "IfcBeam/Beam" has data which is an IFC representation
    And the object "IfcWall/Wall" has data which is an IFC representation
    And the object "IfcSlabType/Slab" has data which is an IFC representation
    And the object "IfcWallType/Wall" has data which is an IFC representation
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Load project elements - load objects filtered by decomposition
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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

Scenario: Load project elements - load objects filtered by IFC class
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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

Scenario: Load project elements - load objects filtered by whitelist
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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

Scenario: Load project elements - load objects filtered by blacklist
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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

Scenario: Load project elements - load no objects due to filter
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
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

Scenario: Load project elements - load with the decomposition collection mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/decomposition.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.collection_mode" to "DECOMPOSITION"
    And I set "scene.BIMProjectProperties.filter_mode" to "NONE"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcSpace/Space" is an "IfcSpace"
    And the object "IfcElementAssembly/Assembly" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcSpace/Space" is in the collection "IfcSpace/Space"
    And the object "IfcElementAssembly/Assembly" is in the collection "IfcElementAssembly/Assembly"
    And the object "IfcBeam/Beam" is in the collection "IfcElementAssembly/Assembly"
    And the collection "IfcSite/My Site" is in the collection "IfcProject/My Project"
    And the collection "IfcBuilding/My Building" is in the collection "IfcSite/My Site"
    And the collection "IfcBuildingStorey/My Storey" is in the collection "IfcBuilding/My Building"
    And the collection "IfcSpace/Space" is in the collection "IfcBuildingStorey/My Storey"
    And the collection "IfcElementAssembly/Assembly" is in the collection "IfcSpace/Space"
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Load project elements - load with the spatial decomposition collection mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/decomposition.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.collection_mode" to "SPATIAL_DECOMPOSITION"
    And I set "scene.BIMProjectProperties.filter_mode" to "NONE"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcSpace/Space" is an "IfcSpace"
    And the object "IfcElementAssembly/Assembly" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcSpace/Space" is in the collection "IfcSpace/Space"
    And the object "IfcElementAssembly/Assembly" is in the collection "IfcSpace/Space"
    And the object "IfcBeam/Beam" is in the collection "IfcSpace/Space"
    And the collection "IfcSite/My Site" is in the collection "IfcProject/My Project"
    And the collection "IfcBuilding/My Building" is in the collection "IfcSite/My Site"
    And the collection "IfcBuildingStorey/My Storey" is in the collection "IfcBuilding/My Building"
    And the collection "IfcSpace/Space" is in the collection "IfcBuildingStorey/My Storey"
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Load project elements - manual offset of object placements
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/manual-geolocation.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.should_offset_model" to "True"
    And I set "scene.BIMProjectProperties.model_offset_coordinates" to "-268388.5, -5774506.0, -21.899999618530273"
    And I press "bim.load_project_elements"
    Then the object "IfcPlate/1780 x 270 PRECAST WALL" is at "0,0,0"

Scenario: Load project elements - auto offset of object placements
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/auto-geolocation.ifc')"
    Then the object "IfcPlate/1780 x 270 PRECAST WALL" is at "0,0,0"

Scenario: Unload project
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    And I press "bim.unload_project"
    Then an IFC file does not exist
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Link IFC
    Given an empty IFC project
    When I press "bim.link_ifc(filepath='{cwd}/test/files/basic.blend')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.blend'].is_loaded" is "True"
    And the object "IfcWall/Wall" exists
    And the object "IfcSlab/Slab" exists
    And the object "IfcElementAssembly/Empty" exists
    And the object "IfcBeam/Beam" exists
    And the object "IfcBuildingStorey/Ground Floor" exists
    And the object "IfcBuildingStorey/Level 1" exists

Scenario: Unload link
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.blend')"
    When I press "bim.unload_link(filepath='{cwd}/test/files/basic.blend')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.blend'].is_loaded" is "False"
    And "scene.collection.children.get('IfcProject/My Project')" is "None"

Scenario: Load link
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.blend')"
    And I press "bim.unload_link(filepath='{cwd}/test/files/basic.blend')"
    When I press "bim.load_link(filepath='{cwd}/test/files/basic.blend')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.blend'].is_loaded" is "True"
    And "scene.collection.children['IfcProject/My Project'].users" is "2"

Scenario: Unlink IFC
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.blend')"
    And I press "bim.unload_link(filepath='{cwd}/test/files/basic.blend')"
    When I press "bim.unlink_ifc(filepath='{cwd}/test/files/basic.blend')"
    Then "scene.BIMProjectProperties.links.get('{cwd}/test/files/basic.blend')" is "None"
    And "scene.collection.children.get('IfcProject/My Project')" is "None"

Scenario: Export IFC - blank project
    Given an empty IFC project
    When I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    Then nothing happens

Scenario: Export IFC - with basic contents
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    Then nothing happens

Scenario: Export IFC - with moved object location synchronised
    Given an empty IFC project
    When the object "IfcBuildingStorey/My Storey" is moved to "0,0,1"
    And I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    And an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/export.ifc')"
    Then the object "IfcBuildingStorey/My Storey" is at "0,0,1"

Scenario: Export IFC - with moved grid axis location synchronised
    Given an empty IFC project
    And I press "mesh.add_grid"
    When the object "IfcGridAxis/01" is moved to "1,0,0"
    And I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    And an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/export.ifc')"
    Then the object "IfcGridAxis/01" bottom left corner is at "1,-2,0"
