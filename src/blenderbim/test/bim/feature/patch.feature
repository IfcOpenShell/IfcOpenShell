@patch
Feature: Patch

Scenario: Execute IFC Patch 
    Given an empty IFC project
    And I set "scene.BIMPatchProperties.ifc_patch_recipes" to "OffsetObjectPlacements"
    And I set "scene.BIMPatchProperties.ifc_patch_input" to "{cwd}/test/files/basic.ifc"
    And I set "scene.BIMPatchProperties.ifc_patch_output" to "{cwd}/test/files/basic-patched.ifc"
    And I set "scene.BIMPatchProperties.ifc_patch_args" to "[123454321,0,0,0]"
    When I press "bim.execute_ifc_patch"
    Then the file "{cwd}/test/files/basic-patched.ifc" should contain "123454321"
