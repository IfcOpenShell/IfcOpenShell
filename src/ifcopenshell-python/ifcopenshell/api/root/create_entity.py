import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file: str = "file", ifc_class: str = "IfcBuildingElementProxy", predefined_type: str = "type", name: str = "dummyName"):
        """Create Entity

        Create a new IFC Root entity

        :param file: The IFC file
        :param ifc_class: The IFC class
        :param predefined_type: The predefined type
        :param name: The name of the root entity
        :return: root element: The created root entity.
        """
        self.file = file
        self.settings = {
            "ifc_class": ifc_class,
            "predefined_type": predefined_type,
            "name": name,
        }
        # for key, value in settings.items():
        #     self.settings[key] = value

    def execute(self):
        element = self.file.create_entity(
            self.settings["ifc_class"],
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
            }
        )
        element.Name = self.settings["name"] or None
        if self.settings["predefined_type"]:
            if hasattr(element, "PredefinedType"):
                try:
                    element.PredefinedType = self.settings["predefined_type"]
                except:
                    element.PredefinedType = "USERDEFINED"
                    if hasattr(element, "ObjectType"):
                        element.ObjectType = self.settings["predefined_type"]
                    elif hasattr(element, "ElementType"):
                        element.ElementType = self.settings["predefined_type"]
            elif hasattr(element, "ObjectType"):
                element.ObjectType = self.settings["predefined_type"]
        if self.file.schema == "IFC2X3":
            self.handle_2x3_defaults(element)
        return element

    def handle_2x3_defaults(self, element):
        if element.is_a("IfcSpatialStructureElement"):
            element.CompositionType = "ELEMENT"
        elif element.is_a("IfcRoof"):
            element.ShapeType = "NOTDEFINED"
