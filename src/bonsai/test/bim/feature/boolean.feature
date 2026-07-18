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
    And the object "Item/IfcExtrudedAreaSolid/73" exists
    And I open the "Add Item" menu
    When I click "Half Space Solid"
    And the object "Item/IfcHalfSpaceSolid/90" exists
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I see "BBIM_Boolean"
    And I see "[91]"

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
    And the object "Item/IfcExtrudedAreaSolid/73" exists
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcHalfSpaceSolid/90"
    When I delete the selected objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I don't see "BBIM_Boolean"
    And I don't see "[91]"

Scenario: A half space solid only cuts the item explicitly selected when it is added
    # Regression test for #7663: once validate_type() has unioned an
    # already-clipped item together with an untouched sibling item (to keep a
    # mixed Items list schema-valid), adding another half space solid while
    # deliberately selecting one specific item must only cut that item, not
    # the whole union it happens to sit in.
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the object "Item/IfcExtrudedAreaSolid/73" exists
    # Cut the cube on its own, before any sibling item exists.
    And I select the object "Item/IfcExtrudedAreaSolid/73"
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the object "Item/IfcHalfSpaceSolid/86" exists
    And the object "Item/IfcHalfSpaceSolid/86" is moved to "0,0,-0.1"
    # Add an untouched sibling item without leaving Item Mode. Exiting item
    # mode now forces validate_type() to union the cube's clip together with
    # this raw cylinder, purely to keep RepresentationType a valid,
    # homogeneous "CSG".
    And I open the "Add Item" menu
    And I click "Extruded Area Solid Cylinder"
    And the object "Item/IfcExtrudedAreaSolid/100" exists
    And I deselect all objects
    And I toggle edit mode
    When I evaluate expression "rep = ifcopenshell.util.representation.resolve_representation(ifcopenshell.util.representation.get_representation(tool.Ifc.get_entity(bpy.data.objects['IfcFurniture/Unnamed']), 'Model', 'Body', 'MODEL_VIEW')); assert rep.RepresentationType == 'CSG'; assert rep.Items[0].is_a('IfcBooleanResult'); assert rep.Items[0].Operator == 'UNION'"

    # Re-enter item mode and cut the CYLINDER specifically -- it is currently
    # a sibling of the cube's clip inside that UNION.
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcExtrudedAreaSolid/100"
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the object "Item/IfcHalfSpaceSolid/111" exists
    And the object "Item/IfcHalfSpaceSolid/111" is rotated by "180,0,0" deg
    And the object "Item/IfcHalfSpaceSolid/111" is moved to "0,0,-0.05"
    And I deselect all objects
    And I toggle edit mode
    # Only the cylinder should now be cut: the cube's own earlier clip must
    # be untouched, and the cube must not be merged into the cylinder's cut.
    When I evaluate expression "rep = ifcopenshell.util.representation.resolve_representation(ifcopenshell.util.representation.get_representation(tool.Ifc.get_entity(bpy.data.objects['IfcFurniture/Unnamed']), 'Model', 'Body', 'MODEL_VIEW')); union = rep.Items[0]; assert union.is_a('IfcBooleanResult'); assert union.Operator == 'UNION'; cube_branch, cyl_branch = union.FirstOperand, union.SecondOperand; assert cube_branch.is_a('IfcBooleanClippingResult'); assert cube_branch.FirstOperand.is_a('IfcExtrudedAreaSolid'); assert cyl_branch.is_a('IfcBooleanClippingResult'); assert cyl_branch.FirstOperand.is_a('IfcExtrudedAreaSolid'); assert cube_branch.FirstOperand.id() != cyl_branch.FirstOperand.id()"
