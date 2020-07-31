#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifcdiff.py`

import ifcopenshell
from deepdiff import DeepDiff
import time
import json
import argparse
import decimal


class IfcDiff():
    def __init__(self, old_file, new_file, output_file, inverse_classes=None):
        self.old_file = old_file
        self.new_file = new_file
        self.output_file = output_file
        self.change_register = {}
        self.representation_ids = []
        self.inverse_classes = inverse_classes
        self.precision = 2

    def diff(self):
        print('# IFC Diff')
        self.load()

        self.precision = self.get_precision()

        old_elements = set(e.GlobalId for e in self.old.by_type('IfcProduct'))
        new_elements = set(e.GlobalId for e in self.new.by_type('IfcProduct'))

        self.deleted_elements = old_elements - new_elements
        self.added_elements = new_elements - old_elements
        same_elements = new_elements - self.added_elements
        total_same_elements = len(same_elements)

        print(' - {} item(s) were deleted'.format(len(self.deleted_elements)))
        print(' - {} item(s) were added'.format(len(self.added_elements)))
        print(' - {} item(s) were retained between the old and new IFC file'.format(total_same_elements))

        start = time.time()
        total_diffed = 0

        for global_id in same_elements:
            total_diffed += 1
            print('{}/{} diffed ...'.format(total_diffed, total_same_elements), end='\r', flush=True)
            old_element = self.old.by_id(global_id)
            new_element = self.new.by_id(global_id)
            self.diff_element(old_element, new_element)
            self.diff_element_inverse_relationships(old_element, new_element)

            representation_id = self.get_representation_id(new_element)
            if representation_id in self.representation_ids:
                continue
            self.representation_ids.append(representation_id)
            self.diff_element_geometry(old_element, new_element)

        print(' - {} item(s) were changed either geometrically or with data'.format(
            len(self.change_register.keys())))
        print('# Diff finished in {:.2f} seconds'.format(time.time() - start))

    def export(self):
        with open(self.output_file, 'w', encoding='utf-8') as diff_file:
            json.dump({
                    'added': list(self.added_elements),
                    'deleted': list(self.deleted_elements),
                    'changed': self.change_register,
                },
                diff_file,
                indent=4,
                cls=DiffEncoder)

    def load(self):
        print('Loading old file ...')
        self.old = ifcopenshell.open(self.old_file)
        print('Loading new file ...')
        self.new = ifcopenshell.open(self.new_file)

    def get_precision(self):
        try:
            precision = [c for c in self.new.by_type('IfcGeometricRepresentationContext') if c.ContextType == 'Model'][0].Precision
            exponent = decimal.Decimal(str(precision)).as_tuple().exponent
            if exponent < 0:
                return abs(exponent)
            return 0
        except:
            return 2

    def diff_element(self, old_element, new_element):
        diff = DeepDiff(old_element, new_element,
            significant_digits=self.precision, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
            exclude_regex_paths=[
                r'root.*id$',
                r'.*Representation.*',
                r'.*OwnerHistory.*',
                r'.*ObjectPlacement.*',
                ])
        if diff and new_element.GlobalId:
            self.change_register.setdefault(new_element.GlobalId, {}).update(diff)

    def diff_element_inverse_relationships(self, old_element, new_element):
        if not self.inverse_classes:
            return
        old_relationships_all = self.old.get_inverse(old_element)
        new_relationships_all = self.new.get_inverse(new_element)
        if self.inverse_classes[0] == 'all':
            old_relationships = old_relationships_all
            new_relationships = new_relationships_all
        else:
            old_relationships = [x for x in old_relationships_all if x.is_a() in self.inverse_classes]
            new_relationships = [x for x in new_relationships_all if x.is_a() in self.inverse_classes]

        diff = DeepDiff(old_relationships, new_relationships,
            significant_digits=self.precision, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
            exclude_regex_paths=[
                r'root.*id$',
                r'.*GlobalId.*',
                r'.*OwnerHistory.*',
                r'.*RelatedObjects.*',
                r'.*RelatingObject.*',
                r'.*RelatingDefinitions.*',
                r'.*RelatedObjectsType.*', # Deprecated in IFC4 anyway
                ])
        if diff and new_element.GlobalId:
            self.change_register.setdefault(new_element.GlobalId, {}).update(diff)

    def diff_element_geometry(self, old_element, new_element):
        try:
            DeepDiff(old_element.ObjectPlacement, new_element.ObjectPlacement,
                terminate_on_first=True,
                significant_digits=self.precision, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
                exclude_regex_paths=r'root.*id$')
            DeepDiff(old_element.Representation, new_element.Representation,
                terminate_on_first=True,
                skip_after_n=1000, # Arbitrary value to "skim" check
                significant_digits=self.precision, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
                exclude_regex_paths=r'root.*id$')
        except:
            if new_element.GlobalId:
                return self.change_register.setdefault(new_element.GlobalId, {}).update({'has_geometry_change': True})

    def get_representation_id(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            if not representation.is_a('IfcShapeRepresentation'):
                continue
            if representation.RepresentationIdentifier == 'Body' \
                and representation.RepresentationType != 'MappedRepresentation':
                return representation.id()
            elif representation.RepresentationIdentifier == 'Body':
                return representation.Items[0].MappingSource.MappedRepresentation.id()


class DiffEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return str(obj)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show the difference between two IFC files')
    parser.add_argument('old', type=str, help='The old IFC file')
    parser.add_argument('new', type=str, help='The new IFC file')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='The JSON diff file to output. Defaults to diff.json',
        default='diff.json')
    parser.add_argument(
        '-r',
        '--relationships',
        type=str,
        help='A list of IFC classes to check in inverse relationships, like "IfcRelDefinesByProperties", or "all".',
        default='')
    args = parser.parse_args()

    ifc_diff = IfcDiff(args.old, args.new, args.output, args.relationships.split())
    ifc_diff.diff()
    ifc_diff.export()
