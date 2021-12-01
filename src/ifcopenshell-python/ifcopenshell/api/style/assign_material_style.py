class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "material": None,
            "style": None,
            "context": None,
            "should_use_presentation_style_assignment": False,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.style = self.settings["style"]
        if self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]:
            self.style = self.file.createIfcPresentationStyleAssignment([self.settings["style"]])

        if self.settings["material"].HasRepresentation:
            self.modify_existing_definition_representation()
        else:
            self.create_new_definition_representation()

    def modify_existing_definition_representation(self):
        definition_representation = self.settings["material"].HasRepresentation[0]
        representation = self.get_styled_representation(definition_representation)
        if representation:
            potential_orphans = []
            items = list(representation.Items)
            new_items = []
            removed_items = []
            for item in items:
                if not item.is_a("IfcStyledItem"):
                    continue
                if self.has_proposed_style(item):
                    return
                if self.has_same_style_type(item):
                    removed_items.append(item)
                else:
                    new_items.append(item)
            new_items.append(self.create_styled_item())
            representation.Items = new_items
            for item in removed_items:
                if len(self.file.get_inverse(item)) == 0:
                    self.file.remove(item)
        else:
            representations = list(definition_representation.Representations)
            representations.append(self.create_styled_representation())
            definition_representation.Representations = representations

    def has_proposed_style(self, styled_item):
        return bool([s for s in styled_item.Styles if s == self.settings["style"]])

    def has_same_style_type(self, styled_item):
        return bool([s for s in styled_item.Styles if s.is_a() == self.settings["style"].is_a()])

    def create_new_definition_representation(self):
        representation = self.create_styled_representation()
        definition_representation = self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            **{"Representations": [representation], "RepresentedMaterial": self.settings["material"]}
        )

    def get_styled_representation(self, definition_representation):
        representations = [
            r
            for r in definition_representation.Representations
            if r.is_a("IfcStyledRepresentation") and r.ContextOfItems == self.settings["context"]
        ]
        if representations:
            return representations[0]

    def create_styled_representation(self):
        return self.file.create_entity(
            "IfcStyledRepresentation",
            **{
                "ContextOfItems": self.settings["context"],
                "RepresentationIdentifier": self.settings["context"].ContextIdentifier,
                "Items": [self.create_styled_item()],
            }
        )

    def create_styled_item(self):
        return self.file.create_entity("IfcStyledItem", **{"Styles": [self.style], "Name": self.settings["style"].Name})
