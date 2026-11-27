# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.placement
import numpy as np

import ifcpatch
import test.bootstrap


class TestMoveMappingTargetsToPlacements(test.bootstrap.IFC4):
    def make_model(self):
        f = self.file
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(f)
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        self.shared_placement = f.createIfcLocalPlacement(
            f.createIfcLocalPlacement(None, self.a2p((5.0, 7.0, 1.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))),
            self.a2p((1.0, 2.0, 3.0)),
        )
        maps = [self.create_map(size) for size in (0.5, 0.8)]
        shared_curve = self.create_curve()
        self.products = {}
        for i in range(6):
            self.products[f"translated {i}"] = self.create_product(maps[i % 2], self.operator((float(i), 2.0, 0.0)))
        rotated = self.operator((3.0, 1.0, 0.5), axis1=(0.0, 1.0, 0.0), axis2=(-1.0, 0.0, 0.0), axis3=(0.0, 0.0, 1.0))
        self.products["rotated"] = self.create_product(maps[0], rotated)
        for i in range(2):
            self.products[f"with axis {i}"] = self.create_product(
                maps[1], self.operator((float(i), 9.0, 0.0)), axis=shared_curve
            )
        self.products["scaled"] = self.create_product(maps[0], self.operator((0.0, 5.0, 0.0), scale=2.0))
        mirrored = self.operator((0.0, 6.0, 0.0), axis1=(-1.0, 0.0, 0.0), axis2=(0.0, 1.0, 0.0), axis3=(0.0, 0.0, 1.0))
        self.products["mirrored"] = self.create_product(maps[0], mirrored)

    def a2p(self, origin, z=None, x=None):
        f = self.file
        return f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint(origin),
            f.createIfcDirection(z) if z else None,
            f.createIfcDirection(x) if x else None,
        )

    def operator(self, origin, axis1=None, axis2=None, axis3=None, scale=1.0):
        f = self.file
        d = lambda v: f.createIfcDirection(v) if v else None
        return f.createIfcCartesianTransformationOperator3D(
            d(axis1), d(axis2), f.createIfcCartesianPoint(origin), scale, d(axis3)
        )

    def create_map(self, s):
        f = self.file
        corners = [(0, 0, 0), (s, 0, 0), (s, s, 0), (0, s, 0), (0, 0, s), (s, 0, s), (s, s, s), (0, s, s)]
        points = [f.createIfcCartesianPoint([float(c) for c in corner]) for corner in corners]
        loops = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        faces = [
            f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([points[i] for i in loop]), True)])
            for loop in loops
        ]
        brep = f.createIfcFacetedBrep(f.createIfcClosedShell(faces))
        rep = f.createIfcShapeRepresentation(self.body, "Body", "Brep", [brep])
        return f.createIfcRepresentationMap(self.a2p((0.0, 0.0, 0.0)), rep)

    def create_curve(self):
        f = self.file
        return f.createIfcPolyline(
            [f.createIfcCartesianPoint((0.0, 0.0, 0.0)), f.createIfcCartesianPoint((0.3, 0.1, 0.2))]
        )

    def create_product(self, rmap, target, axis=None):
        f = self.file
        reps = [
            f.createIfcShapeRepresentation(
                self.body, "Body", "MappedRepresentation", [f.createIfcMappedItem(rmap, target)]
            )
        ]
        if axis:
            reps.append(f.createIfcShapeRepresentation(self.body, "Axis", "Curve3D", [axis]))
        return f.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(),
            None,
            None,
            None,
            None,
            self.shared_placement,
            f.createIfcProductDefinitionShape(None, None, reps),
        )

    def world_points(self, product):
        out = {}
        placement = ifcopenshell.util.placement.get_placement(product.ObjectPlacement)
        for rep in product.Representation.Representations:
            out[rep.RepresentationIdentifier] = np.round(np.array(self.item_points(rep.Items, placement))[:, :3], 9)
        return out

    def item_points(self, items, matrix):
        points = []
        for item in items:
            if item.is_a("IfcMappedItem"):
                inner = matrix @ ifcopenshell.util.placement.get_mappeditem_transformation(item)
                points.extend(self.item_points(item.MappingSource.MappedRepresentation.Items, inner))
            elif item.is_a("IfcPolyline"):
                points.extend(matrix @ np.array([*p.Coordinates, 1.0]) for p in item.Points)
            elif item.is_a("IfcFacetedBrep"):
                for face in item.Outer.CfsFaces:
                    points.extend(matrix @ np.array([*p.Coordinates, 1.0]) for p in face.Bounds[0].Bound.Polygon)
        return points

    def count_geometry_ids(self):
        iterator = ifcopenshell.geom.iterator(ifcopenshell.geom.settings(), self.file)
        ids = set()
        assert iterator.initialize()
        while True:
            ids.add(iterator.get().geometry.id)
            if not iterator.next():
                return len(ids)

    def test_run(self):
        self.make_model()
        before = {name: self.world_points(p) for name, p in self.products.items()}
        old_targets = {
            name: p.Representation.Representations[0].Items[0].MappingTarget.id() for name, p in self.products.items()
        }
        assert self.count_geometry_ids() == len(self.products)

        ifcpatch.execute({"file": self.file, "recipe": "MoveMappingTargetsToPlacements", "arguments": []})

        for name, product in self.products.items():
            after = self.world_points(product)
            assert after.keys() == before[name].keys()
            for identifier in after:
                assert np.allclose(after[identifier], before[name][identifier]), (name, identifier)

        for name, product in self.products.items():
            item = product.Representation.Representations[0].Items[0]
            target = ifcopenshell.util.placement.get_placement(item.MappingTarget)
            if name in ("scaled", "mirrored"):
                assert item.MappingTarget.id() == old_targets[name]
                assert product.ObjectPlacement == self.shared_placement
            else:
                assert np.allclose(target, np.eye(4))
                assert product.ObjectPlacement != self.shared_placement
                assert product.ObjectPlacement.PlacementRelTo == self.shared_placement.PlacementRelTo

        moved = [old_targets[n] for n in self.products if n not in ("scaled", "mirrored")]
        existing = {e.id() for e in self.file.by_type("IfcCartesianTransformationOperator3D")}
        assert not existing & set(moved)

        axis_items = [
            next(
                r
                for r in self.products[f"with axis {i}"].Representation.Representations
                if r.RepresentationIdentifier == "Axis"
            ).Items
            for i in range(2)
        ]
        assert all(len(items) == 1 and items[0].is_a("IfcMappedItem") for items in axis_items)
        assert axis_items[0][0].MappingSource == axis_items[1][0].MappingSource

        maps_shared_by_moved_products, skipped_products = 2, 2
        assert self.count_geometry_ids() == maps_shared_by_moved_products + skipped_products


class TestMoveMappingTargetsToPlacementsIFC2X3(test.bootstrap.IFC2X3, TestMoveMappingTargetsToPlacements):
    pass
