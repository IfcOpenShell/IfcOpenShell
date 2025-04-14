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

import ifcopenshell.util.unit
from typing import Optional, TypeVar

T = TypeVar("T")
COORD_3D = tuple[float, float, float]


def add_mesh_representation(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    vertices: list[list[COORD_3D]],
    edges: Optional[list[list[tuple[int, int]]]] = None,
    # Optional faces is not supported currently.
    faces: list[list[list[int]]] = None,
    coordinate_offset: Optional[COORD_3D] = None,
    unit_scale: Optional[float] = None,
    force_faceted_brep: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a mesh representation.

    Vertices, edges, and faces are given in the form of: ``[item1, item2, item3, ...]``.
    Each ``itemN`` is a sublist representing data for a separate IfcRepresentationItem to add.

    You can provide either ``edges`` or ``faces``, no need to provide both.
    But currently ``edges`` argument is not supported.

    :param context: The IfcGeometricRepresentationContext for the representation.
    :param vertices: A list of coordinates.
        where ``itemN = [(0., 0., 0.), (1., 1., 1.), (x, y, z), ...]``
    :param edges: A list of edges, represented by vertex index pairs
        where ``itemN = [(0, 1), (1, 2), (v1, v2), ...]``
    :param faces: A list of polygons, represented by vertex indices.
        where ``itemN = [(0, 1, 2), (5, 4, 2, 3), (v1, v2, v3, ... vN), ...]``
    :param coordinate_offset: Optionally apply a vector offset to all coordinates.
        In project units.
    :param unit_scale: Scale factor for ``vertices`` units.

        If omitted, it is assumed that ``vertices`` are in SI units.

        If other value is provided ``vertices`` coords will be divided by ``unit_scale``.
    :param force_faceted_brep: Force using IfcFacetedBreps instead of IfcPolygonalFaceSets.
    :return: IfcShapeRepresentation.
    """
    # TODO: Support edges without faces.
    assert faces is not None, f"Currently 'faces' argument is not optional."
    assert len(faces) != 0
    assert len(vertices) != 0
    assert len(faces) == len(vertices)

    usecase = Usecase()
    usecase.file = file
    if unit_scale is None:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    return usecase.execute(context, vertices, faces, cooridnate_offset, unit_scale, force_faceted_brep)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        context: ifcopenshell.entity_instance,
        vertices: list[list[COORD_3D]],
        faces: list[list[list[int]]],
        coordinate_offset: Optional[COORD_3D],
        unit_scale: float,
        force_faceted_brep: bool,
    ) -> ifcopenshell.entity_instance:
        self.vertices = vertices
        self.faces = faces
        self.context = context
        self.coordinate_offset = coordinate_offset
        self.unit_scale = unit_scale
        self.force_faceted_brep = force_faceted_brep
        return self.create_mesh_representation()

    def create_mesh_representation(self) -> ifcopenshell.entity_instance:
        if self.force_faceted_brep or self.file.schema == "IFC2X3":
            return self.create_faceted_brep()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self) -> ifcopenshell.entity_instance:
        items: list[ifcopenshell.entity_instance] = []
        for i in range(0, len(self.vertices)):
            vertices = [
                self.file.create_entity("IfcCartesianPoint", self.convert_si_to_unit(v)) for v in self.vertices[i]
            ]
            faces: list[ifcopenshell.entity_instance] = [
                self.file.create_entity(
                    "IfcFace",
                    [
                        self.file.create_entity(
                            "IfcFaceOuterBound",
                            self.file.create_entity("IfcPolyLoop", [vertices[v] for v in f]),
                            True,
                        )
                    ],
                )
                for f in self.faces[i]
            ]
            items.append(self.file.create_entity("IfcFacetedBrep", self.file.create_entity("IfcClosedShell", faces)))
        return self.file.create_entity(
            "IfcShapeRepresentation",
            self.context,
            self.context.ContextIdentifier,
            "Brep",
            items,
        )

    def create_polygonal_face_set(self) -> ifcopenshell.entity_instance:
        items: list[ifcopenshell.entity_instance] = []
        for i in range(0, len(self.vertices)):
            coordinates = self.file.create_entity(
                "IfcCartesianPointList3D", [self.convert_si_to_unit(v) for v in self.vertices[i]]
            )
            faces = [self.file.create_entity("IfcIndexedPolygonalFace", [v + 1 for v in f]) for f in self.faces[i]]
            items.append(self.file.create_entity("IfcPolygonalFaceSet", coordinates, None, faces))
        return self.file.create_entity(
            "IfcShapeRepresentation",
            self.context,
            self.context.ContextIdentifier,
            "Tessellation",
            items,
        )

    def convert_si_to_unit(self, co: T) -> T:
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        if self.coordinate_offset:
            return (co / self.unit_scale) + self.coordinate_offset
        return co / self.unit_scale
