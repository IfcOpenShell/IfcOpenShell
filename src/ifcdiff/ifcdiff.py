#!/usr/bin/env python3

# IfcDiff - Compare IFCs
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcDiff.
#
# IfcDiff is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcDiff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcDiff.  If not, see <http://www.gnu.org/licenses/>.

# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifcdiff.py`

import time
import json
import logging
import argparse
import numpy as np
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.classification
import ifcopenshell.util.selector
from deepdiff import DeepDiff


class IfcDiff:
    """Main IfcDiff application

    If you are using IfcDiff as a library, this is the class you should use.

    :param old_file: Filepath to the old file
    :type old_file: string
    :param new_file: Filepath to the new file
    :type new_file: string
    :param output_file: Filepath to the output JSON file to store the diff
        results
    :type output_file: string
    :param relationships: List of relationships to check. An empty list means
        that only geometry and attributes are compared.
    :type relationships: list[string]
    :param is_shallow: True if you want only the first difference to be listed.
        False if you want all differences to be checked. Choosing False means
        that comparisons will take longer.
    :type is_shallow: bool
    :param filter_elements: An IFC filter query if you only want to compare a
        subset of elements. For example: ``.IfcWall`` to only compare walls.
    :type filter_elements: string

    Example::

        from ifcdiff import IfcDiff

        ifc_diff = IfcDiff("/path/to/old.ifc", "/path/to/new.ifc", "/path/to/diff.json")
        ifc_diff.diff()
        print(ifc_diff.change_register)
        ifc_diff.export()
    """

    def __init__(self, old_file, new_file, output_file, relationships=None, is_shallow=True, filter_elements=None):
        self.old_file = old_file
        self.new_file = new_file
        self.output_file = output_file
        self.change_register = {}
        self.representation_ids = {}
        self.relationships = relationships
        self.precision = 1e-4
        self.is_shallow = is_shallow
        self.filter_elements = filter_elements

    def diff(self):
        print("# IFC Diff")
        logging.disable(logging.CRITICAL)
        self.load()

        self.precision = self.get_precision()

        if self.filter_elements:
            selector = ifcopenshell.util.selector.Selector()
            old_elements = set(e.GlobalId for e in selector.parse(self.old, self.filter_elements))
            new_elements = set(e.GlobalId for e in selector.parse(self.new, self.filter_elements))
        else:
            old_elements = set(e.GlobalId for e in self.old.by_type("IfcProduct"))
            new_elements = set(e.GlobalId for e in self.new.by_type("IfcProduct"))

        self.deleted_elements = old_elements - new_elements
        self.added_elements = new_elements - old_elements
        same_elements = new_elements - self.added_elements
        total_same_elements = len(same_elements)

        print(" - {} item(s) were deleted".format(len(self.deleted_elements)))
        print(" - {} item(s) were added".format(len(self.added_elements)))
        print(" - {} item(s) were retained between the old and new IFC file".format(total_same_elements))

        start = time.time()
        total_diffed = 0

        for global_id in same_elements:
            total_diffed += 1
            if total_diffed % 250 == 0:
                print("{}/{} diffed ...".format(total_diffed, total_same_elements), end="\r", flush=True)
            old = self.old.by_id(global_id)
            new = self.new.by_id(global_id)
            if self.diff_element(old, new) and self.is_shallow:
                continue
            if self.diff_element_relationships(old, new) and self.is_shallow:
                continue
            diff = self.diff_element_geometry(old, new)
            if diff:
                self.change_register.setdefault(new.GlobalId, {}).update({"geometry_changed": True})

        print(" - {} item(s) were changed either geometrically or with data".format(len(self.change_register.keys())))
        print("# Diff finished in {:.2f} seconds".format(time.time() - start))
        logging.disable(logging.NOTSET)

    def export(self):
        with open(self.output_file, "w", encoding="utf-8") as diff_file:
            json.dump(
                {
                    "added": list(self.added_elements),
                    "deleted": list(self.deleted_elements),
                    "changed": self.change_register,
                },
                diff_file,
                indent=4,
            )

    def load(self):
        print("Loading old file ...")
        self.old = ifcopenshell.open(self.old_file)
        print("Loading new file ...")
        self.new = ifcopenshell.open(self.new_file)

    def get_precision(self):
        contexts = [c for c in self.new.by_type("IfcGeometricRepresentationContext") if c.ContextType == "Model"]
        if contexts:
            return contexts[0].Precision or 1e-4
        return 1e-4

    def diff_element(self, old, new):
        diff = DeepDiff(
            [a for a in old if not isinstance(a, (ifcopenshell.entity_instance, tuple))],
            [a for a in new if not isinstance(a, (ifcopenshell.entity_instance, tuple))],
            math_epsilon=self.precision,
            ignore_string_type_changes=True,
            ignore_numeric_type_changes=True,
        )
        if diff and new.GlobalId:
            self.change_register.setdefault(new.GlobalId, {}).update({"attributes_changed": True})
            return True

    def diff_element_relationships(self, old, new):
        if not self.relationships:
            return
        for relationship in self.relationships:
            if relationship == "type":
                if ifcopenshell.util.element.get_type(old) != ifcopenshell.util.element.get_type(new):
                    self.change_register.setdefault(new.GlobalId, {}).update({"type_changed": True})
                    return True
            elif relationship == "property":
                old_psets = ifcopenshell.util.element.get_psets(old)
                new_psets = ifcopenshell.util.element.get_psets(new)
                try:
                    diff = DeepDiff(
                        old_psets,
                        new_psets,
                        math_epsilon=self.precision,
                        ignore_string_type_changes=True,
                        ignore_numeric_type_changes=True,
                        exclude_regex_paths=[r".*id$"],
                    )
                except:
                    diff = True
                if diff and new.GlobalId:
                    self.change_register.setdefault(new.GlobalId, {}).update({"properties_changed": diff})
                    return True
            elif relationship == "container":
                if ifcopenshell.util.element.get_container(old) != ifcopenshell.util.element.get_container(new):
                    self.change_register.setdefault(new.GlobalId, {}).update({"container_changed": True})
                    return True
            elif relationship == "aggregate":
                if ifcopenshell.util.element.get_aggregate(old) != ifcopenshell.util.element.get_aggregate(new):
                    self.change_register.setdefault(new.GlobalId, {}).update({"aggregate_changed": True})
                    return True
            elif relationship == "classification":
                old_id = "ItemReference" if self.old.schema == "IFC2X3" else "Identification"
                new_id = "ItemReference" if self.new.schema == "IFC2X3" else "Identification"
                old_refs = [getattr(r, old_id) for r in ifcopenshell.util.classification.get_references(old)]
                new_refs = [getattr(r, new_id) for r in ifcopenshell.util.classification.get_references(new)]
                if old_refs != new_refs:
                    self.change_register.setdefault(new.GlobalId, {}).update({"classification_changed": True})
                    return True

    def diff_element_geometry(self, old, new):
        old_placement = ifcopenshell.util.placement.get_local_placement(old.ObjectPlacement)
        new_placement = ifcopenshell.util.placement.get_local_placement(new.ObjectPlacement)
        if not np.allclose(old_placement[:, 3], new_placement[:, 3], atol=self.precision):
            return True
        if not np.allclose(old_placement[0:3, 0:3], new_placement[0:3, 0:3], atol=1e-2):
            return True
        old_openings = [o.RelatedOpeningElement.GlobalId for o in getattr(old, "HasOpenings", []) or []]
        new_openings = [o.RelatedOpeningElement.GlobalId for o in getattr(new, "HasOpenings", []) or []]
        if old_openings != new_openings:
            return True
        old_projections = [o.RelatedFeatureElement.GlobalId for o in getattr(old, "HasProjections", []) or []]
        new_projections = [o.RelatedFeatureElement.GlobalId for o in getattr(new, "HasProjections", []) or []]
        if old_projections != new_projections:
            return True
        old_rep_id = self.get_representation_id(old)
        new_rep_id = self.get_representation_id(new)
        rep_result = self.representation_ids.get(new_rep_id, None)
        if rep_result is not None:
            return rep_result
        if type(old_rep_id) != type(new_rep_id):
            self.representation_ids[new_rep_id] = True
            return True
        if new_rep_id is None:
            return
        result = self.diff_representation(old_rep_id, new_rep_id) or False
        self.representation_ids[new_rep_id] = result
        return result

    def diff_representation(self, old_rep_id, new_rep_id):
        old_rep = self.old.by_id(old_rep_id)
        new_rep = self.new.by_id(new_rep_id)
        if len(old_rep.Items) != len(new_rep.Items):
            return True
        for i, old_item in enumerate(old_rep.Items):
            result = self.diff_representation_item(old_item, new_rep.Items[i])
            if result is True:
                return True

    def diff_representation_item(self, old_item, new_item):
        if old_item.is_a() != new_item.is_a():
            return True
        try:
            diff = DeepDiff(
                old_item.get_info_2(recursive=True),
                new_item.get_info_2(recursive=True),
                custom_operators=[DiffTerminator()] if self.is_shallow else [],
                math_epsilon=self.precision,
                exclude_regex_paths=[r".*id']$"],
            )
        except:
            return True
        if diff:
            return True

    def get_representation_id(self, element):
        if not element.Representation:
            return
        for representation in element.Representation.Representations:
            if not representation.is_a("IfcShapeRepresentation"):
                continue
            if (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType != "MappedRepresentation"
            ):
                return representation.id()
            elif representation.RepresentationIdentifier == "Body":
                return representation.Items[0].MappingSource.MappedRepresentation.id()


class DiffTerminator:
    def match(self, level) -> bool:
        return True

    def give_up_diffing(self, level, diff_instance) -> bool:
        if any(diff_instance.tree.values()):
            raise Exception("Terminated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show the difference between two IFC files")
    parser.add_argument("old", type=str, help="The old IFC file")
    parser.add_argument("new", type=str, help="The new IFC file")
    parser.add_argument(
        "-o", "--output", type=str, help="The JSON diff file to output. Defaults to diff.json", default="diff.json"
    )
    parser.add_argument(
        "-r",
        "--relationships",
        type=str,
        help='A list of space-separated relationships, chosen from "type", "property", "container", "aggregate", "classification"',
        default="",
    )
    args = parser.parse_args()

    ifc_diff = IfcDiff(args.old, args.new, args.output, args.relationships.split())
    ifc_diff.diff()
    ifc_diff.export()
