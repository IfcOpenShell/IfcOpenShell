import ifcopenshell
import ifcopenshell.util.date
from blenderbim.bim.ifc import IfcStore
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
    def load(cls, product_id=None):
        cls._file = IfcStore.get_file()
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
