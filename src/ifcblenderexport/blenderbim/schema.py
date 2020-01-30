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
            'IfcElement',
            'IfcSpatialStructureElement',
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
        self.load()

    def load(self):
        for product in self.products:
            with open(os.path.join(self.schema_dir, f'{product}_IFC4.json')) as f:
                setattr(self, product, json.load(f))
                self.elements.update(getattr(self, product))

        with open(os.path.join(self.schema_dir, 'ifc_types_IFC4.json')) as f:
            self.type_map = json.load(f)

        for property_file in self.property_files:
            for property in property_file.by_type('IfcPropertySetTemplate'):
                if property.Name[0:4] == 'Qto_':
                    # self.qtos.append({ })
                    pass
                else:
                    self.psets[property.Name] = {
                        'HasPropertyTemplates': {p.Name: p for p in property.HasPropertyTemplates}}

ifc = IfcSchema()
