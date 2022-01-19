# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
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
        if representation not in representations:
            return
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
        representation_map.MappedRepresentation = self.file.createIfcShapeRepresentation()
        ifcopenshell.util.element.remove_deep2(self.file, representation_map)
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
                        mapped_representations.append({"product": product, "representation": inverse})
                        just_representations.append(inverse)
        for item in mapped_representations:
            self.unassign_product_representation(item["product"], item["representation"])
        for representation in just_representations:
            ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
