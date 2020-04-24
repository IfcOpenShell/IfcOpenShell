import os
import json
import ifcopenshell
import bpy
from pathlib import Path

cwd = os.path.dirname(os.path.realpath(__file__))

class IfcSchema():
    def __init__(self):
        self.schema_dir = os.path.join(cwd, 'schema') # TODO: make configurable
        self.data_dir = os.path.join(cwd, 'data') # TODO: make configurable
        # TODO: Make it less troublesome
        self.products = [
            'IfcContext',
            'IfcElement',
            'IfcSpatialElement',
            'IfcGroup',
            'IfcStructural',
            'IfcMaterialDefinition',
            'IfcParameterizedProfileDef',
            'IfcBoundaryCondition',
            'IfcElementType'
        ]
        self.elements = {}

        self.property_files = []
        property_paths = Path(os.path.join(self.data_dir, 'pset')).glob('*.ifc')
        for path in property_paths:
            self.property_files.append(ifcopenshell.open(path))
        self.property_files.append(ifcopenshell.open(os.path.join(self.schema_dir, 'Pset_IFC4_ADD2.ifc')))

        self.classification_files = {}
        classification_paths = Path(self.schema_dir).glob('classifications/*.ifc')
        for path in classification_paths:
            self.classification_files[os.path.basename(path).split('.')[0]] = ifcopenshell.open(path)

        self.psets = {}
        self.qtos = {}
        self.applicable_psets = {}
        self.applicable_qtos = {}
        self.classifications = {}
        self.load()

    def load(self):
        for product in self.products:
            with open(os.path.join(self.schema_dir, f'{product}_IFC4.json')) as f:
                setattr(self, product, json.load(f))
                self.elements.update(getattr(self, product))

        with open(os.path.join(self.schema_dir, 'ifc_types_IFC4.json')) as f:
            self.type_map = json.load(f)

        for property_file in self.property_files:
            for prop in property_file.by_type('IfcPropertySetTemplate'):
                if prop.Name[0:4] == 'Qto_':
                    self.qtos[prop.Name] = {
                        'HasPropertyTemplates': {p.Name: p for p in prop.HasPropertyTemplates}}
                    entity = prop.ApplicableEntity if prop.ApplicableEntity else 'IfcRoot'
                    self.applicable_qtos.setdefault(entity, []).append(prop.Name)
                else:
                    self.psets[prop.Name] = {
                        'HasPropertyTemplates': {p.Name: p for p in prop.HasPropertyTemplates}}
                    entity = prop.ApplicableEntity if prop.ApplicableEntity else 'IfcRoot'
                    self.applicable_psets.setdefault(entity, []).append(prop.Name)

        for filename, classification_file in self.classification_files.items():
            classification = classification_file.by_type('IfcClassification')[0]
            self.classifications[filename] = classification

    def load_classification(self, filename):
        classification = self.classifications[filename]
        return {
            'name': '',
            'description': '',
            'children': self.get_classification_references(classification)
        }

    def get_classification_references(self, classification):
        references = {}
        if not classification.HasReferences:
            return references
        for reference in classification.HasReferences:
            references[reference.Identification] = {
                'location': reference.Location,
                'identification': reference.Identification,
                'name': reference.Name,
                'description': reference.Description,
                'children': self.get_classification_references(reference)
            }
        return references


ifc = IfcSchema()
