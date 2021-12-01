import time
import test.bootstrap
import ifcopenshell.api


class TestUpdateOwnerHistory(test.bootstrap.IFC4):
    def test_creating_an_owner_history_when_there_is_no_existing_history(self):
        get_person = ifcopenshell.api.owner.settings.get_person
        get_organisation = ifcopenshell.api.owner.settings.get_organisation
        get_application = ifcopenshell.api.owner.settings.get_application

        person = self.file.createIfcPerson()
        organisation = self.file.createIfcOrganization()
        application = self.file.createIfcApplication()
        user = self.file.createIfcPersonAndOrganization()
        user.ThePerson = person
        user.TheOrganization = organisation
        ifcopenshell.api.owner.settings.get_person = lambda x : person
        ifcopenshell.api.owner.settings.get_organisation = lambda x : organisation
        ifcopenshell.api.owner.settings.get_application = lambda x : application

        element = self.file.createIfcWall()
        history = ifcopenshell.api.run("owner.update_owner_history", self.file, element=element)
        assert history.is_a("IfcOwnerHistory")
        assert element.OwnerHistory == history
        assert history.ChangeAction == "ADDED"
        assert abs(history.LastModifiedDate - time.time()) < 5
        assert history.LastModifyingApplication == application
        assert history.LastModifyingUser == user

        ifcopenshell.api.owner.settings.get_person = get_person
        ifcopenshell.api.owner.settings.get_organisation = get_organisation
        ifcopenshell.api.owner.settings.get_application = get_application
        ifcopenshell.api.owner.settings.users = {}

    def test_updating_an_existing_history(self):
        get_person = ifcopenshell.api.owner.settings.get_person
        get_organisation = ifcopenshell.api.owner.settings.get_organisation
        get_application = ifcopenshell.api.owner.settings.get_application

        person = self.file.createIfcPerson()
        organisation = self.file.createIfcOrganization()
        application = self.file.createIfcApplication()
        user = self.file.createIfcPersonAndOrganization()
        user.ThePerson = person
        user.TheOrganization = organisation
        ifcopenshell.api.owner.settings.get_person = lambda x : person
        ifcopenshell.api.owner.settings.get_organisation = lambda x : organisation
        ifcopenshell.api.owner.settings.get_application = lambda x : application

        element = self.file.createIfcWall()
        old_history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        element.OwnerHistory = old_history

        new_history = ifcopenshell.api.run("owner.update_owner_history", self.file, element=element)
        assert new_history == old_history
        assert element.OwnerHistory == new_history
        assert new_history.ChangeAction == "MODIFIED"
        assert abs(new_history.LastModifiedDate - time.time()) < 5
        assert new_history.LastModifyingApplication == application
        assert new_history.LastModifyingUser == user

        ifcopenshell.api.owner.settings.get_person = get_person
        ifcopenshell.api.owner.settings.get_organisation = get_organisation
        ifcopenshell.api.owner.settings.get_application = get_application
        ifcopenshell.api.owner.settings.users = {}

    def test_updating_an_existing_history_shared_by_multiple_elements(self):
        get_person = ifcopenshell.api.owner.settings.get_person
        get_organisation = ifcopenshell.api.owner.settings.get_organisation
        get_application = ifcopenshell.api.owner.settings.get_application

        person = self.file.createIfcPerson()
        organisation = self.file.createIfcOrganization()
        application = self.file.createIfcApplication()
        user = self.file.createIfcPersonAndOrganization()
        user.ThePerson = person
        user.TheOrganization = organisation
        ifcopenshell.api.owner.settings.get_person = lambda x : person
        ifcopenshell.api.owner.settings.get_organisation = lambda x : organisation
        ifcopenshell.api.owner.settings.get_application = lambda x : application

        element = self.file.createIfcWall()
        element2 = self.file.createIfcWall()
        old_history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        element.OwnerHistory = old_history
        element2.OwnerHistory = old_history

        new_history = ifcopenshell.api.run("owner.update_owner_history", self.file, element=element)
        assert new_history != old_history
        assert element.OwnerHistory == new_history
        assert new_history.ChangeAction == "MODIFIED"
        assert abs(new_history.LastModifiedDate - time.time()) < 5
        assert new_history.LastModifyingApplication == application
        assert new_history.LastModifyingUser == user

        ifcopenshell.api.owner.settings.get_person = get_person
        ifcopenshell.api.owner.settings.get_organisation = get_organisation
        ifcopenshell.api.owner.settings.get_application = get_application
        ifcopenshell.api.owner.settings.users = {}

    def test_doing_nothing_if_no_history_can_be_updated(self):
        person = self.file.createIfcPerson()
        assert ifcopenshell.api.run("owner.update_owner_history", self.file, element=person) == None

    def test_creating_a_user_if_one_does_not_exist(self):
        get_person = ifcopenshell.api.owner.settings.get_person
        get_organisation = ifcopenshell.api.owner.settings.get_organisation
        get_application = ifcopenshell.api.owner.settings.get_application

        person = self.file.createIfcPerson()
        organisation = self.file.createIfcOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_person = lambda x : person
        ifcopenshell.api.owner.settings.get_organisation = lambda x : organisation
        ifcopenshell.api.owner.settings.get_application = lambda x : application

        element = self.file.createIfcWall()
        element.OwnerHistory = ifcopenshell.api.run("owner.create_owner_history", self.file)

        history = ifcopenshell.api.run("owner.update_owner_history", self.file, element=element)
        assert history.LastModifyingUser.ThePerson == person
        assert history.LastModifyingUser.TheOrganization == organisation

        ifcopenshell.api.owner.settings.get_person = get_person
        ifcopenshell.api.owner.settings.get_organisation = get_organisation
        ifcopenshell.api.owner.settings.get_application = get_application
        ifcopenshell.api.owner.settings.users = {}
