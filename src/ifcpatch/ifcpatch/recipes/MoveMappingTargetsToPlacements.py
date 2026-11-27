# IfcPatch - IFC patching utiliy
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import logging
from typing import Union

import ifcopenshell
import ifcopenshell.util.placement
import numpy as np


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: Union[logging.Logger, None] = None):
        """Move the MappingTarget of mapped items into the object placement

        Some exporters (for example SketchUp) place every occurrence of a type
        through the MappingTarget of an IfcMappedItem, with all occurrences
        sharing one object placement. The geometry iterator only reuses the
        geometry of an IfcRepresentationMap when the MappingTarget is the
        identity, so every occurrence is tessellated on its own and viewers
        such as Bonsai create one mesh per occurrence.

        This patch moves each MappingTarget into a new IfcLocalPlacement of
        its product and sets the MappingTarget to the identity. The geometry
        stays exactly where it was, and occurrences of the same map then share
        one mesh.

        A product is changed only when one of its representations holds a
        single IfcMappedItem, none of its representations are used by another
        product, the map origin is the identity and the target is a rotation
        and translation (no scale, no mirror). Its other representations may
        only hold curves (such as an Axis): those are moved into a shared
        IfcRepresentationMap and mapped back with the inverse target, so they
        stay where they were too. Targets left unused are removed. Products
        that are skipped are counted in the log.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "MoveMappingTargetsToPlacements", "arguments": []})
        """
        self.file = file
        self.logger = logger or logging.getLogger("ifcpatch")

    def patch(self) -> None:
        self.directions = {}
        self.curve_maps = {}
        self.identity = None
        old_targets = set()
        count = dict.fromkeys(
            (
                "moved",
                "already identity",
                "other representations",
                "shared representation",
                "map origin not identity",
                "scaled or mirrored target",
                "curve representations mapped",
            ),
            0,
        )

        for product in self.file.by_type("IfcProduct"):
            placement = product.ObjectPlacement
            if not product.Representation or not placement or not placement.is_a("IfcLocalPlacement"):
                continue
            reps = product.Representation.Representations
            if not (mapped := [r for r in reps if any(i.is_a("IfcMappedItem") for i in r.Items)]):
                continue
            others = [r for r in reps if r not in mapped]
            if len(mapped) != 1 or len(mapped[0].Items) != 1 or not all(self.has_only_curves(r) for r in others):
                count["other representations"] += 1
                continue
            if any(len(self.file.get_inverse(r)) > 1 for r in others) or len(self.get_products(mapped[0])) > 1:
                count["shared representation"] += 1
                continue
            item = mapped[0].Items[0]
            if not np.allclose(ifcopenshell.util.placement.get_placement(item.MappingSource.MappingOrigin), np.eye(4)):
                count["map origin not identity"] += 1
                continue
            target = ifcopenshell.util.placement.get_placement(item.MappingTarget)
            rotation = target[:3, :3]
            if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-9) or np.linalg.det(rotation) < 0:
                count["scaled or mirrored target"] += 1
                continue
            if np.allclose(target, np.eye(4)):
                count["already identity"] += 1
                continue

            parent = placement.PlacementRelTo
            local = ifcopenshell.util.placement.get_placement(placement) @ target
            if parent:
                local = np.linalg.inv(ifcopenshell.util.placement.get_placement(parent)) @ local
            product.ObjectPlacement = self.file.createIfcLocalPlacement(
                parent, self.create_axis2placement(local, item.MappingTarget.LocalOrigin)
            )
            inverse = np.linalg.inv(target)
            for rep in others:
                self.map_curves(rep, inverse)
                count["curve representations mapped"] += 1
            old_targets.add(item.MappingTarget)
            item.MappingTarget = self.get_identity_operator()
            count["moved"] += 1

        for target in old_targets:
            self.remove_if_unused(target)
        for key, value in count.items():
            self.logger.info(f"{key}: {value}")

    def has_only_curves(self, rep: ifcopenshell.entity_instance) -> bool:
        return all(i.is_a("IfcPolyline") or i.is_a("IfcIndexedPolyCurve") for i in rep.Items)

    def get_products(self, rep: ifcopenshell.entity_instance) -> set[int]:
        return {
            p.id()
            for definition in rep.OfProductRepresentation
            for p in self.file.get_inverse(definition)
            if p.is_a("IfcProduct")
        }

    def get_direction(self, vector) -> ifcopenshell.entity_instance:
        key = tuple(round(float(v), 12) for v in vector)
        if key not in self.directions:
            self.directions[key] = self.file.createIfcDirection([float(v) for v in vector])
        return self.directions[key]

    def create_axis2placement(self, matrix, reuse_point=None) -> ifcopenshell.entity_instance:
        origin = [float(v) for v in matrix[:3, 3]]
        if reuse_point is not None and np.allclose(reuse_point.Coordinates, origin, atol=1e-12):
            point = reuse_point
        else:
            point = self.file.createIfcCartesianPoint(origin)
        if np.allclose(matrix[:3, :3], np.eye(3), atol=1e-12):
            return self.file.createIfcAxis2Placement3D(point, None, None)
        return self.file.createIfcAxis2Placement3D(
            point, self.get_direction(matrix[:3, 2]), self.get_direction(matrix[:3, 0])
        )

    def create_operator(self, matrix) -> ifcopenshell.entity_instance:
        origin = self.file.createIfcCartesianPoint([float(v) for v in matrix[:3, 3]])
        if np.allclose(matrix[:3, :3], np.eye(3), atol=1e-12):
            return self.file.createIfcCartesianTransformationOperator3D(None, None, origin, 1.0, None)
        x, y, z = (self.get_direction(matrix[:3, i]) for i in range(3))
        return self.file.createIfcCartesianTransformationOperator3D(x, y, origin, 1.0, z)

    def get_identity_operator(self) -> ifcopenshell.entity_instance:
        if self.identity is None:
            self.identity = self.create_operator(np.eye(4))
        return self.identity

    def map_curves(self, rep: ifcopenshell.entity_instance, inverse) -> None:
        # Share each distinct set of curves once, placed back with the inverse target.
        key = (rep.ContextOfItems.id(), rep.RepresentationIdentifier, tuple(i.id() for i in rep.Items))
        if key not in self.curve_maps:
            source = self.file.createIfcShapeRepresentation(
                rep.ContextOfItems, rep.RepresentationIdentifier, rep.RepresentationType, rep.Items
            )
            origin = self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)))
            self.curve_maps[key] = self.file.createIfcRepresentationMap(origin, source)
        rep.Items = [self.file.createIfcMappedItem(self.curve_maps[key], self.create_operator(inverse))]
        rep.RepresentationType = "MappedRepresentation"

    def remove_if_unused(self, element: ifcopenshell.entity_instance) -> None:
        if self.file.get_total_inverses(element):
            return
        children = [
            a for a in element.get_info(recursive=False).values() if isinstance(a, ifcopenshell.entity_instance)
        ]
        self.file.remove(element)
        for child in children:
            self.remove_if_unused(child)
