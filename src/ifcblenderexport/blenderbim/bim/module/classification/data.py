import ifcopenshell
import ifcopenshell.util.date
from blenderbim.bim.ifc import IfcStore


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
    def load(cls, product_id=None):
        cls._file = IfcStore.get_file()
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
                data["EditionDate"] = ifcopenshell.util.date(data.EditionDate).isoformat()
            cls.classifications[classification.id()] = data

    @classmethod
    def load_references(cls):
        cls.references = {}
        for reference in cls._file.by_type("IfcClassificationReference"):
            data = reference.get_info()
            if reference.ReferencedSource:
                #data["ReferencedSource"] = cls.get_referenced_source(reference.ReferencedSource)
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
