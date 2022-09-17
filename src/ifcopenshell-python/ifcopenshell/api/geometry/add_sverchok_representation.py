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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            # Vertices, edges, and faces are given in the form of: [item1, item2, item3, ...]
            # ... where itemN = [(0., 0., 0.), (1., 1., 1.), (x, y, z), ...]
            "vertices": None,  # A list of coordinates
            # ... where itemN = [(0, 1), (1, 2), (v1, v2), ...]
            "edges": None,  # A list of edges, represented by vertex index pairs
            # ... where itemN = [(0, 1, 2), (5, 4, 2, 3), (v1, v2, v3, ... vN), ...]
            "faces": None,  # A list of polygons, represented by vertex indices
            "coordinate_offset": None,  # Optionally apply a vector offset to all coordinates
            "unit_scale": None,  # A scale factor to apply for all vectors in case the unit is different
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["unit_scale"] is None:
            self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        return self.create_mesh_representation()

    def create_mesh_representation(self):
        if self.file.schema == "IFC2X3":
            return self.create_faceted_brep()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self):
        items = []
        for i in range(0, len(self.settings["vertices"])):
            vertices = [
                self.file.createIfcCartesianPoint(self.convert_si_to_unit(v)) for v in self.settings["vertices"][i]
            ]
            faces = [
                self.file.createIfcFace(
                    [self.file.createIfcFaceOuterBound(self.file.createIfcPolyLoop([vertices[v] for v in f]), True)]
                )
                for f in self.settings["faces"][i]
            ]
            items.append(self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(faces)))
        return self.file.createIfcShapeRepresentation(
            self.settings["context"], self.settings["context"].ContextIdentifier, "Brep", items
        )

    def create_polygonal_face_set(self):
        items = []
        for i in range(0, len(self.settings["vertices"])):
            coordinates = self.file.createIfcCartesianPointList3D(
                [self.convert_si_to_unit(v) for v in self.settings["vertices"][i]]
            )
            faces = [self.file.createIfcIndexedPolygonalFace([v + 1 for v in f]) for f in self.settings["faces"][i]]
            items.append(self.file.createIfcPolygonalFaceSet(coordinates, None, faces))
        return self.file.createIfcShapeRepresentation(
            self.settings["context"], self.settings["context"].ContextIdentifier, "Tessellation", items
        )

    def convert_si_to_unit(self, co):
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        if self.settings["coordinate_offset"]:
            return (co / self.settings["unit_scale"]) + self.settings["coordinate_offset"]
        return co / self.settings["unit_scale"]
