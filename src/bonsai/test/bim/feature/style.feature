@style
Feature: Style


Scenario: Unlink style
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.assign_style_to_selected(style_id={style})"
    When I press "bim.unlink_style(blender_material='Style')"
    Then the material "Style" is not an IFC style

Scenario: Add a new style
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I set "scene.BIMStylesProperties.surface_colour" to "[1.0,0.0,0.0]"
    When I press "bim.add_presentation_style"
    Then the material "Style" colour is "1,0,0,1"
    And the material "Style" is an IFC style

Scenario: Disable adding a new style
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    When I press "bim.disable_adding_presentation_style"
    Then nothing happens

Scenario: Remove style
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I set "scene.BIMStylesProperties.surface_colour" to "[1.0,0.0,0.0]"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    When I press "bim.remove_style(style={style})"
    Then the material "Style" does not exist

Scenario: Edit style
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.enable_editing_style(style={style})"
    And I set "scene.BIMStylesProperties.attributes[0].string_value" to "NewStyle"
    When I press "bim.edit_style"
    Then the material "Style" does not exist
    And the material "NewStyle" exists

Scenario: Disable editing style
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.enable_editing_style(style={style})"
    And I set "scene.BIMStylesProperties.attributes[0].string_value" to "NewStyle"
    When I press "bim.disable_editing_style"
    Then the material "NewStyle" does not exist
    And the material "Style" exists

Scenario: Load styles
    Given an empty IFC project
    When I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    Then nothing happens

Scenario: Disable editing styles
    Given an empty IFC project
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    When I press "bim.disable_editing_styles"
    Then nothing happens

Scenario: Assign style to selected
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    When I press "bim.assign_style_to_selected(style_id={style})"
    Then the object "IfcWall/Cube" has the material "Style"

Scenario: Select by style
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.assign_style_to_selected(style_id={style})"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    When I deselect all objects
    And I press "bim.select_by_style(style={style})"
    Then the object "IfcWall/Cube" is selected
