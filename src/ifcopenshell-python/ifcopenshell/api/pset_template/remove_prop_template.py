import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "prop_template": None
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["prop_template"]):
            if len(inverse.HasPropertyTemplates) == 1:
                inverse.HasPropertyTemplates = []
            else:
                has_property_templates = list(inverse.HasPropertyTemplates)
                has_property_templates.remove(self.settings["prop_template"])
                inverse.HasPropertyTemplates = has_property_templates
        ifcopenshell.util.element.remove_deep(self.file, self.settings["prop_template"])
