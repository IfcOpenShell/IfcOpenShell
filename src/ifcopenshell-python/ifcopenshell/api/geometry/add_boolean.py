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

from __future__ import annotations
import ifcopenshell.util.unit
import numpy as np
import numpy.typing as npt
from typing import Optional, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import bpy.types


NPArrayOfFloats = npt.NDArray[np.float64]


def add_boolean(
    file: ifcopenshell.file,
    representation: ifcopenshell.entity_instance,
    # A matrix to define a clipping Ifchalfspacesolid.
    # The XY plane is the clipping boundary and +Z is removed.
    operator: str = "DIFFERENCE",
    # IfcHalfSpaceSolid, Mesh
    type: Literal["IfcHalfSpaceSolid", "Mesh"] = "IfcHalfSpaceSolid",
    matrix: Optional[NPArrayOfFloats] = None,
    # A Blender OBJ to define the voided OBJ for a "Mesh" type
    blender_obj: Optional[bpy.types.Object] = None,
    # A Blender OBJ to define the void OBJ for a "Mesh" type
    blender_void: Optional[bpy.types.Object] = None,
    should_force_faceted_brep: bool = False,
    should_force_triangulation: bool = False,
) -> list[ifcopenshell.entity_instance]:
    """For `type` values:
    - "IfcHalfSpaceSolid" - `matrix` is not optional.
    - "Mesh" - `blender_obj` and `blender_void` are not optional
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "representation": representation,
        "operator": operator,
        "type": type,
        "matrix": matrix,
        "blender_obj": blender_obj,
        "blender_void": blender_void,
        "should_force_faceted_brep": should_force_faceted_brep,
        "should_force_triangulation": should_force_triangulation,
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        if self.settings["type"] == "IfcHalfSpaceSolid":
            result = self.create_half_space_solid()
        elif self.settings["type"] == "Mesh":
            if self.settings["blender_obj"]:
                result = self.create_blender_mesh()
        items = []
        for item in self.settings["representation"].Items:
            if (
                self.settings["operator"] == "DIFFERENCE"
                and result.is_a("IfcHalfSpaceSolid")
                and (
                    item.is_a("IfcSweptAreaSolid")
                    or item.is_a("IfcSweptDiskSolid")
                    or item.is_a("IfcBooleanClippingResult")
                )
            ):
                items.append(self.file.createIfcBooleanClippingResult(self.settings["operator"], item, result))
                representation_type = "Clipping"
            else:
                items.append(self.file.createIfcBooleanResult(self.settings["operator"], item, result))
                representation_type = "CSG"
        self.settings["representation"].RepresentationType = representation_type
        self.settings["representation"].Items = items
        return items

    def create_half_space_solid(self):
        clipping = np.array(self.settings["matrix"])[:3]
        local_z = self.file.createIfcDirection(clipping[:, 2].tolist())
        local_x = self.file.createIfcDirection(clipping[:, 0].tolist())
        point = self.file.createIfcCartesianPoint(self.convert_si_to_unit(clipping[:, 3]).tolist())
        placement = self.file.createIfcAxis2Placement3D(point, local_z, local_x)
        plane = self.file.createIfcPlane(placement)
        return self.file.createIfcHalfSpaceSolid(plane, AgreementFlag=False)

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
