@owner
Feature: Owner

Scenario: Add person
    Given an empty IFC project
    When I press "bim.add_person"
    Then nothing happens

Scenario: Remove person
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[-1].id()"
    And I press "bim.remove_person(person={person})"
    Then nothing happens

Scenario: Add person attribute
    Given an empty IFC project
    When I press "bim.add_person"
    And I press "bim.add_person_attribute(name='MiddleNames')"
    And I press "bim.add_person_attribute(name='PrefixTitles')"
    And I press "bim.add_person_attribute(name='SuffixTitles')"
    Then nothing happens

Scenario: Remove person attribute
    Given an empty IFC project
    When I press "bim.add_person"
    And I press "bim.add_person_attribute(name='MiddleNames')"
    And I press "bim.remove_person_attribute(name='MiddleNames', id=0)"
    And I press "bim.add_person_attribute(name='PrefixTitles')"
    And I press "bim.remove_person_attribute(name='PrefixTitles', id=0)"
    And I press "bim.add_person_attribute(name='SuffixTitles')"
    And I press "bim.remove_person_attribute(name='SuffixTitles', id=0)"
    Then nothing happens

Scenario: Enable editing person
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.enable_editing_person(person={person})"
    Then "scene.BIMOwnerProperties.active_person_id" is "{person}"

Scenario: Disable editing person
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.enable_editing_person(person={person})"
    And I press "bim.disable_editing_person"
    Then "scene.BIMOwnerProperties.active_person_id" is "0"

Scenario: Edit person
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.enable_editing_person(person={person})"
    And I press "bim.edit_person"
    Then "scene.BIMOwnerProperties.active_person_id" is "0"

Scenario: Add role
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_role(parent={person})"
    Then nothing happens

Scenario: Remove role
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_role(parent={person})"
    And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
    And I press "bim.remove_role(role={role})"
    Then nothing happens

Scenario: Enable editing role
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_role(parent={person})"
    And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
    And I press "bim.enable_editing_role(role={role})"
    Then nothing happens

Scenario: Disable editing role
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_role(parent={person})"
    And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
    And I press "bim.enable_editing_role(role={role})"
    And I press "bim.disable_editing_role()"
    Then nothing happens

Scenario: Edit role
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_role(parent={person})"
    And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
    And I press "bim.enable_editing_role(role={role})"
    And I press "bim.edit_role()"
    Then nothing happens

Scenario: Add address
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    Then nothing happens

Scenario: Add address attribute
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.enable_editing_address(address={address})"
    And I press "bim.add_address_attribute(name='AddressLines')"
    Then nothing happens

Scenario: Remove address attribute
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.enable_editing_address(address={address})"
    And I press "bim.add_address_attribute(name='AddressLines')"
    And I press "bim.remove_address_attribute(name='AddressLines', id=0)"
    Then nothing happens

Scenario: Remove address
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.remove_address(address={address})"
    Then nothing happens

Scenario: Enable editing address
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.enable_editing_address(address={address})"
    Then nothing happens

Scenario: Disable editing address
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.enable_editing_address(address={address})"
    And I press "bim.disable_editing_address()"
    Then nothing happens

Scenario: Edit address
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
    And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
    And I press "bim.enable_editing_address(address={address})"
    And I press "bim.edit_address()"
    Then nothing happens

Scenario: Add organisation
    Given an empty IFC project
    When I press "bim.add_organisation"
    Then nothing happens

Scenario: Enable editing organisation
    Given an empty IFC project
    When I press "bim.add_organisation"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[0].id()"
    And I press "bim.enable_editing_organisation(organisation={organisation})"
    Then "scene.BIMOwnerProperties.active_organisation_id" is "{organisation}"

Scenario: Disable editing organisation
    Given an empty IFC project
    When I press "bim.add_organisation"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[0].id()"
    And I press "bim.enable_editing_organisation(organisation={organisation})"
    And I press "bim.disable_editing_organisation"
    Then "scene.BIMOwnerProperties.active_organisation_id" is "0"

Scenario: Edit organisation
    Given an empty IFC project
    When I press "bim.add_organisation"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[0].id()"
    And I press "bim.enable_editing_organisation(organisation={organisation})"
    And I press "bim.edit_organisation"
    Then "scene.BIMOwnerProperties.active_organisation_id" is "0"

Scenario: Remove organisation
    Given an empty IFC project
    When I press "bim.add_organisation"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[-1].id()"
    And I press "bim.remove_organisation(organisation={organisation})"
    Then nothing happens

Scenario: Add person and organisation
    Given an empty IFC project
    When I press "bim.add_person"
    And I press "bim.add_organisation"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[0].id()"
    And I press "bim.add_person_and_organisation(person={person}, organisation={organisation})"
    Then nothing happens

Scenario: Remove person and organisation
    Given an empty IFC project
    When I press "bim.add_person"
    And I press "bim.add_organisation"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[-1].id()"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[-1].id()"
    And I press "bim.add_person_and_organisation(person={person}, organisation={organisation})"
    # Note: these are set to -1 temporarily to prevent crashing due to bug #1747
    And the variable "pno" is "{ifc}.by_type('IfcPersonAndOrganization')[-1].id()"
    And I press "bim.remove_person_and_organisation(person_and_organisation={pno})"
    Then nothing happens

Scenario: Set user
    Given an empty IFC project
    When I press "bim.add_person"
    And I press "bim.add_organisation"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
    And the variable "organisation" is "{ifc}.by_type('IfcOrganization')[0].id()"
    And I press "bim.add_person_and_organisation(person={person}, organisation={organisation})"
    And the variable "user" is "{ifc}.by_type('IfcPersonAndOrganization')[0].id()"
    And I press "bim.set_user(user={user})"
    Then nothing happens

Scenario: Clear user
    Given an empty IFC project
    When I press "bim.clear_user(user={user})"
    Then nothing happens

Scenario: Add actor
    Given an empty IFC project
    And I press "bim.add_person"
    When I press "bim.add_actor"
    Then nothing happens

Scenario: Remove actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[-1].id()"
    When I press "bim.remove_actor(actor={actor})"
    Then nothing happens

Scenario: Enable editing actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[0].id()"
    When I press "bim.enable_editing_actor(actor={actor})"
    Then "scene.BIMOwnerProperties.active_actor_id" is "{actor}"

Scenario: Disable editing actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[0].id()"
    And I press "bim.enable_editing_actor(actor={actor})"
    When I press "bim.disable_editing_actor"
    Then "scene.BIMOwnerProperties.active_actor_id" is "0"

Scenario: Edit actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[0].id()"
    And I press "bim.enable_editing_actor(actor={actor})"
    When I press "bim.edit_actor"
    Then "scene.BIMOwnerProperties.active_actor_id" is "0"

Scenario: Assign actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[0].id()"
    And the object "IfcWall/Cube" is selected
    When I press "bim.assign_actor(actor={actor})"
    Then nothing happens

Scenario: Unassign actor
    Given an empty IFC project
    And I press "bim.add_person"
    And I press "bim.add_actor"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "actor" is "{ifc}.by_type('IfcActor')[0].id()"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_actor(actor={actor})"
    When I press "bim.unassign_actor(actor={actor})"
    Then nothing happens
