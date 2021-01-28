import ifcopenshell
import ifcopenshell.util.date
from blenderbim.bim.ifc import IfcStore
from datetime import datetime


class Data:
    is_loaded = False
    products = {}
    objectives = {}

    @classmethod
    def load(cls, product_id=None):
        cls._file = IfcStore.get_file()
        if not cls._file:
            return
        if product_id:
            return cls.load_product(product_id)
        cls.load_objectives()
        cls.is_loaded = True

    @classmethod
    def load_product(cls, product_id):
        product = cls._file.by_id(product_id)
        cls.products[product_id] = []
        if not product.HasAssociations:
            return
        for association in product.HasAssociations:
            if association.is_a("IfcRelAssociatesConstraint"):
                if not association.RelatingConstraint.is_a("IfcObjective"):
                    continue # not yet implemented
                cls.products[product_id].append(association.RelatingConstraint.id())

    @classmethod
    def load_objectives(cls):
        cls.objectives = {}
        for constraint in cls._file.by_type("IfcObjective"):
            data = constraint.get_info()
            if cls._file.schema == "IFC2X3":
                for attribute in ["CreationTime"]:
                    if data[attribute]:
                        data[attribute] = ifcopenshell.util.date.ifc2datetime(data[attribute]).isoformat()
            cls.objectives[constraint.id()] = data
