import time
import test.bootstrap
import ifcopenshell.api


class TestCreateOwnerHistory(test.bootstrap.IFC4):
    def test_creating_nothing_if_no_user_or_application_is_available(self):
        history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        assert history is None

    def test_creating_a_history_using_a_specified_user_and_application(self):
        old_get_user = ifcopenshell.api.owner.settings.get_user
        old_get_application = ifcopenshell.api.owner.settings.get_application
        user = self.file.createIfcPersonAndOrganization()
        application = self.file.createIfcApplication()
        ifcopenshell.api.owner.settings.get_user = lambda x: user
        ifcopenshell.api.owner.settings.get_application = lambda x: application
        history = ifcopenshell.api.run("owner.create_owner_history", self.file)
        ifcopenshell.api.owner.settings.get_user = old_get_user
        ifcopenshell.api.owner.settings.get_application = old_get_application
        assert history.is_a("IfcOwnerHistory")
        assert history.OwningUser == user
        assert history.OwningApplication == application
        assert history.State == "READWRITE"
        assert history.ChangeAction == "ADDED"
        assert abs(time.time() - history.LastModifiedDate) < 5
        assert history.LastModifyingUser == user
        assert history.LastModifyingApplication == application
        assert abs(time.time() - history.CreationDate) < 5
