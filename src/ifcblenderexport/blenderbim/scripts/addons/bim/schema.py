import os
import json
import ifcopenshell
from pathlib import Path

cwd = os.path.dirname(os.path.realpath(__file__))

class IfcSchema():
    def __init__(self):
        self.schema_dir = os.path.join(cwd, 'schema') # TODO: make configurable
        # TODO: Make it less troublesome
        self.products = [
            'IfcContext',
            'IfcElement',
            'IfcSpatialElement',
            'IfcStructural',
            'IfcMaterialDefinition',
            'IfcParameterizedProfileDef',
            'IfcBoundaryCondition',
            'IfcElementType'
        ]
        self.elements = {}
        self.property_files = []
        property_paths = Path(self.schema_dir).glob('Pset_*.ifc')
        for path in property_paths:
            self.property_files.append(ifcopenshell.open(path))
        self.psets = {}
        self.qtos = {}
        self.applicable_psets = {}
        self.applicable_qtos = {}
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

ifc = IfcSchema()
