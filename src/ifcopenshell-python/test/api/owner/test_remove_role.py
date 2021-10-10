import test.bootstrap
import ifcopenshell.api


class TestRemoveRole(test.bootstrap.IFC4):
    def test_removing_a_role(self):
        role = self.file.createIfcActorRole()
        ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        assert len(self.file.by_type("IfcActorRole")) == 0

    def test_ensuring_organisation_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        organisation = self.file.createIfcOrganization()
        organisation.Roles = [role]
        ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        assert organisation.Roles is None

    def test_ensuring_person_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        person = self.file.createIfcPerson()
        person.Roles = [role]
        ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        assert person.Roles is None

    def test_ensuring_person_and_organisation_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        person_and_organisation = self.file.createIfcPersonAndOrganization()
        person_and_organisation.Roles = [role]
        ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        assert person_and_organisation.Roles is None

    def test_deleting_resource_approval_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcResourceApprovalRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcResourceConstraintRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        organisation = self.file.createIfcOrganization()
        self.file.createIfcExternalReferenceRelationship(RelatedResourceObjects=[organisation])
        ifcopenshell.api.run("owner.remove_organisation", self.file, organisation=organisation)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0
