# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.boundary as subject
import ifcopenshell.util.shape
import test.bootstrap


def _add_extruded_body(ifc_file, element, coords_2d, depth, z_offset=0.0):
    """Add a body representation (extruded polyline) to an element."""
    if not ifc_file.by_type("IfcProject"):
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    ctx = ifc_file.createIfcGeometricRepresentationContext(
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-5,
        WorldCoordinateSystem=ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
            ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
        ),
    )
    sub_ctx = ifc_file.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=ctx,
        TargetView="MODEL_VIEW",
    )
    pts = [ifc_file.createIfcCartesianPoint((float(x), float(y))) for x, y in coords_2d]
    polyline = ifc_file.createIfcPolyline(pts)
    profile = ifc_file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="CURVE", OuterCurve=polyline)
    placement = ifc_file.createIfcAxis2Placement3D(
        ifc_file.createIfcCartesianPoint((0.0, 0.0, z_offset)),
        ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
        ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
    )
    direction = ifc_file.createIfcDirection((0.0, 0.0, 1.0))
    solid = ifc_file.createIfcExtrudedAreaSolid(profile, placement, direction, depth)
    rep = ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=sub_ctx,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=rep)


def _build_shapes_dict(ifc_file, elements):
    """Build a shapes dict as expected by ifcopenshell.util.boundary."""
    settings = ifcopenshell.geom.settings()
    settings.set("disable-opening-subtractions", True)
    shapes = {}
    for element in elements:
        shape = ifcopenshell.geom.create_shape(settings, element)
        shapes[element.id()] = {
            "verts": ifcopenshell.util.shape.get_vertices(shape.geometry),
            "faces": ifcopenshell.util.shape.get_faces(shape.geometry),
            "edges": ifcopenshell.util.shape.get_edges(shape.geometry),
            "matrix": ifcopenshell.util.shape.get_shape_matrix(shape),
        }
    return shapes


class TestAutoGenerateBoundaries(test.bootstrap.IFC4):
    def test_no_building_elements_returns_error(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        _add_extruded_body(self.file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        shapes = _build_shapes_dict(self.file, [space])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary")
        assert isinstance(result, str)
        assert "No building elements" in result

    def test_space_not_in_shapes_returns_error(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        result = subject.auto_generate_boundaries(self.file, space, {}, "IfcRelSpaceBoundary")
        assert isinstance(result, str)
        assert "not found" in result.lower()

    def test_generates_boundary_for_adjacent_wall(self):
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        _add_extruded_body(self.file, space, [[-5, -5], [5, -5], [5, 5], [-5, 5]], 3.0)
        _add_extruded_body(self.file, wall, [[-5, 5], [5, 5], [5, 5.2], [-5, 5.2]], 3.0)
        shapes = _build_shapes_dict(self.file, [space, wall])
        result = subject.auto_generate_boundaries(self.file, space, shapes, "IfcRelSpaceBoundary")
        assert isinstance(result, list)
        assert len(result) >= 1
        boundary = result[0]
        assert boundary.RelatingSpace == space
        assert boundary.RelatedBuildingElement == wall
        assert boundary.PhysicalOrVirtualBoundary == "PHYSICAL"
