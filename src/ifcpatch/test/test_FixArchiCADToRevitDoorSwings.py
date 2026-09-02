# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bonsai Contributors
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
#
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.spatial

import ifcpatch
import test.bootstrap


class TestFixArchiCADToRevitDoorSwings(test.bootstrap.IFC4):
    def _add_contexts(self):
        model_ctx = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
        )
        plan_ctx = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        footprint_ctx = ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="FootPrint",
            target_view="MODEL_VIEW",
            parent=plan_ctx,
        )
        return body_ctx, footprint_ctx

    def _make_footprint_representation(self, context):
        # IfcPolyline is used (rather than IfcIndexedPolyCurve) because it is
        # available in both IFC2X3 and IFC4, unlike IfcIndexedPolyCurve which
        # is IFC4-only.
        points = [
            self.file.create_entity("IfcCartesianPoint", Coordinates=c)
            for c in [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
        ]
        curve = self.file.create_entity("IfcPolyline", Points=points)
        return self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=[curve],
        )

    def test_door_with_footprint_representation_is_split_into_a_3d_accessory(self):
        """The core behaviour: a door's 2D FootPrint swing is moved onto a
        copied IfcDiscreteAccessory whose representation is reassigned to the
        Body context, while the original door keeps only its remaining
        representations."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        body_ctx, footprint_ctx = self._add_contexts()

        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        footprint_rep = self._make_footprint_representation(footprint_ctx)
        door.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[footprint_rep])
        ifcopenshell.api.spatial.assign_container(self.file, products=[door], relating_structure=storey)

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})

        assert not any(r.RepresentationIdentifier == "FootPrint" for r in door.Representation.Representations)

        accessories = self.file.by_type("IfcDiscreteAccessory")
        assert len(accessories) == 1
        accessory = accessories[0]
        assert accessory.GlobalId != door.GlobalId
        body_reps = list(accessory.Representation.Representations)
        assert len(body_reps) == 1
        assert body_reps[0].RepresentationIdentifier == "Body"
        assert body_reps[0].RepresentationType == "Curve3D"
        assert body_reps[0].ContextOfItems == body_ctx

        assert accessory in door.ContainedInStructure[0].RelatedElements

    def test_wall_axis_representation_is_removed(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        body_ctx, _ = self._add_contexts()

        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        axis_curve = self.file.create_entity(
            "IfcPolyline",
            Points=[
                self.file.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0)),
                self.file.create_entity("IfcCartesianPoint", (1.0, 0.0, 0.0)),
            ],
        )
        axis_rep = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=[axis_curve],
        )
        body_rep = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Body",
            RepresentationType="Curve3D",
            Items=[],
        )
        wall.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[axis_rep, body_rep])

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})

        remaining = [r.RepresentationIdentifier for r in wall.Representation.Representations]
        assert remaining == ["Body"]

    def test_wall_with_no_representation_is_skipped_with_a_warning(self):
        """A wall created without geometry (e.g. via the authoring API before
        it is given a shape) has ``Representation is None``. IfcProduct.
        Representation is an OPTIONAL attribute in both IFC2X3 and IFC4, so
        this is a legitimate, reachable state and must not crash the patch
        for the rest of the model."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert wall.Representation is None

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})
        assert self.file.by_type("IfcWall")[0].GlobalId == wall.GlobalId

    def test_door_with_no_representation_is_skipped_with_a_warning(self):
        """Same reasoning as the wall case: IfcDoor.Representation is
        optional, and a door authored without geometry yet must not abort
        the whole patch run."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        assert door.Representation is None

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})
        assert self.file.by_type("IfcDoor")[0].GlobalId == door.GlobalId

    def test_door_with_footprint_but_no_spatial_container_is_skipped_with_a_warning(self):
        """IfcElement.ContainedInStructure is an inverse attribute with
        cardinality S[0:1]: it can legitimately be empty for an orphaned
        element that was never placed in a spatial structure. Without this
        guard the recipe would crash with an IndexError after already
        having split the door's representations, leaving the file half
        patched."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        _, footprint_ctx = self._add_contexts()

        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        footprint_rep = self._make_footprint_representation(footprint_ctx)
        door.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[footprint_rep])
        assert door.ContainedInStructure == ()

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})

        # The door must be left untouched: no accessory copy, footprint kept.
        assert not self.file.by_type("IfcDiscreteAccessory")
        assert any(r.RepresentationIdentifier == "FootPrint" for r in door.Representation.Representations)

    def test_door_without_footprint_representation_is_left_untouched(self):
        """A door with only a Body representation (no ArchiCAD 2D FootPrint
        swing) has nothing to split and must be silently skipped, not
        warned about: this is the normal case for the vast majority of
        doors, not a defect in the input file."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        body_ctx, _ = self._add_contexts()

        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        body_rep = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body_ctx,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[],
        )
        door.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[body_rep])

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})

        assert not self.file.by_type("IfcDiscreteAccessory")
        assert list(door.Representation.Representations) == [body_rep]

    def test_door_type_footprint_representation_map_is_removed(self):
        """The door type entity (``IfcDoorType`` in IFC4, ``IfcDoorStyle`` in
        IFC2X3) has its FootPrint representation map culled, leaving other
        maps untouched."""
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        body_ctx, footprint_ctx = self._add_contexts()

        door_type_class = "IfcDoorStyle" if self.file.schema == "IFC2X3" else "IfcDoorType"
        door_type = ifcopenshell.api.root.create_entity(self.file, ifc_class=door_type_class)

        def make_map(context, identifier, rep_type):
            rep = self.file.create_entity(
                "IfcShapeRepresentation",
                ContextOfItems=context,
                RepresentationIdentifier=identifier,
                RepresentationType=rep_type,
                Items=[],
            )
            origin = self.file.create_entity(
                "IfcAxis2Placement3D", Location=self.file.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0))
            )
            return self.file.create_entity("IfcRepresentationMap", MappingOrigin=origin, MappedRepresentation=rep)

        footprint_map = make_map(footprint_ctx, "FootPrint", "Curve2D")
        body_map = make_map(body_ctx, "Body", "SweptSolid")
        door_type.RepresentationMaps = [footprint_map, body_map]

        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitDoorSwings", "arguments": []})

        remaining = [rm.MappedRepresentation.RepresentationIdentifier for rm in door_type.RepresentationMaps]
        assert remaining == ["Body"]


class TestFixArchiCADToRevitDoorSwingsIFC2X3(test.bootstrap.IFC2X3, TestFixArchiCADToRevitDoorSwings):
    """IFC2X3 has no ``IfcIndexedPolyCurve``/``IfcArcIndex`` (the arc-index
    faceting section is simply not applicable, same as
    ``DowngradeIndexedPolyCurve.py``) and no ``IfcDoorType`` (the door type
    entity is named ``IfcDoorStyle`` there instead, handled by
    ``test_door_type_footprint_representation_map_is_removed`` above, which
    is inherited and re-run against this schema). Every other test in the
    base class exercises ``IfcWall``/``IfcDoor``/``IfcDiscreteAccessory``,
    which are unchanged between schemas, so they are inherited unmodified."""
