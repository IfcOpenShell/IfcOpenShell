import blenderbim.bim.module.geometry.remove_representation as remove_representation
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"product": None, "representation": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcProduct"):
            self.unassign_product_representation(self.settings["product"], self.settings["representation"])
        elif self.settings["product"].is_a("IfcTypeProduct"):
            self.unassign_type_representation()

    def unassign_product_representation(self, product, representation):
        representations = list(product.Representation.Representations or [])
        representations.remove(representation)
        if not representations:
            self.file.remove(product.Representation)
        else:
            product.Representation.Representations = representations

    def unassign_type_representation(self):
        for representation_map in self.settings["product"].RepresentationMaps or []:
            if representation_map.MappedRepresentation == self.settings["representation"]:
                self.unassign_products_using_mapped_representation(representation_map)
                self.remove_representation_map_only(representation_map)
                break
        self.settings["product"].RepresentationMaps = self.settings["product"].RepresentationMaps or None

    def remove_representation_map_only(self, representation_map):
            dummy_representation = self.file.createIfcShapeRepresentation()
            representation_map.MappedRepresentation = dummy_representation
            ifcopenshell.util.element.remove_deep(self.file, representation_map)
            self.file.remove(representation_map)

    def unassign_products_using_mapped_representation(self, representation_map):
        mapped_representations = []
        just_representations = []
        for map_usage in representation_map.MapUsage or []:
            for inverse in self.file.get_inverse(map_usage):
                if not inverse.is_a("IfcShapeRepresentation"):
                    continue
                for definition in inverse.OfProductRepresentation or []:
                    for product in definition.ShapeOfProduct or []:
                        mapped_representations.append({
                            "product": product,
                            "representation": inverse
                        })
                        just_representations.append(inverse)
        for item in mapped_representations:
            self.unassign_product_representation(item["product"], item["representation"])
        for representation in just_representations:
            remove_representation.Usecase(self.file, {"representation": representation}).execute()
