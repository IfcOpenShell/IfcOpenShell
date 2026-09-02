@boolean
Feature: Boolean
    Manage boolean hierarchies and boolean results

Scenario: Ensure added booleans are marked as manual
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the variable "extrusion" is "{ifc}.by_type('IfcExtrudedAreaSolid')[0].id()"
    And the object "Item/IfcExtrudedAreaSolid/{extrusion}" exists
    And I open the "Add Item" menu
    When I click "Half Space Solid"
    And the variable "half_space" is "{ifc}.by_type('IfcHalfSpaceSolid')[0].id()"
    And the variable "boolean" is "{ifc}.by_type('IfcBooleanResult')[0].id()"
    And the object "Item/IfcHalfSpaceSolid/{half_space}" exists
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I see "BBIM_Boolean"
    And I see "[{boolean}]"

Scenario: Ensure removed booleans are unmarked as manual
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the variable "extrusion" is "{ifc}.by_type('IfcExtrudedAreaSolid')[0].id()"
    And the object "Item/IfcExtrudedAreaSolid/{extrusion}" exists
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the variable "half_space" is "{ifc}.by_type('IfcHalfSpaceSolid')[0].id()"
    And the variable "boolean" is "{ifc}.by_type('IfcBooleanResult')[0].id()"
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcHalfSpaceSolid/{half_space}"
    When I delete the selected objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I don't see "BBIM_Boolean"
    And I don't see "[{boolean}]"

Scenario: A half space solid only cuts the item explicitly selected when it is added
    # Regression test for #7663: once validate_type() has unioned an
    # already-clipped item together with an untouched sibling item (to keep a
    # mixed Items list schema-valid), adding another half space solid while
    # deliberately selecting one specific item must only cut that item, not
    # the whole union it happens to sit in.
    #
    # Object names are captured into variables rather than hardcoded, since
    # the underlying STEP ids shift whenever earlier entity allocation in an
    # empty project changes (see 45fa04a94b).
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the variable "cube" is "{ifc}.by_type('IfcExtrudedAreaSolid')[0].id()"
    And the object "Item/IfcExtrudedAreaSolid/{cube}" exists
    # Cut the cube on its own, before any sibling item exists.
    And I select the object "Item/IfcExtrudedAreaSolid/{cube}"
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the variable "cube_cut" is "{ifc}.by_type('IfcHalfSpaceSolid')[0].id()"
    And the object "Item/IfcHalfSpaceSolid/{cube_cut}" exists
    And the object "Item/IfcHalfSpaceSolid/{cube_cut}" is moved to "0,0,-0.1"
    # Add an untouched sibling item without leaving Item Mode. Exiting item
    # mode now forces validate_type() to union the cube's clip together with
    # this raw cylinder, purely to keep RepresentationType a valid,
    # homogeneous "CSG".
    And I open the "Add Item" menu
    And I click "Extruded Area Solid Cylinder"
    And the variable "cylinder" is "{ifc}.by_type('IfcExtrudedAreaSolid')[1].id()"
    And the object "Item/IfcExtrudedAreaSolid/{cylinder}" exists
    And I deselect all objects
    And I toggle edit mode
    When I evaluate expression "rep = ifcopenshell.util.representation.resolve_representation(ifcopenshell.util.representation.get_representation(tool.Ifc.get_entity(bpy.data.objects['IfcFurniture/Unnamed']), 'Model', 'Body', 'MODEL_VIEW')); assert rep.RepresentationType == 'CSG'; assert rep.Items[0].is_a('IfcBooleanResult'); assert rep.Items[0].Operator == 'UNION'"

    # Re-enter item mode and cut the CYLINDER specifically -- it is currently
    # a sibling of the cube's clip inside that UNION.
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcExtrudedAreaSolid/{cylinder}"
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the variable "cylinder_cut" is "{ifc}.by_type('IfcHalfSpaceSolid')[1].id()"
    And the object "Item/IfcHalfSpaceSolid/{cylinder_cut}" exists
    And the object "Item/IfcHalfSpaceSolid/{cylinder_cut}" is rotated by "180,0,0" deg
    And the object "Item/IfcHalfSpaceSolid/{cylinder_cut}" is moved to "0,0,-0.05"
    And I deselect all objects
    And I toggle edit mode
    # Only the cylinder should now be cut: the cube's own earlier clip must
    # be untouched, and the cube must not be merged into the cylinder's cut.
    When I evaluate expression "rep = ifcopenshell.util.representation.resolve_representation(ifcopenshell.util.representation.get_representation(tool.Ifc.get_entity(bpy.data.objects['IfcFurniture/Unnamed']), 'Model', 'Body', 'MODEL_VIEW')); union = rep.Items[0]; assert union.is_a('IfcBooleanResult'); assert union.Operator == 'UNION'; cube_branch, cyl_branch = union.FirstOperand, union.SecondOperand; assert cube_branch.is_a('IfcBooleanClippingResult'); assert cube_branch.FirstOperand.is_a('IfcExtrudedAreaSolid'); assert cyl_branch.is_a('IfcBooleanClippingResult'); assert cyl_branch.FirstOperand.is_a('IfcExtrudedAreaSolid'); assert cube_branch.FirstOperand.id() != cyl_branch.FirstOperand.id()"
