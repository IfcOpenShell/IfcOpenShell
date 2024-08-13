@patch
Feature: Patch

Scenario: Execute IFC Patch - file in memory
    Given an empty IFC project
    And I set "scene.BIMPatchProperties.ifc_patch_recipes" to "OffsetObjectPlacements"
    And I set "scene.BIMPatchProperties.should_load_from_memory" to "True"
    And I set "scene.BIMPatchProperties.ifc_patch_output" to "{cwd}/test/files/temp/basic-patched.ifc"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['X'].string_value" to "123454321"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Y'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Z'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Should Rotate First'].bool_value" to "True"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Ax'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Ay'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Az'].string_value" to "0"
    When I press "bim.execute_ifc_patch()"
    Then the file "{cwd}/test/files/temp/basic-patched.ifc" should contain "123454321"

Scenario: Execute IFC Patch - file from disk
    Given an empty IFC project
    And I set "scene.BIMPatchProperties.ifc_patch_recipes" to "OffsetObjectPlacements"
    And I set "scene.BIMPatchProperties.ifc_patch_input" to "{cwd}/test/files/basic.ifc"
    And I set "scene.BIMPatchProperties.ifc_patch_output" to "{cwd}/test/files/temp/basic-patched.ifc"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['X'].string_value" to "123454321"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Y'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Z'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Should Rotate First'].bool_value" to "True"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Ax'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Ay'].string_value" to "0"
    And I set "scene.BIMPatchProperties.ifc_patch_args_attr['Az'].string_value" to "0"
    When I press "bim.execute_ifc_patch()"
    Then the file "{cwd}/test/files/temp/basic-patched.ifc" should contain "123454321"

Scenario: Run migrate patch
    Given an empty Blender session
    When I press "bim.run_migrate_patch(infile='{cwd}/test/files/ifc2x3.ifc', outfile='{cwd}/test/files/temp/ifc2x3-migrated.ifc', schema='IFC4')"
    Then the file "{cwd}/test/files/temp/ifc2x3-migrated.ifc" should contain "IFC4"
