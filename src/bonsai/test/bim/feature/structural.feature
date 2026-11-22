@structural
Feature: Structural

Scenario: Add element - a structural point connection
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralPointConnection"
    And I set the "Representation" property to "Vertex"
    When I click "OK"
    Then the object "IfcStructuralPointConnection/Foo" data is a "Vertex" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralPointConnection/Foo"
    And I toggle edit mode
    Then the object "Item/IfcVertexPoint/112" exists

Scenario: Add element - a structural curve member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralCurveMember"
    And I set the "Representation" property to "Edge"
    When I click "OK"
    Then the object "IfcStructuralCurveMember/Foo" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralCurveMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcEdge/115" exists

Scenario: Edit a structural curve member's edge to lie along its axis
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralCurveMember"
    And I set the "Representation" property to "Edge"
    And I click "OK"
    And I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralCurveMember/Foo"
    And I toggle edit mode
    And I select the object "Item/IfcEdge/115"
    And I toggle edit mode
    When I evaluate expression "import bmesh; mesh = bpy.context.edit_object.data; bm = bmesh.from_edit_mesh(mesh); bm.verts.ensure_lookup_table(); bm.verts[1].co = (0.0, 0.0, 3.0); bmesh.update_edit_mesh(mesh)"
    And I evaluate expression "obj = bpy.context.edit_object; bpy.ops.object.mode_set(mode='OBJECT'); tool.Geometry.edit_meshlike_item(obj)"
    Then I evaluate expression "import pytest; assert {ifc}.by_type('IfcStructuralCurveMember')[0].Axis.DirectionRatios == pytest.approx((-1.0, 0.0, 0.0), abs=1e-6)"

Scenario: Add element - a structural surface member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralSurfaceMember"
    And I set the "Representation" property to "Face"
    When I click "OK"
    Then the object "IfcStructuralSurfaceMember/Foo" data is a "Face" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralSurfaceMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcFaceSurface/134" exists

Scenario: Add structural item - a curve member of the chosen predefined type in the current model
    Given an empty IFC project
    And I press "bim.add_structural_analysis_model"
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveMember"
    And I set "scene.BIMStructuralProperties.structural_item_predefined_type" to "PIN_JOINED_MEMBER"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralCurveMember/Unnamed" is an "IfcStructuralCurveMember"
    And I evaluate expression "assert bpy.context.scene.objects['IfcStructuralCurveMember/Unnamed'].visible_get()"
    And the object "IfcStructuralCurveMember/Unnamed" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"
    And I evaluate expression "assert tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].PredefinedType == 'PIN_JOINED_MEMBER'"
    And I evaluate expression "assert tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].HasAssignments[0].RelatingGroup.is_a('IfcStructuralAnalysisModel')"

Scenario: Add structural item - a surface member
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralSurfaceMember"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralSurfaceMember/Unnamed" data is a "Face" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - a point connection, which has no predefined type
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralPointConnection/Unnamed" data is a "Vertex" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - a curve connection
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveConnection"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralCurveConnection/Unnamed" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - with the Structural Tool hotkey
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    When I press "bim.structural_hotkey(hotkey='S_A')"
    Then the object "IfcStructuralPointConnection/Unnamed" is an "IfcStructuralPointConnection"

Scenario: Connect structural items - a connection to the members selected with it, once
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveMember"
    And I press "bim.add_structural_item"
    And I rename the object "IfcStructuralCurveMember/Unnamed" to "IfcStructuralCurveMember/M1"
    And I press "bim.add_structural_item"
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    And I press "bim.add_structural_item"
    And the object "IfcStructuralCurveMember/M1" is selected
    And additionally the object "IfcStructuralCurveMember/Unnamed" is selected
    And additionally the object "IfcStructuralPointConnection/Unnamed" is selected
    When I press "bim.structural_hotkey(hotkey='S_C')"
    And I press "bim.connect_structural_items"
    Then I evaluate expression "assert len(tool.Ifc.get().by_type('IfcRelConnectsStructuralMember')) == 2"
    And I evaluate expression "assert {r.RelatedStructuralConnection.is_a() for r in tool.Ifc.get().by_type('IfcRelConnectsStructuralMember')} == {'IfcStructuralPointConnection'}"

Scenario: Add structural support - fixed, then pinned in its place
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    And I press "bim.add_structural_item"
    And the object "IfcStructuralPointConnection/Unnamed" is selected
    When I press "bim.add_structural_support(support='FIXED')"
    Then I evaluate expression "c = tool.Ifc.get().by_type('IfcStructuralPointConnection')[0].AppliedCondition; assert c.Name == 'Fixed' and c.TranslationalStiffnessZ.wrappedValue is True and c.RotationalStiffnessZ.wrappedValue is True"
    When I press "bim.add_structural_support(support='PINNED')"
    Then I evaluate expression "c = tool.Ifc.get().by_type('IfcStructuralPointConnection')[0].AppliedCondition; assert c.Name == 'Pinned' and c.TranslationalStiffnessX.wrappedValue is True and c.RotationalStiffnessX.wrappedValue is False"
    And I evaluate expression "assert len(tool.Ifc.get().by_type('IfcBoundaryNodeCondition')) == 1"

Scenario: Assign structural items to the current model - unassign and assign again
    Given an empty IFC project
    And I press "bim.add_structural_analysis_model"
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveMember"
    And I press "bim.add_structural_item"
    And the object "IfcStructuralCurveMember/Unnamed" is selected
    When I press "bim.structural_hotkey(hotkey='A_P')"
    Then I evaluate expression "assert not tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].HasAssignments"
    When I press "bim.structural_hotkey(hotkey='C_P')"
    Then I evaluate expression "assert tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].HasAssignments[0].RelatingGroup.is_a('IfcStructuralAnalysisModel')"

Scenario: Edit the axis of a curve member from the Structural Tool
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveMember"
    And I press "bim.add_structural_item"
    And the object "IfcStructuralCurveMember/Unnamed" is selected
    When I press "bim.structural_hotkey(hotkey='A_E')"
    Then I evaluate expression "assert bpy.context.active_object.BIMStructuralProperties.is_editing_axis"

Scenario: Update representation - a structural surface member stays a face with its local axes
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralSurfaceMember"
    And I set the "Representation" property to "Face"
    And I click "OK"
    And the variable "plane" is "tool.Ifc.get_entity(bpy.data.objects['IfcStructuralSurfaceMember/Foo']).Representation.Representations[0].Items[0].FaceSurface.id()"
    And I evaluate expression "tool.Ifc.get().by_id({plane}).Position.RefDirection = tool.Ifc.get().createIfcDirection((0., 1., 0.))"
    And I evaluate expression "[v for v in bpy.data.objects['IfcStructuralSurfaceMember/Foo'].data.vertices if (v.co - Vector((1, 1, 0))).length < 1e-6][0].co = (2, 1, 0)"
    When I press "bim.update_representation(obj='IfcStructuralSurfaceMember/Foo')"
    Then the object "IfcStructuralSurfaceMember/Foo" data is a "Face" representation of "Model/Reference/GRAPH_VIEW"
    And the variable "face" is "tool.Ifc.get_entity(bpy.data.objects['IfcStructuralSurfaceMember/Foo']).Representation.Representations[0].Items[0].id()"
    And I evaluate expression "assert tool.Ifc.get().by_id({face}).is_a('IfcFaceSurface')"
    And I evaluate expression "assert sorted(tuple(round(c, 3) for c in e.EdgeElement.EdgeStart.VertexGeometry.Coordinates) for e in tool.Ifc.get().by_id({face}).Bounds[0].Bound.EdgeList) == [(0, 0, 0), (0, 1000, 0), (1000, 0, 0), (2000, 1000, 0)]"
    And I evaluate expression "assert np.allclose(tool.Ifc.get().by_id({face}).FaceSurface.Position.Axis.DirectionRatios, (0, 0, 1))"
    And I evaluate expression "assert np.allclose(tool.Ifc.get().by_id({face}).FaceSurface.Position.RefDirection.DirectionRatios, (0, 1, 0))"

Scenario: Edit item - a structural surface member's face is the whole of its mesh
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralSurfaceMember"
    And I set the "Representation" property to "Face"
    And I click "OK"
    And I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralSurfaceMember/Foo"
    And I toggle edit mode
    And I evaluate expression "[v for v in bpy.data.objects['Item/IfcFaceSurface/134'].data.vertices if (v.co - Vector((1, 1, 0))).length < 1e-6][0].co = (2, 1, 0)"
    When I evaluate expression "tool.Geometry.edit_meshlike_item(bpy.data.objects['Item/IfcFaceSurface/134'])"
    Then the variable "face" is "tool.Ifc.get_entity(bpy.data.objects['IfcStructuralSurfaceMember/Foo']).Representation.Representations[0].Items[0].id()"
    And I evaluate expression "assert tool.Ifc.get().by_id({face}).is_a('IfcFaceSurface')"
    And I evaluate expression "assert sorted(tuple(round(c, 3) for c in e.EdgeElement.EdgeStart.VertexGeometry.Coordinates) for e in tool.Ifc.get().by_id({face}).Bounds[0].Bound.EdgeList) == [(0, 0, 0), (0, 1000, 0), (1000, 0, 0), (2000, 1000, 0)]"

Scenario: Load structural analysis models
    Given an empty IFC project
    When I press "bim.load_structural_analysis_models"
    Then nothing happens

Scenario: Add structural analysis model
    Given an empty IFC project
    And I press "bim.load_structural_analysis_models"
    When I press "bim.add_structural_analysis_model"
    Then nothing happens

Scenario: Disable structural analysis model editing UI
    Given an empty IFC project
    And I press "bim.load_structural_analysis_models"
    When I press "bim.disable_structural_analysis_model_editing_ui"
    Then nothing happens

Scenario: Enable editing structural load group activities
    Given an empty IFC project
    And the variable "member" is "ifcopenshell.api.root.create_entity({ifc}, ifc_class='IfcStructuralCurveMember', name='Beam').id()"
    And the variable "load" is "ifcopenshell.api.structural.add_structural_load({ifc}, name='Wind', ifc_class='IfcStructuralLoadLinearForce').id()"
    And the variable "activity" is "ifcopenshell.api.structural.add_structural_activity({ifc}, applied_load={ifc}.by_id({load}), structural_member={ifc}.by_id({member}), ifc_class='IfcStructuralCurveAction').id()"
    And the variable "load_group" is "ifcopenshell.api.structural.add_structural_load_group({ifc}, name='Wind').id()"
    And I evaluate expression "ifcopenshell.api.group.assign_group({ifc}, products=[{ifc}.by_id({activity})], group={ifc}.by_id({load_group}))"
    When I press "bim.enable_editing_structural_load_group_activities(load_group={load_group})"
    Then "scene.BIMStructuralProperties.load_group_activities[0].name" is "Wind on Beam"
    And "scene.BIMStructuralProperties.load_group_activities[0].applied_load_class" is "IfcStructuralLoadLinearForce"

Scenario: Enable editing structural load group activities - an activity assigned to no item
    Given an empty IFC project
    And the variable "load" is "ifcopenshell.api.structural.add_structural_load({ifc}, name='Wind', ifc_class='IfcStructuralLoadSingleForce').id()"
    And the variable "activity" is "ifcopenshell.api.root.create_entity({ifc}, ifc_class='IfcStructuralPointAction').id()"
    And I evaluate expression "{ifc}.by_id({activity}).AppliedLoad = {ifc}.by_id({load})"
    And the variable "load_group" is "ifcopenshell.api.structural.add_structural_load_group({ifc}, name='Wind').id()"
    And I evaluate expression "ifcopenshell.api.group.assign_group({ifc}, products=[{ifc}.by_id({activity})], group={ifc}.by_id({load_group}))"
    When I press "bim.enable_editing_structural_load_group_activities(load_group={load_group})"
    Then "scene.BIMStructuralProperties.load_group_activities[0].name" is "Wind on Unnamed"
