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


class Data:
    products = {}
    representations = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.representations = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        cls.products[product_id] = []
        product = file.by_id(product_id)
        representations = []
        if product.is_a("IfcProduct") and product.Representation:
            representations = product.Representation.Representations
        elif product.is_a("IfcTypeProduct"):
            representations = [rm.MappedRepresentation for rm in product.RepresentationMaps or []]
        for representation in representations:
            c = representation.ContextOfItems
            rep_id = int(representation.id())
            cls.representations[rep_id] = {
                "RepresentationIdentifier": representation.RepresentationIdentifier,
                "RepresentationType": representation.RepresentationType,
                "ContextOfItems": {
                    "ContextType": c.ContextType,
                    "ContextIdentifier": c.ContextIdentifier,
                    "TargetView": c.TargetView if c.is_a("IfcGeometricRepresentationSubContext") else "",
                },
            }
            cls.products[product_id].append(rep_id)
