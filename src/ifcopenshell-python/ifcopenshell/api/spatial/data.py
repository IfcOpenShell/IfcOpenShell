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
    spatial_elements = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.spatial_elements = {}

    @classmethod
    def load(cls, file, product_id=None):
        if product_id:
            return cls.load_product(file, product_id)
        cls.load_spatial_elements(file)

    @classmethod
    def load_product(cls, file, product_id):
        if not file:
            return
        product = file.by_id(product_id)
        if not hasattr(product, "ContainedInStructure"):
            cls.products[product_id] = None
        elif product.ContainedInStructure:
            structure = product.ContainedInStructure[0].RelatingStructure
            cls.products[product_id] = {"type": structure.is_a(), "Name": structure.Name, "id": int(structure.id())}
        else:
            cls.products[product_id] = {"type": None, "Name": None, "id": None}

    @classmethod
    def load_spatial_elements(cls, file):
        if not file:
            return
        cls.spatial_elements = {}
        ifc_class = "IfcSpatialElement"
        if file.schema == "IFC2X3":
            ifc_class = "IfcSpatialStructureElement"
        for element in file.by_type(ifc_class):
            decomposes = None
            if element.Decomposes:
                decomposes = element.Decomposes[0].RelatingObject.id()
            is_decomposed_by = []
            if element.IsDecomposedBy:
                for rel in element.IsDecomposedBy:
                    is_decomposed_by.extend([e.id() for e in rel.RelatedObjects])
            cls.spatial_elements[element.id()] = {
                "Name": element.Name,
                "LongName": element.LongName,
                "Decomposes": decomposes,
                "IsDecomposedBy": is_decomposed_by,
            }
