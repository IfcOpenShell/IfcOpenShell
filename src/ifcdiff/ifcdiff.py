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
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.util.placement
import ifcopenshell.util.classification
import ifcopenshell.util.representation
from deepdiff import DeepDiff
from orderly_set import OrderedSet
from typing import Optional, Union, Literal, Any


__version__ = version = "0.0.0"


RELATIONSHIP_TYPE = Literal["geometry", "attributes", "type", "property", "container", "aggregate", "classification"]


class IfcDiff:
    """Main IfcDiff application

    If you are using IfcDiff as a library, this is the class you should use.

    :param old: IFC file object for the old model
    :param new: IFC file object for the new model
    :param relationships: List of relationships to check. None means that only
        geometry is compared. See RELATIONSHIP_TYPE for available relationships.
    :param is_shallow: True if you want only the first difference to be listed.
        False if you want all differences to be checked. Choosing False means
        that comparisons will take longer.
    :param filter_elements: An IFC filter query if you only want to compare a
        subset of elements. For example: ``IfcWall`` to only compare walls.

    Example::

        from ifcdiff import IfcDiff

        ifc_diff = IfcDiff("/path/to/old.ifc", "/path/to/new.ifc", "/path/to/diff.json")
        ifc_diff.diff()
        print(ifc_diff.change_register)
        ifc_diff.export()
    """

    added_elements: set[ifcopenshell.entity_instance]
    deleted_elements: set[ifcopenshell.entity_instance]
    # GlobalIds to changes dictionary.
    change_register: dict[str, dict[str, Any]]

    def __init__(
        self,
        old: ifcopenshell.file,
        new: ifcopenshell.file,
        relationships: Optional[list[RELATIONSHIP_TYPE]] = None,
        is_shallow: bool = True,
        filter_elements: Optional[str] = None,
    ):
        self.old = old
        self.new = new
        self.change_register = {}
        self.representation_ids = {}
        self.relationships = relationships or ["geometry"]
        self.precision = 1e-4
        self.is_shallow = is_shallow
        self.filter_elements = filter_elements

    def diff(self) -> None:
        logging.disable(logging.CRITICAL)

        self.precision = self.get_precision()

        if self.filter_elements:
            old_elements = set(
                e.GlobalId for e in ifcopenshell.util.selector.filter_elements(self.old, self.filter_elements)
            )
            new_elements = set(
                e.GlobalId for e in ifcopenshell.util.selector.filter_elements(self.new, self.filter_elements)
            )
        else:
            old_elements = self.old.by_type("IfcElement")
            if self.old.schema == "IFC2X3":
                old_elements += self.old.by_type("IfcSpatialStructureElement")
            else:
                old_elements += self.old.by_type("IfcSpatialElement")
            old_elements = set(e.GlobalId for e in old_elements if not e.is_a("IfcFeatureElement"))
            new_elements = self.new.by_type("IfcElement")
            if self.new.schema == "IFC2X3":
                new_elements += self.new.by_type("IfcSpatialStructureElement")
            else:
                new_elements += self.new.by_type("IfcSpatialElement")
            new_elements = set(e.GlobalId for e in new_elements if not e.is_a("IfcFeatureElement"))

        print(" - {} item(s) are in the old model".format(len(old_elements)))
        print(" - {} item(s) are in the new model".format(len(new_elements)))

        self.deleted_elements = old_elements - new_elements
        self.added_elements = new_elements - old_elements
        same_elements = new_elements - self.added_elements
        total_same_elements = len(same_elements)

        print(" - {} item(s) were added".format(len(self.added_elements)))
        print(" - {} item(s) were deleted".format(len(self.deleted_elements)))
        print(" - {} item(s) are common to both models".format(total_same_elements))

        total_diffed = 0

        potential_old_changes = []
        potential_new_changes = []

        should_check_attributes = False
        should_check_geometry = False
        should_check_other = False

        for relationship in self.relationships:
            if relationship == "attributes":
                should_check_attributes = True
            elif relationship == "geometry":
                should_check_geometry = True
            else:
                should_check_other = True

        for global_id in same_elements:
            total_diffed += 1
            if total_diffed % 250 == 0:
                print("{}/{} diffed ...".format(total_diffed, total_same_elements), end="\r", flush=True)
            old = self.old.by_id(global_id)
            new = self.new.by_id(global_id)
            if should_check_attributes:
                if self.diff_element(old, new) and self.is_shallow:
                    continue
            if should_check_other:
                if self.diff_element_relationships(old, new) and self.is_shallow:
                    continue
            if should_check_geometry:
                # Option 1: check everything heuristically using the iterator (seems faster)
                if ifcopenshell.util.representation.get_representation(new, "Model", "Body", "MODEL_VIEW"):
                    potential_old_changes.append(old)
                    potential_new_changes.append(new)
                # Option 2: check first using Python, then fallback to iterator (twice as slow)
                # diff = self.diff_element_basic_geometry(old, new)
                # if diff:
                #    self.change_register.setdefault(new.GlobalId, {}).update({"geometry_changed": True})
                # else:
                #    potential_old_changes.append(old)
                #    potential_new_changes.append(new)

        print(" - {} item(s) had simple changes".format(len(self.change_register.keys())))

        if potential_old_changes:
            print(" - {} item(s) are queued for a detailed geometry check".format(len(potential_old_changes)))
            print("... processing old shapes ...")
            old_shapes = self.summarise_shapes(self.old, potential_old_changes)
            print("... processing new shapes ...")
            new_shapes = self.summarise_shapes(self.new, potential_new_changes)
            print("... comparing shapes ...")
            for global_id, old_shape in old_shapes.items():
                new_shape = new_shapes.get(global_id, None)
                if not new_shape:
                    self.change_register.setdefault(global_id, {}).update({"geometry_changed": True})
                    continue
                del new_shapes[global_id]
                diff = DeepDiff(old_shape, new_shape, math_epsilon=1e-5)
                if diff:
                    self.change_register.setdefault(global_id, {}).update({"geometry_changed": True})
                    continue

            for global_id in new_shapes.keys():
                self.change_register.setdefault(global_id, {}).update({"geometry_changed": True})

        print(" - {} item(s) were changed".format(len(self.change_register.keys())))

        logging.disable(logging.NOTSET)

    def summarise_shapes(
        self, ifc: ifcopenshell.file, elements: list[ifcopenshell.entity_instance]
    ) -> dict[str, dict[str, Any]]:
        shapes = {}
        iterator = ifcopenshell.geom.iterator(
            self.get_settings(ifc), ifc, multiprocessing.cpu_count(), include=elements
        )
        valid_file = iterator.initialize()
        while True:
            shape = iterator.get()
            element = ifc.by_id(shape.id)
            geometry = shape.geometry
            if geometry.verts:
                shapes[element.GlobalId] = {
                    "total_verts": len(geometry.verts),
                    "sum_verts": sum(geometry.verts),
                    "min_vert": min(geometry.verts),
                    "max_vert": max(geometry.verts),
                    "matrix": tuple(shape.transformation.matrix),
                    "openings": sorted(
                        [o.RelatedOpeningElement.GlobalId for o in getattr(element, "HasOpenings", []) or []]
                    ),
                    "projections": sorted(
                        [o.RelatedFeatureElement.GlobalId for o in getattr(element, "HasProjections", []) or []]
                    ),
                }
            if not iterator.next():
                break
        return shapes

    def get_settings(self, ifc: ifcopenshell.file) -> ifcopenshell.geom.settings:
        settings = ifcopenshell.geom.settings()
        # Are you feeling lucky?
        settings.set("disable-boolean-result", True)
        # Are you feeling very lucky?
        settings.set("disable-opening-subtractions", True)
        # Facetation is to accommodate broken Revit files
        # See https://forums.buildingsmart.org/t/suggestions-on-how-to-improve-clarity-of-representation-context-usage-in-documentation/3663/6?u=moult
        body_contexts = [
            c.id()
            for c in ifc.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier in ["Body", "Facetation"]
        ]
        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        body_contexts.extend(
            [
                c.id()
                for c in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
                if c.ContextType == "Model"
            ]
        )
        if body_contexts:
            settings.set("context-ids", body_contexts)
        return settings

    def json_dump_default(self, obj):
        # result of DeepDiff may contain ordered sets
        if isinstance(obj, (OrderedSet, set)):
            return list(obj)
        return json.JSONEncoder.default(None, obj)

    def export(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as diff_file:
            json.dump(
                {
                    "added": list(self.added_elements),
                    "deleted": list(self.deleted_elements),
                    "changed": self.change_register,
                },
                diff_file,
                indent=4,
                default=self.json_dump_default,
            )

    def get_precision(self) -> float:
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
                old_type = ifcopenshell.util.element.get_type(old)
                new_type = ifcopenshell.util.element.get_type(new)
                if old_type is not None and new_type is not None:
                    if old_type.GlobalId != new_type.GlobalId:
                        self.change_register.setdefault(new.GlobalId, {}).update({"type_changed": True})
                        return True
                elif old_type != new_type:
                    # one of the types is None while the other is not None
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

    def diff_element_basic_geometry(self, old, new):
        old_placement = ifcopenshell.util.placement.get_local_placement(old.ObjectPlacement)
        new_placement = ifcopenshell.util.placement.get_local_placement(new.ObjectPlacement)
        if not np.allclose(old_placement[:, 3], new_placement[:, 3], atol=self.precision):
            return True
        if not np.allclose(old_placement[0:3, 0:3], new_placement[0:3, 0:3], atol=1e-2):
            return True
        old_openings = sorted([o.RelatedOpeningElement.GlobalId for o in getattr(old, "HasOpenings", []) or []])
        new_openings = sorted([o.RelatedOpeningElement.GlobalId for o in getattr(new, "HasOpenings", []) or []])
        if old_openings != new_openings:
            return True
        old_projections = sorted([o.RelatedFeatureElement.GlobalId for o in getattr(old, "HasProjections", []) or []])
        new_projections = sorted([o.RelatedFeatureElement.GlobalId for o in getattr(new, "HasProjections", []) or []])
        if old_projections != new_projections:
            return True
        # Option 3: check completely using Python with get_info_2 (extremely slow, not worth it)
        # old_rep_id = self.get_representation_id(old)
        # new_rep_id = self.get_representation_id(new)
        # rep_result = self.representation_ids.get(new_rep_id, None)
        # if rep_result is not None:
        #    return rep_result
        # if type(old_rep_id) != type(new_rep_id):
        #    self.representation_ids[new_rep_id] = True
        #    return True
        # if new_rep_id is None:
        #    return
        # result = self.diff_representation(old_rep_id, new_rep_id) or False
        # self.representation_ids[new_rep_id] = result
        # return result

    def diff_representation(self, old_rep_id: int, new_rep_id: int) -> bool:
        old_rep = self.old.by_id(old_rep_id)
        new_rep = self.new.by_id(new_rep_id)
        if len(old_rep.Items) != len(new_rep.Items):
            return True
        for i, old_item in enumerate(old_rep.Items):
            result = self.diff_representation_item(old_item, new_rep.Items[i])
            if result is True:
                return True
        return False

    def diff_representation_item(
        self, old_item: ifcopenshell.entity_instance, new_item: ifcopenshell.entity_instance
    ) -> bool:
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
        return False

    def get_representation_id(self, element: ifcopenshell.entity_instance) -> Union[int, None]:
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
        return False


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

    print("# IFC Diff")

    start = time.time()
    print("Loading old file ...")
    old = ifcopenshell.open(args.old)
    print("Loading new file ...")
    new = ifcopenshell.open(args.new)

    print("# Loading finished in {:.2f} seconds".format(time.time() - start))
    start = time.time()

    ifc_diff = IfcDiff(old, new, args.relationships.split())
    ifc_diff.diff()

    print("# Diff finished in {:.2f} seconds".format(time.time() - start))

    ifc_diff.export(args.output)
