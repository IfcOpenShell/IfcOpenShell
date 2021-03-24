import ifcopenshell
import ifcopenshell.util.schema


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "product": None,
            "reference": None,
            "classification": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        relating_classification = None

        if hasattr(self.settings["reference"], "ItemReference"):
            identification = self.settings["reference"].ItemReference  # IFC2X3
        else:
            identification = self.settings["reference"].Identification

        for reference in self.file.by_type("IfcClassificationReference"):
            if self.file.schema == "IFC2X3":
                if reference.ItemReference == identification:
                    relating_classification = reference
                    break
            else:
                if reference.Identification == identification:
                    relating_classification = reference
                    break

        if relating_classification:
            association = self.get_association(relating_classification)
            related_objects = set(association.RelatedObjects)
            related_objects.add(self.settings["product"])
            association.RelatedObjects = list(related_objects)
            return

        migrator = ifcopenshell.util.schema.Migrator()
        # This removal patch is to support a lightweight classification
        old_referenced_source = self.settings["reference"].ReferencedSource
        self.settings["reference"].ReferencedSource = None
        relating_classification = migrator.migrate(self.settings["reference"], self.file)
        relating_classification.ReferencedSource = self.settings["classification"]
        self.settings["reference"].ReferencedSource = old_referenced_source
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatedObjects": [self.settings["product"]],
                "RelatingClassification": relating_classification,
            }
        )

    def get_association(self, reference):
        if self.file.schema == "IFC2X3":
            for association in self.file.by_type("IfcRelAssociatesClassification"):
                if association.RelatingClassification == reference:
                    return association
        elif reference.ClassificationRefForObjects:
            return reference.ClassificationRefForObjects[0]
