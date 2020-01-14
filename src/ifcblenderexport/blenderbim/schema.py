import os
import json
import ifcopenshell

cwd = os.path.dirname(os.path.realpath(__file__))

class IfcSchema():
    def __init__(self):
        self.schema_dir = os.path.join(cwd, 'schema') # TODO: make configurable
        self.products = [
            'IfcElement',
            'IfcSpatialStructureElement',
            'IfcStructural',
            'IfcMaterialDefinition',
            'IfcParameterizedProfileDef'
        ]
        self.elements = {}
        self.property_file = ifcopenshell.open(os.path.join(self.schema_dir, 'IFC4_ADD2.ifc'))
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

        for property in self.property_file.by_type('IfcPropertySetTemplate'):
            if property.Name[0:4] == 'Qto_':
                # self.qtos.append({ })
                pass
            else:
                self.psets[property.Name] = {
                    'HasPropertyTemplates': {p.Name: p for p in property.HasPropertyTemplates}}
