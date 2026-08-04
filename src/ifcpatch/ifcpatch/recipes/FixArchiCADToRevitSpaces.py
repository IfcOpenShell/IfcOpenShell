# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import logging
from typing import TypeVar, Union

import numpy as np
import numpy.typing as npt
import shapely
import shapely.ops
from shapely.geometry.polygon import orient

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import ShapeBuilder

import ifcpatch

T = TypeVar("T", float, npt.NDArray[np.float64])


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Union[logging.Logger, None] = None):
        """Allow ArchiCAD IFC spaces to open as Revit rooms

        The underlying problem is that Revit does not bring in IFC spaces as
        spaces / rooms in Revit when you link an IFC in Revit. This has been
        broken for at least 3 years and counting. This is a problem typically
        for ArchiCAD architects who want to send rooms to MEP folks using
        Revit.

        See bug: https://github.com/Autodesk/revit-ifc/issues/15

        The solution is to open an IFC in Revit instead of linking it, which
        will convert IFC spaces into Revit rooms. However, there are very
        specific scenarios where Revit will convert these rooms, which have
        been painstakingly reverse engineered through trial and error.
        Firstly, the rooms should have a lower bound with a Z value matching
        the Z value of the storey it is on. Secondly, although faceted breps
        do work in some scenarios (I assume Revit has an internal topological
        analysis tool), conversion to an extruded area solid yield much more
        robust results. Finally, changing the Precision value to an obscene
        number very strangely seems to cause a lot more rooms to be converted
        successfully.

        This patch is designed to only work on ArchiCAD IFC exports where the
        only contents of the IFC is IFC space and `nothing else`.

        Example:

        .. code:: python

            ifcpatch.execute({"file": model, "recipe": "FixArchiCADToRevitSpaces", "arguments": []})
        """
        super().__init__(file, logger)
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
        self.builder = ShapeBuilder(file)
        # Triangulated coplanar faces are riddled with collinear vertices. A
        # micron is small enough to only cull those, but large enough to
        # survive floating point noise from the mesher.
        self.tolerance = 1e-6

    def patch(self) -> None:
        settings = ifcopenshell.geom.settings()

        for space in self.file.by_type("IfcSpace"):
            body = ifcopenshell.util.representation.get_representation(space, "Model", "Body")
            if body is None:
                self.logger.warning(f"Space {space.GlobalId} has no body representation and was not patched.")
                continue

            storey_elevation = self.get_storey_elevation(space)
            if storey_elevation is None:
                self.logger.warning(f"Space {space.GlobalId} is not on a storey and was not patched.")
                continue

            try:
                shape = ifcopenshell.geom.create_shape(settings, space)
            except RuntimeError:
                self.logger.warning(f"Space {space.GlobalId} geometry could not be processed and was not patched.")
                continue

            # Geometry is in SI units, local to the space's own placement.
            matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
            vertices = ifcopenshell.util.shape.get_vertices(shape.geometry)
            faces = ifcopenshell.util.shape.get_faces(shape.geometry)

            # Revit only converts spaces into rooms if the lower bound sits at
            # the elevation of its storey, so instead of extruding from the
            # bottom of the space we extrude from the storey.
            base_z = (np.linalg.inv(matrix) @ np.array((0.0, 0.0, storey_elevation, 1.0)))[2]
            top_z, bottom_z = vertices[:, 2].max(), vertices[:, 2].min()
            depth = top_z - base_z
            if depth <= self.tolerance:
                # The storey can sit at or above the top of the space, typically
                # when the space is assigned to the wrong storey. Keeping the
                # space's own height is better than losing its geometry.
                depth = top_z - bottom_z
            if depth <= self.tolerance:
                self.logger.warning(f"Space {space.GlobalId} is flat and was not patched.")
                continue

            extrusions = [
                self.create_extrusion(polygon, base_z, depth) for polygon in self.get_footprints(vertices, faces)
            ]
            if not extrusions:
                self.logger.warning(f"Space {space.GlobalId} has no footprint and was not patched.")
                continue

            representation = self.builder.get_representation(body.ContextOfItems, extrusions, "SweptSolid")
            representations = list(space.Representation.Representations)
            representations[representations.index(body)] = representation
            space.Representation.Representations = representations
            ifcopenshell.api.geometry.remove_representation(self.file, representation=body)

        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.Precision:
                context.Precision = 10

    def get_storey_elevation(self, space: ifcopenshell.entity_instance) -> Union[float, None]:
        """Get the absolute Z of the storey the space belongs to, in SI units"""
        storey = ifcopenshell.util.element.get_aggregate(space) or ifcopenshell.util.element.get_container(space)
        if storey is None or not storey.ObjectPlacement:
            return None
        return ifcopenshell.util.placement.get_local_placement(storey.ObjectPlacement)[2][3] * self.unit_scale

    def get_footprints(self, vertices: npt.NDArray[np.float64], faces: npt.NDArray[np.int32]) -> list[shapely.Polygon]:
        """Flatten every downwards facing triangle into a set of 2D footprints

        Unioning the downwards facing triangles (as opposed to only taking the
        faces sitting at the bottom of the space) means that spaces which are
        stepped or clipped from below still yield their full footprint, and
        that any columns poking through the space become voids in that
        footprint.
        """
        v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
        v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
        normals = np.cross(v1, v2)
        lengths = np.linalg.norm(normals, axis=1)
        # Degenerate triangles have no meaningful normal to test against.
        is_downwards = np.zeros(len(faces), dtype=bool)
        is_valid = lengths > self.tolerance
        is_downwards[is_valid] = (normals[is_valid, 2] / lengths[is_valid]) < -0.01

        polygons = []
        for face in faces[is_downwards]:
            polygon = shapely.Polygon(vertices[face][:, :2])
            if polygon.is_valid and polygon.area:
                polygons.append(polygon)

        footprint = shapely.ops.unary_union(polygons)
        footprints = footprint.geoms if footprint.geom_type == "MultiPolygon" else [footprint]
        return [orient(f.simplify(self.tolerance)) for f in footprints if f.geom_type == "Polygon" and not f.is_empty]

    def create_extrusion(self, footprint: shapely.Polygon, base_z: float, depth: float) -> ifcopenshell.entity_instance:
        outer_curve = self.create_curve(footprint.exterior)
        inner_curves = [self.create_curve(interior) for interior in footprint.interiors]
        profile = self.builder.profile(outer_curve, inner_curves=inner_curves)
        return self.builder.extrude(
            profile,
            magnitude=self.convert_si_to_unit(depth),
            position=(0.0, 0.0, self.convert_si_to_unit(base_z)),
        )

    def create_curve(self, ring: shapely.LinearRing) -> ifcopenshell.entity_instance:
        # Shapely repeats the first point to close the ring, IFC does not.
        points = np.array(ring.coords[:-1])
        return self.builder.polyline(self.convert_si_to_unit(points), closed=True)

    def convert_si_to_unit(self, value: T) -> T:
        return value / self.unit_scale
