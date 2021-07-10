import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"relating_structural_member": None, "related_structural_connection": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for connection in self.settings["related_structural_connection"].ConnectsStructuralMembers or []:
            if connection.RelatingStructuralMember == self.settings["relating_structural_member"]:
                return
        rel = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelConnectsStructuralMember")
        rel.RelatingStructuralMember = self.settings["relating_structural_member"]
        rel.RelatedStructuralConnection = self.settings["related_structural_connection"]
        return rel
