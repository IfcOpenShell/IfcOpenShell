Feature: Owner
    Covers ownership history, people, organisations, roles, and addresses.

Scenario: Add person
    Given an empty IFC project
    When I press "bim.add_person"
    Then nothing happens

Scenario: Remove person
    Given an empty IFC project
    When I press "bim.add_person"
    And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
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
