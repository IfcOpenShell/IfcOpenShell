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
            "representation": None,
            "operator": "DIFFERENCE",
            # IfcHalfSpaceSolid, Mesh
            "type": "IfcHalfSpaceSolid",
            # The XY plane is the clipping boundary and +Z is removed.
            "matrix": None,  # A matrix to define a clipping Ifchalfspacesolid.
            "blender_obj": None,  # A Blender OBJ to define the voided OBJ for a "Mesh" type
            "blender_void": None,  # A Blender OBJ to define the void OBJ for a "Mesh" type
            "should_force_faceted_brep": False,
            "should_force_triangulation": False,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        self.settings["representation"].RepresentationType = "Clipping"
        if self.settings["type"] == "IfcHalfSpaceSolid":
            result = self.create_half_space_solid()
        elif self.settings["type"] == "Mesh":
            if self.settings["blender_obj"]:
                result = self.create_blender_mesh()
        items = []
        for item in self.settings["representation"].Items:
            items.append(self.file.createIfcBooleanResult(self.settings["operator"], item, result))
        self.settings["representation"].Items = items

    def create_half_space_solid(self):
        clipping = self.settings["matrix"]
        return self.file.createIfcHalfSpaceSolid(
            self.file.createIfcPlane(
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint(
                        (
                            self.convert_si_to_unit(clipping[0][3]),
                            self.convert_si_to_unit(clipping[1][3]),
                            self.convert_si_to_unit(clipping[2][3]),
                        )
                    ),
                    self.file.createIfcDirection((clipping[0][2], clipping[1][2], clipping[2][2])),
                    self.file.createIfcDirection((clipping[0][0], clipping[1][0], clipping[2][0])),
                )
            ),
            False,
        )

    def create_blender_mesh(self):
        self.ifc_vertices = []
        if self.file.schema == "IFC2X3" or self.settings["should_force_faceted_brep"]:
            return self.create_faceted_brep()
        if self.settings["should_force_triangulation"]:
            return self.create_triangulated_face_set()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self):
        self.create_vertices()
        faces = []
        for polygon in self.settings["blender_void"].data.polygons:
            faces.append(
                self.file.createIfcFace(
                    [
                        self.file.createIfcFaceOuterBound(
                            self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                            True,
                        )
                    ]
                )
            )
        # TODO: May not actually be a closed shell, but who checks anyway?
        return self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(faces))

    def create_triangulated_face_set(self):
        faces = []
        for polygon in self.settings["blender_void"].data.polygons:
            faces.append([v + 1 for v in polygon.vertices])

        mat1 = self.settings["blender_void"].matrix_world
        mat2 = self.settings["blender_obj"].matrix_world.inverted()
        coordinates = self.file.createIfcCartesianPointList3D(
            [self.convert_si_to_unit(mat2 @ mat1 @ v.co) for v in self.settings["blender_void"].data.vertices]
        )
        return self.file.createIfcTriangulatedFaceSet(coordinates, None, None, faces)

    def create_polygonal_face_set(self):
        faces = []
        for polygon in self.settings["blender_void"].data.polygons:
            faces.append(self.file.createIfcIndexedPolygonalFace([v + 1 for v in polygon.vertices]))
        mat1 = self.settings["blender_void"].matrix_world
        mat2 = self.settings["blender_obj"].matrix_world.inverted()
        coordinates = self.file.createIfcCartesianPointList3D(
            [self.convert_si_to_unit(mat2 @ mat1 @ v.co) for v in self.settings["blender_void"].data.vertices]
        )
        return self.file.createIfcPolygonalFaceSet(coordinates, None, faces)

    def create_vertices(self):
        mat1 = self.settings["blender_void"].matrix_world
        mat2 = self.settings["blender_obj"].matrix_world.inverted()
        self.ifc_vertices.extend(
            [
                self.file.createIfcCartesianPoint(self.convert_si_to_unit(mat2 @ mat1 @ v.co))
                for v in self.settings["blender_void"].data.vertices
            ]
        )

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
