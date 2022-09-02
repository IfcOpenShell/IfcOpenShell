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

import ifcopenshell
import ifcopenshell.util.date


class Data:
    is_loaded = False
    products = {}
    classifications = {}
    references = {}
    library_file = None
    library_classifications = {}
    library_references = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.classifications = {}
        cls.references = {}
        cls.library_file = None
        cls.library_classifications = {}
        cls.library_references = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            return cls.load_product_classifications(product_id)
        cls.load_classifications()
        cls.load_references()
        cls.is_loaded = True

    @classmethod
    def load_product_classifications(cls, product_id):
        product = cls._file.by_id(product_id)
        cls.products[product_id] = []
        if not product.HasAssociations:
            return
        for association in product.HasAssociations:
            if association.is_a("IfcRelAssociatesClassification"):
                cls.products[product_id].append(association.RelatingClassification.id())

    @classmethod
    def load_classifications(cls):
        cls.classifications = {}
        for classification in cls._file.by_type("IfcClassification"):
            data = classification.get_info()
            if cls._file.schema == "IFC2X3" and data["EditionDate"]:
                data["EditionDate"] = ifcopenshell.util.date.ifc2datetime(data["EditionDate"]).isoformat()
            cls.classifications[classification.id()] = data

    @classmethod
    def load_references(cls):
        cls.references = {}
        for reference in cls._file.by_type("IfcClassificationReference"):
            data = reference.get_info()
            if reference.ReferencedSource:
                # data["ReferencedSource"] = cls.get_referenced_source(reference.ReferencedSource)
                data["ReferencedSource"] = reference.ReferencedSource.id()
            cls.references[reference.id()] = data

    @classmethod
    def get_referenced_source(cls, reference):
        if reference.is_a("IfcClassification"):
            return reference
        elif reference.is_a("IfcClassificationReference") and reference.ReferencedSource:
            return cls.get_referenced_source(reference.ReferencedSource)

    @classmethod
    def load_library(cls, filepath):
        cls.library_file = ifcopenshell.open(filepath)
        cls.library_classifications = {}
        for classification in cls.library_file.by_type("IfcClassification"):
            cls.library_classifications[classification.id()] = classification.Name
