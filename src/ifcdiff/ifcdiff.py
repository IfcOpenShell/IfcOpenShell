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

import argparse
import hashlib
import json
import logging
import multiprocessing
import time
from typing import Any, Literal, Optional, Union

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.classification
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import numpy as np
from deepdiff import DeepDiff
from orderly_set import StableSet

__version__ = version = "0.0.0"


RELATIONSHIP_TYPE = Literal["geometry", "attributes", "type", "property", "container", "aggregate", "classification"]


class IfcDiff:
    """Main IfcDiff application

    If you are using IfcDiff as a library, this is the class you should use.

    :param old: IFC file object for the old model
    :param new: IFC file object for the new model
    :param relationships: List of relationships to check. None means that
        attributes and geometry are compared, so changes such as a modified or
        removed PredefinedType are reported. See RELATIONSHIP_TYPE for available
        relationships.
    :param is_shallow: True if you want only the first difference to be listed.
        False if you want all differences to be checked. Choosing False means
        that comparisons will take longer.
    :param filter_elements: An IFC filter query if you only want to compare a
        subset of elements. For example: ``IfcWall`` to only compare walls.
    :param match_by_signature: True to enable an opt-in fallback that re-pairs
        elements whose GlobalId changed between the two files (common with some
        authoring tools). Elements left in the added/deleted sets after the
        GlobalId comparison are matched on a content signature (same IFC class,
        Name, type, properties and materials) plus a placement within
        ``signature_tolerance``. This avoids reporting a re-GlobalId'd but
        otherwise identical element as a spurious delete + add. Default False
        preserves the historical GlobalId-only behaviour exactly.
    :param signature_tolerance: Placement tolerance (in the file's length unit)
        used when ``match_by_signature`` is enabled. Two candidate elements are
        considered to be in the same place if their placement origins are within
        this distance. Defaults to 0.05 (the reporter's +-5cm, assuming metres).

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
    # New GlobalId to {"old_global_id": ..., "moved": bool} for elements that
    # were re-paired across a GlobalId change by the signature fallback.
    rematched_elements: dict[str, dict[str, Any]]

    def __init__(
        self,
        old: ifcopenshell.file,
        new: ifcopenshell.file,
        relationships: Optional[list[RELATIONSHIP_TYPE]] = None,
        is_shallow: bool = True,
        filter_elements: Optional[str] = None,
        match_by_signature: bool = False,
        signature_tolerance: float = 0.05,
    ):
        self.old = old
        self.new = new
        self.change_register = {}
        self.rematched_elements = {}
        self.representation_ids = {}
        self.relationships = relationships or ["attributes", "geometry"]
        self.precision = 1e-4
        self.is_shallow = is_shallow
        self.filter_elements = filter_elements
        self.match_by_signature = match_by_signature
        self.signature_tolerance = signature_tolerance

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
        same_elements = old_elements & new_elements

        # Opt-in fallback: re-pair elements whose GlobalId changed but whose
        # content and placement still match, so that GlobalId churn is not
        # reported as spurious add + delete. This mutates added_elements /
        # deleted_elements and returns the (old, new) pairs to diff normally.
        rematched_pairs = self._match_by_signature() if self.match_by_signature else []

        print(" - {} item(s) were added".format(len(self.added_elements)))
        print(" - {} item(s) were deleted".format(len(self.deleted_elements)))
        print(" - {} item(s) are common to both models".format(len(same_elements)))
        if rematched_pairs:
            print(" - {} item(s) were re-matched across a GlobalId change".format(len(rematched_pairs)))

        element_pairs = [(self.old.by_id(g), self.new.by_id(g)) for g in same_elements]
        element_pairs += rematched_pairs
        total_same_elements = len(element_pairs)

        total_diffed = 0

        potential_old_changes = []
        potential_new_changes = []
        # Maps an old GlobalId to its paired new GlobalId for the geometry stage.
        # For GlobalId-matched elements this is the identity; for signature
        # rematches the two GlobalIds differ, so the shape dicts (each keyed by
        # their own file's GlobalId) must be paired through this map.
        geometry_pair_map: dict[str, str] = {}

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

        for old, new in element_pairs:
            total_diffed += 1
            if total_diffed % 250 == 0:
                print("{}/{} diffed ...".format(total_diffed, total_same_elements), end="\r", flush=True)
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
                    geometry_pair_map[old.GlobalId] = new.GlobalId
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
            for old_global_id, old_shape in old_shapes.items():
                new_global_id = geometry_pair_map.get(old_global_id, old_global_id)
                new_shape = new_shapes.get(new_global_id, None)
                if not new_shape:
                    self.change_register.setdefault(new_global_id, {}).update({"geometry_changed": True})
                    continue
                del new_shapes[new_global_id]
                diff = DeepDiff(old_shape, new_shape, math_epsilon=1e-5)
                if diff:
                    self.change_register.setdefault(new_global_id, {}).update({"geometry_changed": True})
                    continue

            for new_global_id in new_shapes.keys():
                self.change_register.setdefault(new_global_id, {}).update({"geometry_changed": True})

        print(" - {} item(s) were changed".format(len(self.change_register.keys())))

        logging.disable(logging.NOTSET)

    def _content_signature(self, element: ifcopenshell.entity_instance) -> str:
        """Stable content hash of an element ignoring GlobalId and OwnerHistory.

        Two elements sharing this signature have the same class, Name, type
        Name, property sets (excluding internal ids) and material Names. This is
        the "content hash" approach referenced by the maintainer; placement is
        handled separately so it can use a tolerance.
        """
        parts = [element.is_a(), element.Name or ""]
        try:
            element_type = ifcopenshell.util.element.get_type(element)
            parts.append((element_type.Name or "") if element_type else "")
        except Exception:
            parts.append("")
        try:
            psets = ifcopenshell.util.element.get_psets(element, should_inherit=False)
            cleaned = {name: {k: v for k, v in props.items() if k != "id"} for name, props in psets.items()}
            parts.append(json.dumps(cleaned, sort_keys=True, default=str))
        except Exception:
            parts.append("")
        try:
            materials = ifcopenshell.util.element.get_materials(element) or []
            parts.append(json.dumps(sorted((m.Name or "") for m in materials)))
        except Exception:
            parts.append("")
        return hashlib.sha1("\x00".join(parts).encode("utf-8")).hexdigest()

    def _placement_location(self, element: ifcopenshell.entity_instance) -> Optional[np.ndarray]:
        placement = getattr(element, "ObjectPlacement", None)
        if placement is None:
            return None
        try:
            return ifcopenshell.util.placement.get_local_placement(placement)[:3, 3]
        except Exception:
            return None

    def _location_key(self, location: Optional[np.ndarray]) -> Optional[tuple[int, ...]]:
        if location is None:
            return None
        tol = self.signature_tolerance or self.precision
        return tuple(int(round(float(c) / tol)) for c in location)

    def _match_by_signature(self) -> list[tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance]]:
        """Re-pair added/deleted elements whose GlobalId changed but content did not.

        Builds an index of the added elements keyed by their content signature
        (and a rounded placement bucket) so that each deleted element is matched
        in roughly constant time instead of scanning every added element. A pair
        with the same content within ``signature_tolerance`` is treated as
        unchanged; a pair with the same content but a different placement is
        treated as moved. Matched GlobalIds are removed from the added/deleted
        sets. Returns the (old, new) pairs so they still flow through the normal
        attribute/geometry/relationship diff.
        """
        added = list(self.added_elements)
        deleted = list(self.deleted_elements)
        if not added or not deleted:
            return []

        # Index added elements once (roughly O(n)).
        added_info: dict[str, tuple[str, Optional[np.ndarray]]] = {}
        strict_index: dict[tuple[str, Any], list[str]] = {}
        loose_index: dict[str, list[str]] = {}
        for guid in added:
            element = self.new.by_id(guid)
            sig = self._content_signature(element)
            loc = self._placement_location(element)
            added_info[guid] = (sig, loc)
            strict_index.setdefault((sig, self._location_key(loc)), []).append(guid)
            loose_index.setdefault(sig, []).append(guid)

        used_added: set[str] = set()
        pairs: list[tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance, bool]] = []

        # Pass 1: same content and same location within tolerance -> unchanged.
        # Search the target bucket and its 26 neighbours so that points near a
        # bucket boundary but still within tolerance are not missed.
        unmatched_deleted: list[tuple[str, str]] = []
        for guid in deleted:
            element = self.old.by_id(guid)
            sig = self._content_signature(element)
            loc = self._placement_location(element)
            match = None
            for neighbour in self._neighbour_keys(self._location_key(loc)):
                for cand in strict_index.get((sig, neighbour), []):
                    if cand in used_added:
                        continue
                    cand_loc = added_info[cand][1]
                    if loc is None or cand_loc is None or np.allclose(loc, cand_loc, atol=self.signature_tolerance):
                        match = cand
                        break
                if match is not None:
                    break
            if match is not None:
                used_added.add(match)
                pairs.append((element, self.new.by_id(match), False))
            else:
                unmatched_deleted.append((guid, sig))

        # Pass 2: same content, any location -> moved.
        for guid, sig in unmatched_deleted:
            match = None
            for cand in loose_index.get(sig, []):
                if cand in used_added:
                    continue
                match = cand
                break
            if match is not None:
                used_added.add(match)
                pairs.append((self.old.by_id(guid), self.new.by_id(match), True))

        result = []
        for old_element, new_element, moved in pairs:
            self.added_elements.discard(new_element.GlobalId)
            self.deleted_elements.discard(old_element.GlobalId)
            self.rematched_elements[new_element.GlobalId] = {
                "old_global_id": old_element.GlobalId,
                "moved": moved,
            }
            if moved:
                self.change_register.setdefault(new_element.GlobalId, {}).update({"moved": True})
            result.append((old_element, new_element))
        return result

    @staticmethod
    def _neighbour_keys(key: Optional[tuple[int, ...]]) -> list[Any]:
        if key is None:
            return [None]
        keys = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    keys.append((key[0] + dx, key[1] + dy, key[2] + dz))
        return keys

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
        if isinstance(obj, (StableSet, set)):
            return list(obj)
        return json.JSONEncoder.default(None, obj)

    def export(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as diff_file:
            json.dump(
                {
                    "added": list(self.added_elements),
                    "deleted": list(self.deleted_elements),
                    "changed": self.change_register,
                    "rematched": self.rematched_elements,
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
        help=(
            'A list of space-separated relationships, chosen from "attributes", "geometry", '
            '"type", "property", "container", "aggregate", "classification". '
            'Defaults to "attributes geometry" when omitted.'
        ),
        default="",
    )
    parser.add_argument(
        "-m",
        "--match-by-signature",
        action="store_true",
        help="Re-pair elements whose GlobalId changed but whose content and placement still match, "
        "instead of reporting them as add + delete (helps with GlobalId churn from some authoring tools)",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        type=float,
        default=0.05,
        help="Placement tolerance (in the file's length unit) for --match-by-signature. Defaults to 0.05",
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

    ifc_diff = IfcDiff(
        old,
        new,
        args.relationships.split(),
        match_by_signature=args.match_by_signature,
        signature_tolerance=args.tolerance,
    )
    ifc_diff.diff()

    print("# Diff finished in {:.2f} seconds".format(time.time() - start))

    ifc_diff.export(args.output)
