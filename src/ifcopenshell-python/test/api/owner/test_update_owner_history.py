import time
import test.bootstrap
import ifcopenshell.api


class TestUpdateOwnerHistory(test.bootstrap.IFC4):
    def test_creating_an_owner_history_when_there_is_no_existing_history(self):
        get_user = ifcopenshell.api.owner.settings.get_user
        get_application = ifcopenshell.api.owner.settings.get_application

        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application

        element = self.file.createIfcWall()
        history = ifcopenshell.api.run("owner.update_owner_history", self.file, element=element)
        assert history.is_a("IfcOwnerHistory")
        assert element.OwnerHistory == history
        assert history.ChangeAction == "ADDED"
        assert abs(history.LastModifiedDate - time.time()) < 5
        assert history.LastModifyingApplication == application
        assert history.LastModifyingUser == user

        ifcopenshell.api.owner.settings.get_user = get_user
        ifcopenshell.api.owner.settings.get_application = get_application

    def test_updating_an_existing_history(self):
        get_user = ifcopenshell.api.owner.settings.get_user
        get_application = ifcopenshell.api.owner.settings.get_application

        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application

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

        ifcopenshell.api.owner.settings.get_user = get_user
        ifcopenshell.api.owner.settings.get_application = get_application

    def test_updating_an_existing_history_shared_by_multiple_elements(self):
        get_user = ifcopenshell.api.owner.settings.get_user
        get_application = ifcopenshell.api.owner.settings.get_application

        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application

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

        ifcopenshell.api.owner.settings.get_user = get_user
        ifcopenshell.api.owner.settings.get_application = get_application

    def test_doing_nothing_if_no_history_can_be_updated(self):
        person = self.file.createIfcPerson()
        assert ifcopenshell.api.run("owner.update_owner_history", self.file, element=person) == None
