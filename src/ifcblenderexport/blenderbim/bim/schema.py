import os
import json
import ifcopenshell
import ifcopenshell.util.pset
import bpy
from pathlib import Path

cwd = os.path.dirname(os.path.realpath(__file__))


class IfcSchema:
    def __init__(self):
        self.schema_dir = Path(cwd).joinpath("schema")  # TODO: make configurable
        self.data_dir = Path(cwd).joinpath("data")  # TODO: make configurable
        # TODO: Make it less troublesome
        self.products = [
            "IfcElement",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcMaterialDefinition",
            "IfcParameterizedProfileDef",
            "IfcBoundaryCondition",
            "IfcElementType",
            "IfcAnnotation",
        ]
        self.elements = {}

        self.property_files = []
        property_paths = self.data_dir.joinpath("pset").glob("*.ifc")
        self.psetqto = ifcopenshell.util.pset.PsetQto("IFC4")
        for path in property_paths:
            self.psetqto.templates.append(ifcopenshell.open(path))

        self.classification_files = {}
        self.classifications = {}
        self.load()

    def load(self):
        for product in self.products:
            with open(os.path.join(self.schema_dir, f"{product}_IFC4.json")) as f:
                setattr(self, product, json.load(f))
                self.elements.update(getattr(self, product))

        with open(os.path.join(self.schema_dir, "ifc_types_IFC4.json")) as f:
            self.type_map = json.load(f)

    def load_classification(self, name, classification_index=None):
        if name not in self.classifications:
            if classification_index is not None:
                self.classification_files[name] = ifcopenshell.file.from_string(
                    bpy.context.scene.BIMProperties.classifications[classification_index].data
                )
            else:
                classification_path = os.path.join(self.schema_dir, "classifications", "{}.ifc".format(name))
                self.classification_files[name] = ifcopenshell.open(classification_path)
            self.classifications[name] = self.classification_files[name].by_type("IfcClassification")[0]
        classification = self.classifications[name]
        bpy.context.scene.BIMProperties.active_classification_name = self.classifications[name].Name
        return {"name": "", "description": "", "children": self.get_classification_references(classification)}

    def get_classification_references(self, classification):
        references = {}
        if not hasattr(classification, "HasReferences") or not classification.HasReferences:
            return references
        for reference in classification.HasReferences:
            references[reference.Identification] = {
                "location": reference.Location,
                "identification": reference.Identification,
                "name": reference.Name,
                "description": reference.Description,
                "children": self.get_classification_references(reference),
            }
        return references


ifc = IfcSchema()
