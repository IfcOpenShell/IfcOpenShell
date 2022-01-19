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
from datetime import datetime


class Data:
    is_loaded = False
    products = {}
    references = {}
    information = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.references = {}
        cls.information = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            return cls.load_product(product_id)
        cls.load_references()
        cls.load_information()
        cls.is_loaded = True

    @classmethod
    def load_product(cls, product_id):
        product = cls._file.by_id(product_id)
        cls.products[product_id] = []
        if not product.HasAssociations:
            return
        for association in product.HasAssociations:
            if association.is_a("IfcRelAssociatesDocument"):
                cls.products[product_id].append(association.RelatingDocument.id())

    @classmethod
    def load_information(cls):
        cls.information = {}
        for information in cls._file.by_type("IfcDocumentInformation"):
            data = information.get_info()
            if cls._file.schema == "IFC2X3":
                for attribute in ["CreationTime", "LastRevisionTime", "ValidFrom", "ValidUntil"]:
                    if data[attribute]:
                        data[attribute] = ifcopenshell.util.date.ifc2datetime(data[attribute]).isoformat()
                if data["ElectronicFormat"]:
                    data["ElectronicFormat"] = "{}/{}".format(
                        information.ElectronicFormat.MimeContentType, information.ElectronicFormat.MimeSubtype
                    )
            cls.information[information.id()] = data

    @classmethod
    def load_references(cls):
        cls.references = {}
        for reference in cls._file.by_type("IfcDocumentReference"):
            data = reference.get_info()
            if cls._file.schema == "IFC2X3":
                if reference.ReferenceToDocument:
                    data["ReferencedDocument"] = reference.ReferenceToDocument[0].id()
            elif reference.ReferencedDocument:
                data["ReferencedDocument"] = reference.ReferencedDocument.id()
            cls.references[reference.id()] = data
