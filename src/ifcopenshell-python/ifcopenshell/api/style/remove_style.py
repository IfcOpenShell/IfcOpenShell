import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"style": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.purge_styled_items(self.settings["style"])
        ifcopenshell.util.element.remove_deep(self.file, self.settings["style"])

    def purge_styled_items(self, style):
        for inverse in self.file.get_inverse(style):
            if inverse.is_a("IfcStyledItem") and len(inverse.Styles) == 1:
                self.purge_styled_representations(inverse)
                self.file.remove(inverse)

    def purge_styled_representations(self, styled_item):
        for inverse in self.file.get_inverse(styled_item):
            if inverse.is_a("IfcStyledRepresentation") and len(inverse.Items) == 1:
                self.purge_material_definition_representations(inverse)
                self.file.remove(inverse)

    def purge_material_definition_representations(self, styled_representation):
        for inverse in self.file.get_inverse(styled_representation):
            if inverse.is_a("IfcMaterialDefinitionRepresentation") and len(inverse.Representations) == 1:
                self.file.remove(inverse)
