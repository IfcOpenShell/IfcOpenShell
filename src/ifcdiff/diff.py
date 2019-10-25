import ifcopenshell
from deepdiff import DeepDiff
import time
import json

class IfcDiff():
    def __init__(self, old_file, new_file):
        self.old_file = old_file
        self.new_file = new_file
        self.change_register = {}
        self.representation_ids = []

    def diff(self):
        print('# IFC Diff')
        self.load()

        old_elements = set(e.GlobalId for e in self.old.by_type('IfcElement'))
        new_elements = set(e.GlobalId for e in self.new.by_type('IfcElement'))

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

            representation_id = self.get_representation_id(new_element)
            if representation_id in self.representation_ids:
                continue
            self.representation_ids.append(representation_id)
            self.diff_element_geometry(old_element, new_element)

        print(' - {} item(s) were changed either geometrically or with data'.format(
            len(self.change_register.keys())))
        print('# Diff finished in {:.2f} seconds'.format(time.time() - start))

    def load(self):
        print('Loading old file ...')
        self.old = ifcopenshell.open(self.old_file)
        print('Loading new file ...')
        self.new = ifcopenshell.open(self.new_file)

    def diff_element(self, old_element, new_element):
        diff = DeepDiff(old_element, new_element,
            significant_digits=2, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
            exclude_regex_paths=[
                r'root.*id$',
                r'.*Representation.*',
                r'.*OwnerHistory.*',
                r'.*ObjectPlacement.*',
                ])
        if diff and new_element.GlobalId:
            self.change_register.setdefault(new_element.GlobalId, {}).update(diff)

    def diff_element_geometry(self, old_element, new_element):
        try:
            DeepDiff(old_element.ObjectPlacement, new_element.ObjectPlacement,
                terminate_on_first=True,
                significant_digits=2, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
                exclude_regex_paths=r'root.*id$')
            DeepDiff(old_element.Representation, new_element.Representation,
                terminate_on_first=True,
                skip_after_n=1000, # Arbitrary value to "skim" check
                significant_digits=2, ignore_string_type_changes=True, ignore_numeric_type_changes=True,
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

ifc_diff = IfcDiff('old.ifc', 'new.ifc')
ifc_diff.diff()

class DiffEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return str(obj)

with open('diff.json', 'w', encoding='utf-8') as diff_file:
    json.dump({
        'added': list(ifc_diff.added_elements),
        'deleted': list(ifc_diff.deleted_elements),
        'changed': ifc_diff.change_register,
        }, diff_file, indent=4, cls=DiffEncoder)
