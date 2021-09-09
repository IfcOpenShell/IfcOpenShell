import ifcopenshell
import ifcopenshell.util.date
from datetime import datetime


class Data:
    is_loaded = False
    products = {}
    objectives = {}
    metrics = {}
    references = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.objectives = {}
        cls.metrics = {}
        cls.references = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            return cls.load_product(product_id)
        cls.load_objectives()
        cls.load_metrics()
        cls.load_references()
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
                    continue  # not yet implemented
                cls.products[product_id].append(association.RelatingConstraint.id())

    @classmethod
    def load_objectives(cls):
        cls.objectives = {}
        for constraint in cls._file.by_type("IfcObjective"):
            data = constraint.get_info()
            for key, value in data.items():
                if not value:
                    continue

            if cls._file.schema == "IFC2X3":
                for attribute in ["CreationTime"]:
                    if data[attribute]:
                        data[attribute] = ifcopenshell.util.date.ifc2datetime(data[attribute]).isoformat()
            data["BenchmarkValues"] = [metric.id() for metric in constraint.BenchmarkValues or []]
            cls.objectives[constraint.id()] = data

    @classmethod
    def load_metrics(cls):
        cls.metrics = {}
        for metric in cls._file.by_type("IfcMetric"):
            data = metric.get_info()
            for key, value in data.items():
                if not value:
                    continue
            data["ConstrainedObjects"] = []
            for association in cls._file.by_type("IfcRelAssociatesConstraint"):
                if association.RelatingConstraint.id() == metric.id():
                    data["ConstrainedObjects"] = [o.id() for o in association.RelatedObjects or []]
            if metric.DataValue:
                data["DataValue"] = data["DataValue"].id()
            if metric.ReferencePath:
                data["ReferencePath"] = data["ReferencePath"].id()
            cls.metrics[metric.id()] = data

    @classmethod
    def load_references(cls):
        cls.references = {}
        for reference in cls._file.by_type("IfcReference"):
            data = reference.get_info()
            for key, value in data.items():
                if not value:
                    continue
            cls.references[refenrece.id()] = data
