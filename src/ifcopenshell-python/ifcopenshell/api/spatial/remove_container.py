import ifcopenshell
import ifcopenshell.api.owner.update_owner_history as update_owner_history


class Usecase:
    def __init__(self, file, settings={}):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        contained_in_structure = self.settings["product"].ContainedInStructure

        if contained_in_structure:
            related_elements = list(contained_in_structure[0].RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                contained_in_structure[0].RelatedElements = related_elements
                update_owner_history.Usecase(self.file, {"element": contained_in_structure[0]}).execute()
            else:
                self.file.remove(contained_in_structure)
