import test.bootstrap
import ifcopenshell.api


class TestRemovePersonAndOrganisation(test.bootstrap.IFC4):
    def test_removing(self):
        user = self.file.createIfcPersonAndOrganization()
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcPersonAndOrganization")) == 0

    def test_deleting_actors(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcActor(GlobalId=ifcopenshell.guid.new(), TheActor=user)
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcActor")) == 0

    def test_ensuring_document_information_should_not_be_left_in_an_invalid_set_cardinality(self):
        user = self.file.createIfcPersonAndOrganization()
        document_information = self.file.createIfcDocumentInformation(Editors=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert document_information.Editors is None

    def test_deleting_resource_approval_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcResourceApprovalRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcResourceConstraintRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcExternalReferenceRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0

    def test_deleting_owner_history(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcOwnerHistory(OwningUser=user)
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcOwnerHistory")) == 0
