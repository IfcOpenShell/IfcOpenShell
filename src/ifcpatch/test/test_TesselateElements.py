# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.representation
import ifcpatch
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.profile
import ifcopenshell.api.root
import ifcopenshell.api.unit
import test.bootstrap
import ifcopenshell.geom
import ifcopenshell.util.element
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestTesselateElements(test.bootstrap.IFC4):
    def test_run(self):
        is_ifc2x3 = self.file.schema == "IFC2X3"
        ifcopenshell.api.root.create_entity(self.file, "IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, "IfcWall")
        model = ifcopenshell.api.context.add_context(self.file, "Model")
        body = ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )

        # Add a length unit just for tests.
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])

        builder = ShapeBuilder(self.file)
        rect = builder.polyline(builder.get_rectangle_coords(), closed=True)
        extrusion = builder.extrude(rect, 1.0)
        rep = builder.get_representation(body, extrusion)
        ifcopenshell.api.geometry.assign_representation(self.file, wall, rep)
        original_rep_id = rep.id()

        ifcpatch.execute({"file": self.file, "recipe": "TessellateElements", "arguments": ["IfcWall"]})

        # Original representation still exists.
        assert self.file.by_id(original_rep_id)

        other_reps = [r for r in ifcopenshell.util.representation.get_representations_iter(wall) if r != rep]
        assert len(other_reps) == 1
        new_rep = other_reps[0]
        new_rep.ContextOfItems = body
        new_rep.RepresentationIdentifier = "Body"
        new_rep.RepresentationType = "Tesselation"
        assert len(items := new_rep.Items) == 1
        item = items[0]
        if is_ifc2x3:
            assert item.is_a("IfcFacetedBrep")
            assert len(faces := item.Outer.CfsFaces) == 12
            for face in faces:
                assert len(face.Bounds[0].Bound.Polygon) == 3
        else:
            assert item.is_a("IfcPolygonalFaceSet")
            assert len(faces := item.Faces) == 12
            for face in faces:
                assert len(face.CoordIndex) == 3


class TestTesselateElementsIFC2X3(test.bootstrap.IFC2X3, TestTesselateElements):
    pass
